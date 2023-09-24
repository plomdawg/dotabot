import logging
import os
import random
import sys
import asyncio

import discord
from discord.commands.context import ApplicationContext

# Get secret tokens from environment variables.
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_SECRET_TOKEN = os.environ.get('DISCORD_SECRET_TOKEN')

# Make sure we got them.
if DISCORD_CLIENT_ID is None:
    print("ERROR: DISCORD_CLIENT_ID not set.")
    sys.exit(1)

if DISCORD_SECRET_TOKEN is None:
    print("ERROR: DISCORD_SECRET_TOKEN not set.")
    sys.exit(1)

# Set up discord module logging.
discord_logger = logging.getLogger('discord')

# Set up our logging.
if os.environ.get('VERBOSE_LOGGING') is not None:
    discord_logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
else:
    discord_logger.setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.DEBUG)


class DotaBot(discord.Bot):
    def __init__(self):
        # Call discord.Bot() init function with a custom activity.
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="for /quiz")
        super().__init__(intents=discord.Intents.all(), activity=activity)

        # Expose Client ID to the cogs.
        self.client_id = DISCORD_CLIENT_ID

        # Expose invite link to the cogs.
        # TODO: figure out permissions from https://discord.com/developers/applications/649351968623427640/bot
        permissions = "545447734385"
        self.invite_link = f"https://discord.com/api/oauth2/authorize?client_id={self.client_id}&permissions={permissions}&scope=bot%20applications.commands"

        # Load cogs.
        self.load_extension('cogs.help')
        self.load_extension('cogs.error_handler')
        self.load_extension('cogs.emojis')
        self.load_extension('cogs.database')
        self.load_extension('cogs.dota_wiki')
        self.load_extension('cogs.quiz')
        self.load_extension('cogs.voice_lines')

        @self.event
        async def on_ready():
            """ Called after the bot successfully connects to Discord servers """
            print(f"Connected as {self.user.display_name}")

            # Print guild info
            print(f"Active in {len(self.guilds)} servers:")
            user_count = 0
            for guild in self.guilds:
                try:
                    count = len(guild.members) - 1  # remove self from list
                    print(
                        f" - [{guild.id}] ({count} users) {guild.name} (Owner: {guild.owner.name}#{guild.owner.discriminator} {guild.owner.id})")
                    # add user count, exclude discord bot list
                    if guild.id != 264445053596991498:
                        user_count += count
                except AttributeError:
                    pass
            print(f"Total user reach: {user_count}")

            # Load emojis now that we're connected to discord servers.
            self.get_cog('Emojis').load_emojis()

            # Load the quiz now that the emojis are loaded.
            self.get_cog('ShopkeeperQuiz').load_words()

        @self.event
        async def on_guild_join(guild):
            # Try to find the #general channel to send first message.
            channel = discord.utils.get(guild.text_channels, name="general")
            # Fall back to the first text channel if there's no #general.
            if len(guild.text_channels) > 0 and channel is None:
                channel = guild.text_channels[0]
            await channel.send('Hello! You can send either a full quote with exact punctuation ("Haha!") or a partial quote prefixed by "dota" ("dota haha")')
            await channel.send('Support server: https://discord.gg/Czj2g9c')
            
        @self.event
        async def on_voice_state_update(member, before, after):
          # Leave if nobody is in the channel with the bot.
          vc = discord.utils.get(self.voice_clients, guild=member.guild)
          if vc and vc.channel:
              if not any([not user.bot for user in vc.channel.members]):
                  await vc.disconnect()
          

    async def send_embed(self, channel, color=None, footer=None, footer_icon=None, subtitle=None,
                         subtext=None, text=None, title=None, thumbnail=None):
        """ Sends a message to a channel, and returns the discord.Message of the sent message.

        If the text is over 2048 characters, subtitle and subtext fields are ignored and the
        message is split up into chunks. The first message will have the title and thumbnail,
        and only the last message will have the footer. 

        Returns a list of messages sent.
        """
        MAX_MSG_LENGTH = 2048

        # Use a random color if none was given
        if color is None:
            color = random.randint(0, 0xFFFFFF)

        # If the text is short enough to fit into one message,
        # create and send a single embed.
        if text is None or len(text) <= MAX_MSG_LENGTH:
            embed = discord.Embed(color=color)
            if footer is not None:
                if footer_icon is None:
                    embed.set_footer(text=footer)
                else:
                    embed.set_footer(text=footer, icon_url=footer_icon)
            if subtitle is not None or subtext is not None:
                embed.add_field(name=subtitle, value=subtext, inline=True)
            if thumbnail is not None:
                embed.set_thumbnail(url=thumbnail)
            if title is not None:
                embed.title = title
            if text is not None:
                embed.description = text

            # If this is a ctx, use respond() so the command succeeds and doesn't
            # print "This interaction failed" to the user.
            if type(channel) == ApplicationContext:
                response = await channel.respond(embed=embed)
                return

            # Send the single message
            return await channel.send(embed=embed)

        # If the text is too long, it must be broken into chunks.
        message_index = 0
        lines = text.split("\n")
        while lines:
            # Construct the text of this message
            text = ""
            while True:
                if not lines:
                    break
                line = lines.pop(0) + '\n'

                # next line fits in this message, add it
                if len(text) + len(line) < MAX_MSG_LENGTH:
                    text += line

                # one line is longer than max length of message, split the line and put the rest back
                elif len(line) > MAX_MSG_LENGTH:
                    cutoff = MAX_MSG_LENGTH - len(text)
                    next_line = line[:cutoff]
                    remainder = line[cutoff:-1]
                    text += next_line
                    lines.insert(0, remainder)
                # message is full - send it
                else:
                    lines.insert(0, line)
                    break

            embed = discord.Embed(color=color, description=text)

            # First message in chain - add the title and thumbnail
            if message_index == 0:
                if title is not None:
                    embed.title = title
                if thumbnail is not None:
                    embed.set_thumbnail(url=thumbnail)
                if subtitle is not None or subtext is not None:
                    embed.add_field(name=subtitle, value=subtext, inline=True)
                response = await channel.send(embed=embed)

            # Last message in chain - add the footer.
            if not lines:
                if footer is not None:
                    if footer_icon is not None:
                        embed.set_footer(text=footer, icon_url=footer_icon)
                    else:
                        embed.set_footer(text=footer)

            # If this is a ctx, use respond() so the command succeeds and doesn't
            # print "This interaction failed" to the user.
            if type(channel) == ApplicationContext:
                response = await channel.respond(embed=embed)
            else:
                response = await channel.send(embed=embed)

            message_index = message_index + 1

        # Return the last message sent so reactions can be easily added
        return response

    async def add_reactions(self, message, emojis):
        """ Adds a list of reactions to a message, ignoring NotFound errors """
        try:
            for emoji in emojis:
                await message.add_reaction(emoji)
        except discord.errors.NotFound:
            pass

    async def delete_message(self, message):
        """ Deletes a message, ignoring NotFound errors """
        if message is not None:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass


def main():
    # Create the bot.
    bot = DotaBot()
    # Print the invite link.
    print(f"Invite link: {bot.invite_link}")
    # Run the bot.
    bot.run(DISCORD_SECRET_TOKEN)


if __name__ == '__main__':
    main()
