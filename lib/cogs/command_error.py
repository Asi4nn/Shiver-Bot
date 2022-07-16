from discord import HTTPException, Forbidden
from discord.ext.commands import Cog, CommandNotFound, BadArgument, MissingRequiredArgument, MissingPermissions, \
    CheckFailure, CommandError
import re

from lib.bot import PREFIX


class CommandErrorHandler(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_command_error, "on_command_error")

    async def on_command_error(self, ctx, exc):
        if hasattr(ctx.command, "on_error"):
            return  # Don't interfere with custom error handlers

        if isinstance(exc, CommandNotFound):
            # Checks if command looks like currency (matches numbers and periods)
            if not re.match(r'^\$[0-9.]*$', ctx.message.content.split(' ', 1)[0]):
                return await ctx.reply(f"Command not found, type {PREFIX}help for a list of commands")
        elif isinstance(exc, BadArgument):
            return await ctx.reply(f"Bad argument, type {PREFIX}help for a list of commands")
        elif isinstance(exc, MissingRequiredArgument):
            return await ctx.reply("Argument(s) are missing from command")
        elif isinstance(exc, HTTPException):
            return await ctx.reply("Unable to send message (likely too long)")
        elif isinstance(exc, Forbidden):
            return await ctx.reply("I don't have permission to do that")
        elif isinstance(exc, MissingPermissions):
            return await ctx.reply("You don't have permission to do that")
        elif isinstance(exc, CheckFailure):
            return await ctx.reply("Failed to check permissions (internal error, try again)")
        elif isinstance(exc, CommandError):
            return await ctx.reply(str(exc))

        await ctx.reply("Unexpected error while running that command (check logs)")
        raise exc


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
