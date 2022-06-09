""" Error handler that PMs me with any unhandled errors """
import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.plom = self.bot.get_user(163040232701296641)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ Triggered if a command raises an error.
        Args:
            ctx   : commands.Context
            error : Exception
        """
        print("Error:", error)

        # Ignore unknown command errors
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.errors.Forbidden):
                permissions = ctx.channel.permissions_for(ctx.me)
                if not permissions.send_messages:
                    await ctx.author.send(f"Hey! I need permission to **send messages** to channel {ctx.channel}.")
                elif not permissions.embed_links:
                    await ctx.send(f"{ctx.author.mention} I need permission to **embed links** in this channel.")
                elif not permissions.add_reactions:
                    await ctx.send(f"{ctx.author.mention} I need permission to **add reactions** in this channel.")
                elif not permissions.manage_messages:
                    await ctx.send(f"{ctx.author.mention} I need permission to **manage messages** in this channel.")
                else:
                    # Unhandled error - Send me a message about it
                    await self.plom.send(f"Command ;{ctx.command} failed in server [{ctx.guild.name}]! {error} 1")
                    await print(ctx, error)
            else:
                await self.plom.send(f"Command ;{ctx.command} failed in server [{ctx.guild.name}]! {error} 2")
                await print(ctx, error)
        else:
            await self.plom.send(f"Command ;{ctx.command} failed in server [{ctx.guild.name}]! {error} 3")
            await print(ctx, error)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
