from typing import Optional
from datetime import datetime
from pytz import timezone
from pytz import utc

from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from discord import Member
from discord.colour import Colour
from discord.ext.commands import Context

est = timezone("US/Eastern")
utc = utc


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Info cog ready")

    @command(name="userinfo", aliases=['ui', 'whois'], brief="Gets info about a user in the server")
    async def user_info(self, ctx: Context, target: Optional[Member]):
        target = target or ctx.author

        embed = Embed(
            title=f"{target.name}#{target.discriminator}",
            description=target.mention,
            colour=target.colour,
            timestamp=datetime.now().astimezone(est)
        )
        embed.set_thumbnail(url=target.avatar_url)

        # Discord API doesn't return their datetimes with a timezone for some reason,
        # even though they are in UTC by default
        joined = target.joined_at
        created = target.created_at
        joined = utc.localize(joined)
        created = utc.localize(created)

        fields = [
            ("ID", target.id, False),
            ("Roles", ', '.join([role.mention for role in target.roles if str(role) != "@everyone"]), True),
            ("Highest role", target.top_role.mention, False),
            ("Join date", joined.astimezone(est).strftime("%d/%m/%Y, %H:%M:%S"), True),
            ("Account created", created.astimezone(est).strftime("%d/%m/%Y, %H:%M:%S"), True),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name="serverinfo", aliases=["guildinfo", "si", "gi"], brief="Gets info about the server")
    async def server_info(self, ctx: Context):
        target = ctx.guild

        embed = Embed(
            title=target.name,
            colour=Colour.from_rgb(255, 255, 0),
            timestamp=datetime.now().astimezone(est)
        )
        embed.set_thumbnail(url=target.icon_url)

        created = target.created_at
        created = utc.localize(created)

        fields = [
            ("ID", target.id, False),
            ("Roles", ', '.join([role.mention for role in target.roles if str(role) != "@everyone"]), True),
            ("Region", target.region, False),
            ("Created", created.astimezone(est).strftime("%d/%m/%Y, %H:%M:%S"), True),
            ("Total Members", target.member_count, True),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
