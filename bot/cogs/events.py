import logging

from aiohttp import ClientResponseError
from discord import Colour, Embed, Member, Object
from discord.ext.commands import (
    BadArgument, Bot, BotMissingPermissions,
    CommandError, CommandInvokeError, CommandNotFound,
    Context, NoPrivateMessage, UserInputError
)

from bot.cogs.modlog import ModLog
from bot.constants import (
    Channels, Colours, DEBUG_MODE,
    Guild, Icons, Keys,
    Roles, URLs
)
from bot.utils import chunks

log = logging.getLogger(__name__)

RESTORE_ROLES = (str(Roles.muted), str(Roles.announcements))


class Events:
    """No commands, just event handlers."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_command_error(self, ctx: Context, e: CommandError):
        command = ctx.command
        parent = None

        if command is not None:
            parent = command.parent

        if parent and command:
            help_command = (self.bot.get_command("help"), parent.name, command.name)
        elif command:
            help_command = (self.bot.get_command("help"), command.name)
        else:
            help_command = (self.bot.get_command("help"),)

        if hasattr(command, "on_error"):
            log.debug(f"Command {command} has a local error handler, ignoring.")
            return

        if isinstance(e, CommandNotFound) and not hasattr(ctx, "invoked_from_error_handler"):
            tags_get_command = self.bot.get_command("tags get")
            ctx.invoked_from_error_handler = True

            # Return to not raise the exception
            return await ctx.invoke(tags_get_command, tag_name=ctx.invoked_with)
        elif isinstance(e, BadArgument):
            await ctx.send(f"Bad argument: {e}\n")
            await ctx.invoke(*help_command)
        elif isinstance(e, UserInputError):
            await ctx.invoke(*help_command)
        elif isinstance(e, NoPrivateMessage):
            await ctx.send("Sorry, this command can't be used in a private message!")
        elif isinstance(e, BotMissingPermissions):
            await ctx.send(
                f"Sorry, it looks like I don't have the permissions I need to do that.\n\n"
                f"Here's what I'm missing: **{e.missing_perms}**"
            )
        elif isinstance(e, CommandInvokeError):
            if isinstance(e.original, ClientResponseError):
                if e.original.code == 404:
                    await ctx.send("There does not seem to be anything matching your query.")
                else:
                    await ctx.send("BEEP BEEP UNKNOWN API ERROR!=?!??!?!?!?")

            else:
                await ctx.send(
                    f"Sorry, an unexpected error occurred. Please let us know!\n\n```{e}```"
                )
                raise e.original
        raise e

def setup(bot):
    bot.add_cog(Events(bot))
    log.info("Cog loaded: Events")
