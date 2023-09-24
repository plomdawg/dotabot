from discord.commands import slash_command
from discord import Embed
from discord.ext import commands

command_list = """
`/quiz` - *Play the Shopkeeper's quiz*
`/gold` - *Check your gold balance*
`/top` - *List the top gold balances*
`[exact quote]` - *Play a voiceline*
`dota [partial quote]` - *Play a voiceline*
`dota [partial quote] [n]` - *Play voiceline n out of many*
`hero [hero]` - *Play a hero's voiceline*
`list [command]` - *List results for a command*
`list [n] [command]` - *List starting at an index*
"""


example_list = """
`Ho ho.` - *Plays "Ho ho. (Lifestealer)"*
`Ha ha. 10` - *Plays "Ha ha. (Invoker) (10 out of 17)"*
`dota banana` - *Plays "That's the biggest banana slug I've ever seen."*
`random Techies` - *Play a random Techies voice line*
`list hero Techies` - *List all Techies voice lines*
`list dota haha` - *List all voicelines containing "haha"*
"""


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", description="Learn how to use this bot")
    async def _help(self, ctx):
        """Sends help message """
        embed = Embed()
        embed.add_field(name="Commands", value=command_list, inline=False)
        embed.add_field(name="Examples", value=example_list, inline=False)
        #embed.add_field(
        #    name="Invite", value=f"[Invite dotabot to a new server]({self.bot.invite_link})")
        embed.color = 0xFF0000
        await ctx.respond(content="", embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
