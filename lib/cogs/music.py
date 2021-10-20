import asyncio
from typing import Optional, Dict

import discord
import youtube_dl
from discord.ext.commands import Cog, command, Context, guild_only, check

from ..helpers.video import Video

QUEUE = []
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


class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None

    def is_requester(self, user):
        return self.now_playing.requested_by == user


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states: Dict[GuildState] = {}

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
        await ctx.send("", embed=state.now_playing.get_embed())

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
            message = [f"  **NOW PLAYING**: **{np.title}** (requested by **{np.requested_by.name}**)",
                       f"{len(queue)} songs in queue:"]
            message += [
                f"  {index + 1}. **{song.title}** (requested by **{song.requested_by.name}**)"
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

    @command(name="remove", aliases=["r"], brief="Remove the song at the given")
    @guild_only()
    @check(audio_playing)
    @check(in_voice_channel)
    async def remove(self, ctx: Context, index: str):
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
             brief="Makes the bot join your voice channel if applicable")
    @guild_only()
    async def leave(self, ctx: Context):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            state.playlist = []
            state.now_playing = None

    @command(name="play", aliases=["p"], brief="Plays a song from a YouTube url (pls don't sue me)")
    @guild_only()
    async def play(self, ctx: Context, *, url: Optional[str]):
        vc: discord.VoiceClient = ctx.guild.voice_client
        state = self.get_state(ctx.guild)

        if vc is not None and vc.is_paused() and not url:   # resumes play if no url param
            vc.resume()
            await ctx.send("Resumed")
            return

        if vc is not None and vc.channel:
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                print(f"Error downloading video: {e}")
                await ctx.send("There was an error downloading your video")
                return
            state.playlist.append(video)
            await ctx.send("Added to queue.", embed=video.get_embed())
        else:
            if ctx.author is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    await ctx.send("There was an error downloading your video")
                    return
                client = await channel.connect()
                self._play_song(client, state, video)
                await ctx.send("", embed=video.get_embed())
            else:
                await ctx.send("You need to be in a voice channel to do that")

    def _play_song(self, client, state, song):
        state.now_playing = song
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, **FFMPEG_OPTIONS), volume=state.volume)

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)

        client.play(source, after=after_playing)

    @command(name="clearqueue", aliases=["cq"], brief="Clears the song queue")
    @guild_only()
    @check(audio_playing)
    async def clearqueue(self, ctx: Context):
        state = self.get_state(ctx.guild)
        state.playlist = []

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
            await ctx.send("Music bot is currently paused!")


def setup(bot):
    bot.add_cog(Music(bot))
