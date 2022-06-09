import logging

from discord.commands import slash_command
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", description="Learn how to use this bot")
    async def _help(self, ctx):
        """Sends help message """
        await ctx.send(f"[Invite dotabot to a new server](f{self.bot.invite_link})")


def setup(bot):
    bot.add_cog(Help(bot))
