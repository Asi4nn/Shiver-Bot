from apscheduler.triggers.cron import CronTrigger
from discord import Embed, Color, utils
from discord.ext.commands import Cog, Context
from discord.ext.commands import command
from discord.ext.commands import has_permissions

from re import fullmatch
from datetime import datetime

from discord.utils import get

from lib.bot import PREFIX
from lib.db import bot_queries, USE_DB


class Birthday(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        # Daily birthday checker at noon est
        if USE_DB:
            self.bot.scheduler.add_job(self.birthday_trigger, CronTrigger(second="0", minute="0", hour="12"))
            self.bot.scheduler.start()

        print("Birthday cog ready")

    async def announce_birthday(self, guild, channel, mention, age):
        send_channel = get(self.bot.get_guild(guild).text_channels, id=channel)
        await send_channel.send(f":birthday: @here Happy Birthday to {mention} who's turning {age} today!")

    async def birthday_trigger(self):
        bdays = bot_queries.get_birthdays()

        for record in bdays:
            if int(record[2][0:2]) == datetime.today().day and int(record[2][3:5]) == datetime.today().month:
                channel = self.bot.get_announcement_channel(record[1])
                if channel is None:
                    general = get(self.bot.get_guild(record[1]).text_channels, name="general")
                    await general.send(f"Please set a announcement channel with {PREFIX}channel to use the birthday "
                                       "announcement feature")
                    break
                age = datetime.today().year - int(record[2][6:])
                await self.announce_birthday(record[1], channel, f'<@!{record[0]}>', age)

    @command(name="birthday", aliases=["bday"], brief="Saves your birthday info and adds notification on that date, "
                                                      "date must be in the form DD/MM/YYYY")
    async def birthday(self, ctx: Context, date):
        date = date.strip()
        if self.validate_birthday(ctx.author.mention, date):
            if bot_queries.set_birthday(ctx.author.id, ctx.guild.id, date):
                return await ctx.reply(f"Added birthdate {date} for {ctx.author.mention}")
            await ctx.reply(f"Failed to add birthday for {ctx.author.mention}")
        else:
            await ctx.reply(f"Invalid format! (Use DD/MM/YYYY like a human)")

    @command(name="birthday_set", aliases=["bday_set"], brief="Saves birthday info for the given user, "
                                                              "date must be in the form DD/MM/YYYY")
    @has_permissions(manage_roles=True)
    async def birthday_set(self, ctx: Context, mention, date):
        mention = mention.strip()
        date = date.strip()
        if self.validate_birthday(mention, date) and ctx.guild.get_member(int(mention[3:len(mention) - 1])) is not None:
            if bot_queries.set_birthday(int(mention[3:len(mention) - 1]), ctx.guild.id, date):
                return await ctx.reply(f"Added birthdate {date} for {mention}")
            await ctx.reply(f"Failed to add birthday for {mention}")
        else:
            await ctx.reply(f"Invalid format! (Use DD/MM/YYYY like a human)")

    @command(name="birthday_check", aliases=["bday_check"],
             brief="Checks birth date for the given user")
    async def birthday_check(self, ctx, mention):
        mention = mention.strip()
        record = bot_queries.get_birthday_record(int(mention[3:len(mention) - 1]), ctx.guild.id)
        if record is None:
            await ctx.reply("This this user has no recorded birth date")
        else:
            date = record[2].split("/")
            date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]))
            await ctx.reply(f"{mention}'s birth date is on {date.strftime('%B %d, %Y')}")

    @command(name="birthday_all", aliases=["bday_all"], brief="Lists all recorded birthdays in the server")
    async def birthday_all(self, ctx):
        await ctx.reply("Fetching birthdays...")

        bdays = bot_queries.get_guild_birthdays(ctx.guild.id)

        embed = Embed(title=":birthday: Birthdays", description=f"List of bdays for {ctx.guild.name}", colour=Color.blue())

        # Sort by date
        def date_key(record):
            record_date = [int(i) for i in record[2].split("/")]
            return datetime(day=record_date[0], month=record_date[1], year=record_date[2]).timestamp()

        bdays = sorted(bdays, key=date_key)

        for bday in bdays:
            date = bday[2].split("/")
            date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]))
            embed.add_field(name=utils.get(ctx.guild.members, id=bday[0]),
                            value=date.strftime('%B %d, %Y'),
                            inline=False)

        await ctx.reply(embed=embed)

    @staticmethod
    def validate_birthday(mention, date):
        if (fullmatch(r"<@(!|)\d{18}>", mention) is not None and fullmatch(r"\d\d/\d\d/\d\d\d\d", date) is not None
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
