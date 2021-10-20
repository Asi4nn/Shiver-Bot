import discord
from discord.ext.commands import Cog, command, Context
import youtube_dl

QUEUE = []


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Music cog ready")

    @command(name="join", brief="Makes the bot join your voice channel if applicable")
    async def join(self, ctx: Context):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")

        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

    @command(name="leave", aliases=["disconnect", "fuckoff"],
             brief="Makes the bot join your voice channel if applicable")
    async def disconnect(self, ctx: Context):
        await ctx.voice_client.disconnect()

    @command(name="play", aliases=["p"], brief="Plays a song from a YouTube url (pls don't sue me youtube)")
    async def play(self, ctx: Context, url: str):
        if ctx.voice_client:
            ctx.voice_client.stop()
        else:
            await self.join(ctx)
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': "FFmpegExtractAudio",
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)

    @command(name="pause", brief="Pauses the music if applicable")
    async def pause(self, ctx: Context):
        await ctx.voice_client.pause()
        await ctx.send("Paused")

    @command(name="resume", brief="Resumes the music if applicable")
    async def resume(self, ctx: Context):
        await ctx.voice_client.pause()
        await ctx.send("Resumed")


def setup(bot):
    bot.add_cog(Music(bot))
