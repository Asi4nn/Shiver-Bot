import youtube_dl as ytdl
import discord
import time

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist",
    'postprocessors': [{
        'key': "FFmpegExtractAudio",
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
}


class Video:
    """Class containing information about a particular video."""

    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            video = self._get_info(url_or_search)
            video_format = video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video[
                "thumbnail"] if "thumbnail" in video else None
            self.requested_by = requested_by
            self.duration = video["duration"]

    def _get_info(self, video_url):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, description=self.uploader, url=self.video_url, colour=discord.Colour.blue())
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar_url)

        duration = time.gmtime(self.duration)
        if duration.tm_hour == 0:
            formatted_time = time.strftime("%M Minutes, %S Seconds", duration)
        else:
            formatted_time = time.strftime("%H Hours %M Minutes, %S Seconds", duration)
        embed.add_field(name="Duration", value=formatted_time, inline=True)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed

    @staticmethod
    def format_duration(duration: int):
        """This assumes less than a day duration"""
        duration = time.gmtime(duration)
        if duration.tm_hour == 0:
            return time.strftime("%M Minutes, %S Seconds", duration)
        else:
            return time.strftime("%H Hours %M Minutes, %S Seconds", duration)
