import asyncio
from typing import Optional, Dict

import discord
import youtube_dl
from discord.ext.commands import Cog, command, Context, guild_only, check
from ..bot import PREFIX

from ..helpers.video import Video, QueryManager

QUEUE = []
LEAVE_DELAY = 60    # in seconds
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

'''Many ideas taken from: https://github.com/joek13/py-music-bot/blob/master/musicbot/cogs/music.py'''


async def audio_playing(ctx):
    """Checks that audio is currently playing before continuing."""
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        await ctx.send("Not currently playing any audio")


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        await ctx.send("You need to be in the channel to do that")
        return False


class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None
        self.looping = False

    def is_requester(self, user):
        return self.now_playing.requested_by == user


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states: Dict[GuildState] = {}

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Auto leave after a delay and all members have left the channel"""
        vc = member.guild.voice_client
        if not vc:  # if not connected do nothing
            return

        if not member.bot:
            # check members after a member has left the bots channel
            if before and before.channel and before.channel.id == vc.channel.id and not [m for m in before.channel.members if not m.bot]:
                await self.check_and_disconnect(member, before.channel, vc)
        elif member.id == self.bot.user.id and after.channel is not None:   # check channel if bot has been moved
            if not [m for m in after.channel.members if not m.bot]:
                await self.check_and_disconnect(member, after.channel, vc)

    async def check_and_disconnect(self, member, channel, vc):
        state = self.get_state(member.guild)
        await asyncio.sleep(LEAVE_DELAY)    # delay
        if not [m for m in channel.members if not m.bot]:   # check again
            await vc.disconnect()
            state.playlist = []
            state.now_playing = None

    def get_state(self, guild) -> GuildState:
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @Cog.listener()
    async def on_ready(self):
        print("Music cog ready")

    @command(aliases=["np"], brief="Checks the song currently playing, if applicable")
    @guild_only()
    @check(audio_playing)
    async def nowplaying(self, ctx):
        """Displays information about the current song."""
        state = self.get_state(ctx.guild)
        if state.now_playing:
            await ctx.send("", embed=state.now_playing.get_embed())
        else:
            await ctx.send("Not currently playing")

    @command(name="queue", aliases=["q", "playlist"], brief="Displays the song queue")
    @guild_only()
    @check(audio_playing)
    async def queue(self, ctx):
        """Display the current play queue."""
        state = self.get_state(ctx.guild)
        await ctx.send(self._queue_text(state.playlist, ctx))

    def _queue_text(self, queue, ctx):
        """Returns a block of text describing a given song queue."""
        np = self.get_state(ctx.guild).now_playing
        if len(queue) > 0 or np is not None:
            message = [f"  **NOW PLAYING**: **{np.title}** Duration: **{Video.format_duration(np.duration)}** (requested by **{np.requested_by.name}**)",
                       f"{len(queue)} songs in queue:"]
            message += [
                f"  {index + 1}. **{song.title}** Duration: **{Video.format_duration(song.duration)}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "The play queue is empty."

    @command(name="skip", aliases=["s"], brief="Skips the current song")
    @guild_only()
    @check(audio_playing)
    @check(in_voice_channel)
    async def skip(self, ctx):
        client = ctx.guild.voice_client
        client.stop()
        await ctx.send("Skipping")

    @command(name="remove", aliases=["r"], brief="Remove the song at the given queue index")
    @guild_only()
    @check(audio_playing)
    @check(in_voice_channel)
    async def remove(self, ctx: Context, index: str):
        if not index.isdigit():
            await ctx.send("Invalid index")
            return

        playlist = self.get_state(ctx.guild).playlist
        if 1 <= int(index) <= len(playlist):
            song = playlist.pop(int(index) - 1)
            await ctx.send(f"Removing {index}. **{song.title}** request by **{song.requested_by}**")
        else:
            await ctx.send("Invalid index")

    @command(name="join", brief="Makes the bot join your voice channel if applicable")
    @guild_only()
    async def join(self, ctx: Context):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")

        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

    @command(name="leave", aliases=["disconnect", "dc", "fuckoff"],
             brief="Makes the bot leave your voice channel if applicable")
    @guild_only()
    async def leave(self, ctx: Context):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            await ctx.send(":wave: Bye!")
            state.playlist = []
            state.now_playing = None
            state.looping = False

    @command(name="play", aliases=["p"], brief="Plays a song from a YouTube url, or resumes playing if paused")
    @guild_only()
    async def play(self, ctx: Context, *, url: Optional[str]):
        vc: discord.VoiceClient = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if vc and vc.channel and not await in_voice_channel(ctx):
            return

        if vc and vc.is_paused() and not url:   # resumes play if no url param
            vc.resume()
            await ctx.send("Resumed")
            return

        if vc and vc.channel:
            try:
                new = await QueryManager.query_url(state.playlist, url, ctx.author, ctx)
            except youtube_dl.DownloadError as e:
                print(f"Error downloading video: {e}")
                await ctx.send("There was an error downloading your video")
                return
            except:
                await ctx.send("There was an error retrieving your video")
                return
            state.playlist = new
            if not vc.is_playing():
                self._play_song(vc.guild.voice_client, state, state.playlist.pop(0))
        else:
            if ctx.author is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    state.playlist = await QueryManager.query_url(state.playlist, url, ctx.author, ctx)
                except youtube_dl.DownloadError as e:
                    await ctx.send("There was an error downloading your video")
                    print(e)
                    return
                client = await channel.connect()
                self._play_song(client, state, state.playlist.pop(0))
            else:
                await ctx.send("You need to be in a voice channel to do that")

    def _play_song(self, client, state, song):
        state.now_playing = song
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, **FFMPEG_OPTIONS), volume=state.volume)

        def after_playing(err):
            if state.looping and state.now_playing:
                self._play_song(client, state, state.now_playing)
            else:
                state.now_playing = None

            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            # else:
            #     asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)  # changed to dc after all members leave channel

        client.play(source, after=after_playing)

    @command(name="clearqueue", aliases=["cq"], brief="Clears the song queue")
    @guild_only()
    @check(audio_playing)
    async def clearqueue(self, ctx: Context):
        state = self.get_state(ctx.guild)
        state.playlist = []
        await ctx.send("Cleared all songs in queue")

    @command(name="pause", brief="Pauses the music if applicable")
    @guild_only()
    @check(audio_playing)
    @check(in_voice_channel)
    async def pause(self, ctx: Context):
        vc = ctx.guild.voice_client
        if not vc.is_paused():
            vc.pause()
            await ctx.send("Paused")
        else:
            await ctx.send(f"Music bot is currently paused! (Type {PREFIX}play to resume)")

    @command(name="loop", aliases=["repeat"], brief="Loops the current song (if applicable")
    @guild_only()
    @check(in_voice_channel)
    async def loop(self, ctx: Context):
        state = self.get_state(ctx.guild)
        if state.looping:
            state.looping = False
            await ctx.send(":repeat: Stopped looping")
        else:
            state.looping = True
            await ctx.send(":repeat: Looping current song")


def setup(bot):
    bot.add_cog(Music(bot))
