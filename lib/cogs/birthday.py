from discord.ext.commands import Cog, Context
from discord.ext.commands import command
from discord.ext.commands import has_permissions

from re import fullmatch
from datetime import datetime

from lib.db import bot_queries

from ..bot import PREFIX


class Birthday(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Birthday cog ready")

    @command(name="birthday", aliases=["bday"], brief="Saves your birthday info and adds notification on that date, "
                                                      "date must be in the form DD/MM/YYYY")
    async def birthday(self, ctx: Context, date):
        date = date.strip()
        if self.validate_birthday(ctx.author.mention, date):
            if bot_queries.set_birthday(ctx.author.id, ctx.guild.id, date):
                return await ctx.send(f"Added birthdate {date} for {ctx.author.mention}")
            await ctx.send(f"Failed to add birthday for {ctx.author.mention}")
        else:
            await ctx.send(f"Invalid format! (Type {PREFIX}help for syntax)")

    @command(name="set_birthday", aliases=["set_bday"], brief="Saves birthday info for the given user, "
                                                              "date must be in the form DD/MM/YYYY")
    @has_permissions(manage_roles=True)
    async def set_birthday(self, ctx: Context, mention, date):
        mention = mention.strip()
        date = date.strip()
        if self.validate_birthday(mention, date) and ctx.guild.get_member(int(mention[3:len(mention) - 1])) is not None:
            if bot_queries.set_birthday(int(mention[3:len(mention) - 1]), ctx.guild.id, date):
                return await ctx.send(f"Added birthdate {date} for {mention}")
            await ctx.send(f"Failed to add birthday for {mention}")
        else:
            await ctx.send(f"Invalid format! (Type {PREFIX}help for syntax)")

    @command(name="birthday_check", aliases=["bdaycheck", "bday_check"],
             brief="Checks birth date for the given user")
    async def birthday_check(self, ctx, mention):
        mention = mention.strip()
        record = bot_queries.get_birthday_record(int(mention[3:len(mention) - 1]), ctx.guild.id)
        if record is None:
            await ctx.send("This this user has no recorded birth date")
        else:
            date = record[2].split("/")
            date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]))
            await ctx.send(f"{mention}'s birth date is on {date.strftime('%B %d, %Y')}")

    @staticmethod
    def validate_birthday(mention, date):
        if (fullmatch(r"<@!\d{18}>", mention) is not None and fullmatch(r"\d\d/\d\d/\d\d\d\d", date) is not None
                and int(date[6:]) <= datetime.today().year):
            try:
                datetime(day=int(date[0:2]), month=int(date[3:5]), year=int(date[6:]))
            except ValueError:
                pass
            else:
                return True
        return False


def setup(bot):
    bot.add_cog(Birthday(bot))
