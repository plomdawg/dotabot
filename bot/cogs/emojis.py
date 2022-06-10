""" Emojis """
import discord
from discord.commands import slash_command
from discord.ext import commands
import os

# DotA Heroes servers
SERVERS = [650182236490170369, 650182259248463907, 650180306782912533]


# Checks
async def author_is_plomdawg(ctx):
    """ Returns True if the author is plomdawg """
    return ctx.author.id == 163040232701296641


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Call bot.get_cog('Emojis').load_emojis() in the on_ready function to populate this
        self.emojis = {}

    def get(self, emoji_name):
        """ Get an emoji """
        return self.emojis.get(emoji_name, "")

    async def load_emojis(self):
        """ Loads all emojis from the 3 servers above """
        for guild_id in SERVERS:
            guild = self.bot.get_guild(guild_id)
            for emoji in guild.emojis:
                self.emojis[emoji.name] = str(emoji)
        print("loaded emojis:", self.emojis)

    # @commands.check(author_is_plomdawg)
    # @slash_command(name="setup", description="Play the Shopkeeper's quiz")
    # async def setup_emojis(self, ctx):
    #    """ Uploads all the hero icons onto 3 different servers (50 max each) """
    #    icon_dir = 'assets\\icons'
    #    icons = os.listdir(icon_dir)
    #
    #    for chunk, server in zip(chunks(icons, 50), SERVERS):
    #        guild = discord.utils.get(self.bot.guilds, id=server)
    #        for icon in chunk:
    #            path = os.path.join(icon_dir, icon)
    #            name = icon.replace('.png', '').replace(
    #                '-', '').replace('_', '').replace("'", '')
    #            print(
    #                f"({server}) [{guild.name}] uploading {path} as '{name}'")
    #            with open(path, 'rb') as f:
    #                await guild.create_custom_emoji(name=name, image=f.read())
    #
    # @commands.command()
    # @commands.check(author_is_plomdawg)
    # async def list_emojis(self, ctx):
    #    """ Prints all available emojis """
    #    for chunk in chunks(self.emojis, 60):
    #        text = ""
    #        for emoji in chunk:
    #            text += str(emoji)
    #        print("emoji:", text)
    #        await ctx.send(text)


def setup(bot):
    print("Loading Emojis cog")
    bot.add_cog(Emojis(bot))
    print("Loaded Emojis cog")
