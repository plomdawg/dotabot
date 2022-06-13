import asyncio
import random
import sqlite3

import discord
from discord.ext import commands


class VoiceLines(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.play_lock = False

        self.dota_wiki = self.bot.get_cog('DotaWiki')

        # Set up the sqlite database.
        self.connection = sqlite3.connect("responses.sqlite")
        self.cursor = self.connection.cursor()

        # Generate the table if needed.
        fields = ("name", "responses_url", "url", "text", "thumbnail")
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS responses ({' TEXT, '.join(fields)} TEXT)")

        # Populate the responses table.
        for hero in self.dota_wiki.data['heroes']:
            name = hero['_name']
            responses_url = f"{hero['url']}/Responses"
            print(f"Adding {len(hero['responses'])} responses for hero {name}")

            query = f"INSERT or IGNORE INTO responses ({','.join(fields)}) VALUES (?,?,?,?,?)"

            self.cursor.executemany(
                query, ([name, responses_url, response['url'], response['text'], hero['thumbnail']] for response in hero['responses']))

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore empty messages and self messages.
        if message.content == "" or message.author == self.bot.user:
            return

        # Only respond to users in a voice channel
        try:
            if message.author.voice.channel is None:
                return
        except AttributeError:
            return

        # Construct the response.
        response = None

        # Count total number of possible responses for given query.
        num_responses = 0

        # Disconnect command
        if message.content == "dotabot leave":
            vc = discord.utils.get(self.bot.voice_clients, guild=message.guild)
            if vc:
                await vc.disconnect(force=True)
                return

        # Random command
        if message.content.startswith("random"):
            query = message.content.split(' ', 1)[1].title()
            print(f"Getting random response for hero: {query}")
            # Find a random response
            self.cursor.execute(
                f'SELECT * FROM responses WHERE name = "{query}"')
            responses = self.cursor.fetchall()
            if responses:
                index = random.randint(0, len(responses) - 1)
                num_responses = len(responses)
                response = responses[index]

        # dota command
        elif message.content.startswith("dota") or message.content.startswith("any"):
            # If last token is a number, select that index from the results.
            try:
                index = int(message.content.split(' ')[-1]) - 1
                query = message.content[:-(len(str(index))+1)
                                        ].split(' ', 1)[1].title()
            except:
                query = message.content.split(' ', 1)[1].title()
                index = None

            print(f"Getting any response containing: {query} (index: {index})")
            self.cursor.execute(
                f'SELECT * FROM responses WHERE text LIKE "%{query}%"')
            responses = self.cursor.fetchall()
            num_responses = len(responses)
            if num_responses > 0:
                if index is None:
                    index = random.randint(0, len(responses) - 1)
                response = responses[index]

        else:
            response, index, num_responses = self.get_response(message.content)

        if response:
            # Reply in the same channel as the message.
            channel = message.channel
            bot_message = None

            # Hard-coded redirection to music channel.
            # todo: copy plombot
            if message.channel.id == 555565606649200641 or message.channel.id == 619389333899706388 or message.channel.id == 670084705210597386:
                channel = self.bot.get_channel(int(408481491597787136))

                # Delete the message and mention the music channel if it doesn't match
                if message.author != self.bot.user:
                    await self.bot.delete_message(message)
                    bot_message = await message.channel.send(f'{message.author.mention} {channel.mention}')

            # Play the voice line.
            await self.respond(message.author.voice.channel, channel, response, num_responses, index)

            # Also delete the bot's message after 30 seconds
            if bot_message is not None:
                await asyncio.sleep(30)
                await self.bot.delete_message(bot_message)

    async def respond(self, voice_channel, text_channel, response, n, index):
        name, responses, url, text, thumbnail = response
        await self.bot.send_embed(channel=text_channel,
                                  text=f"[{text} ({name})]({responses})",
                                  thumbnail=thumbnail,
                                  footer=f"voice line {index+1} out of {n}")
        await self.play_response(voice_channel, url)

    def get_response(self, text, name=None):
        text = text.replace('…', '...')
        print(f"Looking up '{text}' (name: {name})")
        if name:
            self.cursor.execute(
                f'SELECT * FROM responses WHERE text = "{text}" AND name = "{name}"')
        else:
            self.cursor.execute(
                f'SELECT * FROM responses WHERE text = "{text}"')
        responses = self.cursor.fetchall()
        if responses:
            index = random.randint(0, len(responses))
            return responses[index], index, len(responses)
        else:
            return None, 0, 0

    async def play_response(self, channel, url):
        """ Plays an mp3 from a URL in a voice channel """
        # Connect to the voice channel
        await self.Connect(channel)

        # Set up ffmpeg stream at 17% volume
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

    async def Connect(self, voice_channel):
        """ Connects to a voice channel. Returns the voice channel or None if error """
        print("Connecting to voice channel:", voice_channel)
        try:
            self.vc = await voice_channel.connect()
            while not self.vc.is_connected():
                print("waiting to connect")
            print("Successfully connected to:")
            print(self.vc.channel.name)
        except discord.errors.ClientException:
            print("Already connected")
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
    bot.add_cog(VoiceLines(bot))
