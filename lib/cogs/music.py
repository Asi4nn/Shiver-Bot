import asyncio
import discord
from discord.ext.commands import Cog, command, Context, CommandError, guild_only, check
import youtube_dl
from ..helpers.video import Video

QUEUE = []
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'default_search': "ytsearch",
    'postprocessors': [{
        'key': "FFmpegExtractAudio",
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    "extract_flat": "in_playlist"
}

'''Many ideas taken from: https://github.com/joek13/py-music-bot/blob/master/musicbot/cogs/music.py'''


async def audio_playing(ctx):
    """Checks that audio is currently playing before continuing."""
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise CommandError("Not currently playing any audio.")


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise CommandError("You need to be in the channel to do that.")


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    def get_state(self, guild):
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
        message = await ctx.send("", embed=state.now_playing.get_embed())

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

    @command(name="leave", aliases=["disconnect", "fuckoff", "dc"],
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
    async def play(self, ctx: Context, *, url: str):
        vc: discord.VoiceClient = ctx.guild.voice_client
        state = self.get_state(ctx.guild)

        if vc is not None and vc.is_paused() and not url:   # resumes play if no url param
            vc.resume()
            return

        if vc is not None and vc.channel:
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                print(f"Error downloading video: {e}")
                await ctx.send(
                    "There was an error downloading your video, sorry")
                return
            state.playlist.append(video)
            await ctx.send("Added to queue.", embed=video.get_embed())
        else:
            if ctx.author is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    await ctx.send(
                        "There was an error downloading your video, sorry")
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
                asyncio.run_coroutine_threadsafe(client.disconnect(),
                                                 self.bot.loop)

        client.play(source, after=after_playing)

    @command(name="pause", brief="Pauses the music if applicable")
    @guild_only()
    async def pause(self, ctx: Context):
        if not ctx.voice_client.is_paused():
            await ctx.voice_client.pause()
            await ctx.send("Paused")
        else:
            await ctx.send("Music bot is currently paused!")


class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None

    def is_requester(self, user):
        return self.now_playing.requested_by == user


def setup(bot):
    bot.add_cog(Music(bot))
