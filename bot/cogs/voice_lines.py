import asyncio
import random
import sqlite3

import discord
from discord.ext import commands


def get_index_from_query(text):
    """ Splits off the last token in the string if it's a number.
        Example: "dota haha 2" -> ("dota haha", 2)
    """
    try:
        tokens = text.split(' ')
        index = int(tokens[-1]) - 1
        text = ' '.join(tokens[:-1])
    except:
        index = None
    return text, index


def user_in_voice_channel(user):
    """ Returns True if the user is in a voice channel. """
    try:
        if user.voice.channel is not None:
            return True
    except AttributeError:
        return False
    return False


class VoiceLines(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.play_lock = False

        self.dota_wiki = self.bot.get_cog('DotaWiki')

        self.db_connection = sqlite3.connect("responses.sqlite")
        self.db_cursor = self.db_connection.cursor()
        self.create_database()

        @self.bot.event
        async def on_message(message):
            """ For every message, we want to do a few things:
                - Check if it's an exact match for a response
                    - If so, play the response
                - Check if the message starts with "dota" (e.g. "dota haha")
                    - If so, play a random response from any hero that contains the text.
                - Check if the message starts with "hero" (e.g. "hero juggernaut")
                    - If so, play a random response from that hero.
                - Check if the message ends with a number (e.g. "dota haha 2")
                    - If so, play the nth response from the query.
            """
            # Ignore bot messages.
            if message.author.bot:
                return

            # Ignore messages if the author is not in a voice channel.
            if not user_in_voice_channel(message.author):
                return

            # Check if the message ends in a number.
            text, index = get_index_from_query(message.content)
            
            # Check if the message starts with "list" (e.g. "list hero juggernaut")
            # List mode: list all possible responses for the query without playing it.
            list_mode = False
            list_start = 0
            if text.lower().startswith("list "):
                list_mode = True
                text = text.split(' ', 1)[1]
                
                # Check if the text starts with a number. It can be a multidigit number.
                # if so, use it as the list start
                if text[0].isdigit() and " " in text:
                    list_start = int(text.split(' ', 1)[0]) - 1
                    text = text.split(' ', 1)[1]

            # Check if the message is an exact match for a response.
            responses, index = self.get_voice_responses(
                exact_text=text, index=index)
            if responses:
                return await self.respond(message, responses, index, list_mode, list_start)

            # Check if the message starts with "dota" (e.g. "dota haha")
            if text.lower().startswith("dota ") or text.lower().startswith("any "):
                # Split off the prefix.
                text = text.split(' ', 1)[1]
                # Get a random response from any hero that contains the text.
                responses, index = self.get_voice_responses(
                    text=text, index=index)
                if responses:
                    return await self.respond(message, responses, index, list_mode, list_start)

            elif text.lower().startswith("hero "):
                # Split off the prefix.
                hero_name = text.split(' ', 1)[1]
                # Get a random response from the given hero that contains the text.
                responses, index = self.get_voice_responses(
                    name=hero_name, index=index)
                if responses:
                    return await self.respond(message, responses, index, list_mode, list_start)

    def create_database(self):
        """ Creates the database and loads the json file into it. """
        # Generate the table if needed.
        fields = ("name", "voice_url", "url", "text", "thumbnail")
        self.db_cursor.execute(
            f"CREATE TABLE IF NOT EXISTS responses ({' TEXT, '.join(fields)} TEXT)")

        # Populate the responses table.
        for voice in self.dota_wiki.data['voices']:
            print(f"Adding {len(voice['responses'])} responses for {voice['name']}")

            query = f"INSERT or IGNORE INTO responses ({','.join(fields)}) VALUES (?,?,?,?,?)"

            self.db_cursor.executemany(
                query, ([voice['name'], voice['url'], response['url'], response['text'], voice['thumbnail']] for response in voice['responses']))

    async def respond(self, message, responses, index, list_mode=False, list_start=0, forward=True):
        text_channel = message.channel
        
        if list_mode:
            max_list_length = 16
            message = f"Found {len(responses)} responses."
            
            # Check if the requested start is out of bounds.
            if list_start >= len(responses):
                message = f"Start index **{list_start+1}** is greater than the number of responses ({len(responses)})."
                return await self.bot.send_embed(channel=text_channel, text=message)
            
            elif list_start < 0:
                message = f"Start index **{list_start+1}** is less than 1."
                return await self.bot.send_embed(channel=text_channel, text=message)
            
            # The list is longer than the max list length.
            if len(responses) > max_list_length:
                if list_start == 0:
                    message = f" Showing the first **{max_list_length}**."
                else:
                    message = f" Showing **{list_start+1}** to **{list_start+max_list_length}**."
                list_end = list_start + max_list_length
                responses = responses[list_start:list_end]

                message += "\nUse `list [n] [command]` to list starting at a different index."

            for i, response in enumerate(responses):
                name, response, url, text, thumbnail = response
                voice_line = f"\n{i+1+list_start}. [{text}]({response}) [({name})]({url})"
                print(voice_line)
                message += voice_line
            print(message)
            return await self.bot.send_embed(channel=text_channel, text=message)
        
        voice_channel = message.author.voice.channel
        name, response, url, text, thumbnail = responses[index]
        text = f"[{text} ({name})]({response})"
        footer = f"voice line {index+1} out of {len(responses)}"
        warning_message = None

        # If the message was sent in my-dudes server,
        # forward the command to the music channel and
        # let the user know the command is being forwarded.
        if forward and message.guild.id == 408172061723459584:
            music_channel = self.bot.get_channel(int(408481491597787136))
            if message.channel != music_channel:
                await message.delete()
                warning = f"{message.author.mention} wrong channel - forwaring to {music_channel.mention}"
                warning_message = await self.bot.send_embed(channel=text_channel, text=warning)
                text_channel = self.bot.get_channel(int(408481491597787136))

        # Respond to the message and play the voice response.
        await self.bot.send_embed(channel=text_channel, text=text, thumbnail=thumbnail, footer=footer)
        await self.play_response(voice_channel, url)

        # Delete our own message in 30 seconds.
        if warning_message is not None:
            await asyncio.sleep(30)
            await warning_message.delete()

    def get_voice_responses(self, exact_text=None, text=None, index=None, name=None):
        """ Find responses for the given query. """

        # Construct the database operation.
        if exact_text:
            # Match the exact response text.
            operation = f'SELECT * FROM responses WHERE text = "{exact_text}"'
        elif text:
            # Match any response containing the text.
            operation = f'SELECT * FROM responses WHERE text LIKE "%{text}%"'
            # Match the hero name if specified.
            if name:
                operation += f' AND name = "{name}"'
        else:
            operation = f'SELECT * FROM responses WHERE name = "{name}"'

        # Replace elipses with periods.
        operation = operation.replace('…', '...')

        # Fetch the results.
        responses = self.db_cursor.execute(operation).fetchall()

        # Use a random index if not specified.
        if index is None and responses:
            index = random.randint(0, len(responses) - 1)

        return responses, index

    async def play_response(self, channel, url):
        """ Connects to a voice channel and plays the mp3 in the url """
        # Connect to the voice channel
        await self.connect_to_voice_channel(channel)
        print(f"Playing {url} in {channel}")

        # Set up ffmpeg stream at 20% volume
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                source=url,
                options=f"-af loudnorm=I=-16.0:TP=-1.0"
            ),
            volume=0.2
        )

        # Begin playback and wait for it to finish
        try:
            self.vc.play(audio)
        except discord.errors.ClientException:
            # Already playing - wait then try again
            while self.vc and self.vc.is_playing():
                await asyncio.sleep(1)
            await self.play_response(channel, url)

        try:
            while self.vc and self.vc.is_playing():
                await asyncio.sleep(1)
        except AttributeError:
            pass

        # Player was stopped or paused
        if self.vc is None or self.vc.is_paused():
            self.play_lock = False
            return

    async def connect_to_voice_channel(self, voice_channel):
        """ Connects to a voice channel. Returns the voice channel or None if error """
        #print("Connecting to voice channel:", voice_channel)
        try:
            self.vc = await voice_channel.connect()
            while not self.vc.is_connected():
                print("waiting to connect")
            print("Successfully connected to:")
            print(self.vc.channel.name)
        except discord.errors.ClientException:
            #print("Already connected")
            pass
        except asyncio.TimeoutError:
            print("Timed out!")

        # Find the voice client for this server
        self.vc = discord.utils.get(
            self.bot.voice_clients, guild=voice_channel.guild)

        # Move to the user if nobody is in the room with the bot
        if self.vc is not None and len(self.vc.channel.members) == 1:
            print("Moving to", voice_channel)
            await self.vc.move_to(voice_channel)

        return self.vc


def setup(bot):
    print("Loading Dota cog")
    bot.add_cog(VoiceLines(bot))
    print("Done loading Dota cog")


def teardown(bot):
    for vc in bot.voice_clients:
        asyncio.ensure_future(vc.disconnect(force=True))
