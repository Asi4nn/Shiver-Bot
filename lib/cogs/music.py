import asyncio
from typing import Optional, Dict

import discord
import youtube_dl
from discord.ext.commands import Cog, command, Context, guild_only, check, CommandError
from ..bot import PREFIX

from ..helpers.video import Video, QueryManager

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
        raise CommandError("Not currently playing any audio")


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise CommandError("You need to be in the channel to do that")


class GuildMusicState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None
        self.looping = False
        self.idle = False

    def is_requester(self, user):
        return self.now_playing.requested_by == user


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states: Dict[GuildMusicState] = {}

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Auto leave after a delay and all members have left the channel"""
        client = member.guild.voice_client
        if not client:  # if not connected do nothing
            return

        if not member.bot:
            # check members after a member has left the bots channel
            if (before and before.channel and before.channel.id == client.channel.id
                    and not [m for m in before.channel.members if not m.bot]):
                await self.check_and_disconnect(member, before.channel, client)
        elif member.id == self.bot.user.id and after.channel is not None:   # check channel if bot has been moved
            if not [m for m in after.channel.members if not m.bot]:
                await self.check_and_disconnect(member, after.channel, client)

    async def check_and_disconnect(self, member, channel, vc):
        state = self.get_state(member.guild)
        await asyncio.sleep(LEAVE_DELAY)    # delay
        if await self.idle_loop(state) and not [m for m in channel.members if not m.bot]:   # check again
            await self.disconnect(state, vc)

    async def idle_loop(self, state) -> bool:
        """
        Idle loop for when the bot is in idle state, waiting to possible disconnect on its own
        :param state: Guild state
        :return: Whether or not the conditions to disconnect are met
        """

        idle_time = 0
        state.idle = True
        while state.idle:
            await asyncio.sleep(1)
            idle_time += 1
            if idle_time >= LEAVE_DELAY:
                return True
        return False

    async def disconnect(self, state, client):
        state.playlist = []
        state.now_playing = None
        state.looping = False
        state.idle = False
        await client.disconnect()

    def get_state(self, guild) -> GuildMusicState:
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildMusicState()
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
            await ctx.reply("", embed=state.now_playing.get_embed())
        else:
            await ctx.reply("Not currently playing")

    @command(name="queue", aliases=["q", "playlist"], brief="Displays the song queue")
    @guild_only()
    @check(audio_playing)
    async def queue(self, ctx):
        """Display the current play queue."""
        state = self.get_state(ctx.guild)
        await ctx.reply(self._queue_text(state.playlist, ctx))

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
        await ctx.reply("Skipping")

    @command(name="remove", aliases=["r"], brief="Remove the song at the given queue index")
    @guild_only()
    @check(audio_playing)
    @check(in_voice_channel)
    async def remove(self, ctx: Context, index: str):
        if not index.isdigit():
            await ctx.reply("Invalid index")
            return

        playlist = self.get_state(ctx.guild).playlist
        if 1 <= int(index) <= len(playlist):
            song = playlist.pop(int(index) - 1)
            await ctx.reply(f"Removing {index}. **{song.title}** request by **{song.requested_by}**")
        else:
            await ctx.reply("Invalid index")

    @command(name="join", brief="Makes the bot join your voice channel if applicable")
    @guild_only()
    async def join(self, ctx: Context):
        if ctx.author.voice is None:
            await ctx.reply("You're not in a voice channel!")

        channel = ctx.author.voice.channel
        client = ctx.voice_client
        if client is None:
            await channel.connect()
        else:
            await client.move_to(channel)
            if not client.is_playing():
                await self.idle_loop(self.get_state(ctx.guild))

    @command(name="leave", aliases=["disconnect", "dc", "fuckoff"],
             brief="Makes the bot leave your voice channel if applicable")
    @guild_only()
    async def leave(self, ctx: Context):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await ctx.reply(":wave: Bye!")
            await self.disconnect(state, client)

    @command(name="play", aliases=["p"], brief="Plays a song from a YouTube url, or resumes playing if paused")
    @guild_only()
    async def play(self, ctx: Context, *, url: Optional[str]):
        client: discord.VoiceClient = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        state.idle = False

        if client and client.channel and not await in_voice_channel(ctx):
            return

        if client and client.is_paused() and not url:   # resumes play if no url param
            client.resume()
            await ctx.reply("Resumed")
            return

        if client and client.channel:
            try:
                new = await QueryManager.query_url(state.playlist, url, ctx.author, ctx)
            except youtube_dl.DownloadError as e:
                print(f"Error downloading video: {e}")
                await ctx.reply("There was an error downloading your video")
                return
            except Exception as e:
                print(e)
                await ctx.reply("There was an error retrieving your video")
                return
            state.playlist = new
            if not client.is_playing():
                self._play_song(client.guild.voice_client, state, state.playlist.pop(0))
        else:
            if ctx.author is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    state.playlist = await QueryManager.query_url(state.playlist, url, ctx.author, ctx)
                except youtube_dl.DownloadError as e:
                    await ctx.reply("There was an error downloading your video")
                    print(e)
                    return
                client = await channel.connect()
                self._play_song(client, state, state.playlist.pop(0))
            else:
                await ctx.reply("You need to be in a voice channel to do that")

    def _play_song(self, client, state, song):
        state.now_playing = song
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, **FFMPEG_OPTIONS), volume=state.volume)

        async def after_playing_idle():
            if await self.idle_loop(state):
                await self.disconnect(state, client)

        def after_playing(err):
            if state.looping and state.now_playing:
                self._play_song(client, state, state.now_playing)
            else:
                state.now_playing = None

            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                # Disconnect after done playing
                asyncio.run_coroutine_threadsafe(after_playing_idle(), self.bot.loop)

        client.play(source, after=after_playing)

    @command(name="clearqueue", aliases=["cq"], brief="Clears the song queue")
    @guild_only()
    @check(audio_playing)
    async def clearqueue(self, ctx: Context):
        state = self.get_state(ctx.guild)
        state.playlist = []
        await ctx.reply("Cleared all songs in queue")

    @command(name="pause", brief="Pauses the music if applicable")
    @guild_only()
    @check(audio_playing)
    @check(in_voice_channel)
    async def pause(self, ctx: Context):
        vc = ctx.guild.voice_client
        if not vc.is_paused():
            vc.pause()
            await ctx.reply("Paused")
            self.get_state(ctx.guild).idle = True
        else:
            await ctx.reply(f"Music bot is currently paused! (Type {PREFIX}play to resume)")

    @command(name="loop", aliases=["repeat"], brief="Loops the current song (if applicable")
    @guild_only()
    @check(in_voice_channel)
    async def loop(self, ctx: Context):
        state = self.get_state(ctx.guild)
        if state.looping:
            state.looping = False
            await ctx.reply(":repeat: Stopped looping")
        else:
            state.looping = True
            await ctx.reply(":repeat: Looping current song")


def setup(bot):
    bot.add_cog(Music(bot))
