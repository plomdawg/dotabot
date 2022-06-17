""" Shopkeeper Quiz """
import asyncio
import random
import time

import discord
from discord.commands import slash_command
from discord.ext import commands
from matplotlib.image import thumbnail
from pyrsistent import T

# Pictures used for the embedded messages.
SHOPKEEPER_IMAGE = "https://i.imgur.com/Xyf1VjQ.png"
UNKNOWN_IMAGE = "https://static.wikia.nocookie.net/dota2_gamepedia/images/5/5d/Unknown_Unit_icon.png/revision/latest/scale-to-width-down/128?cb=20170416184928"


def strip_punctuation(text):
    """ Remove quotes and dashes from the text. """
    return text.replace("'", "").replace("-", " ")


def scramble(word) -> str:
    """ Randomly scrambles a word """
    char_list = list(word)
    random.shuffle(char_list)
    scrambled = ''.join(char_list)
    # Try again if the word isn't scrambled.
    if word in scrambled:
        return scramble(word)
    return scrambled


class Word:
    def __init__(self, text, category, image, url, hint=None) -> None:
        self.text = text
        self.category = category
        self.image = image
        self.url = url
        self.hint = hint

    @property
    def scrambled(self) -> str:
        """ Returns the scrambled text """
        return scramble(strip_punctuation(self.text).upper())

    @property
    def easy_scrambled(self) -> str:
        """ Returns the scrambled text, with spaces in place """
        scrambled = ""
        for word in strip_punctuation(self.text).split(" "):
            scrambled += scramble(word) + " "
        # Remove trailing space and capitalize.
        return scrambled[:-1].upper()

    def check(self, word) -> bool:
        """ Returns True if text matches the word, ignoring case and punctuation. """
        return strip_punctuation(word.lower()) == strip_punctuation(self.text.lower())


class Quiz:
    def __init__(self, bot, words, channel) -> None:
        self.bot = bot
        self.in_progress = False
        self.round_time = 23  # seconds
        self.max_gold = 20  # total possible gold for an answer.
        self.current_word = None
        self.channel = channel  # discord text channel.
        self.guesses = {}  # current guesses for a round.

        # Create a copy of the word list so we can pop() from it.
        self.words = words.copy()

    def next_word(self):
        """ Gets the next word from the word list. """
        index = random.randrange(len(self.words))
        word = self.words.pop(index)
        self.current_word = word
        return word

    def add_score(self, elapsed_time, user):
        """ Calculates and adds to a user's score. """
        # More points for fast guesses.
        score = int(self.max_gold - (elapsed_time *
                    self.max_gold / (self.round_time * 4)))
        # Add bonus points if more people guessed.
        score += (len(self.guesses.keys()) * 3) - 3
        try:
            self.scores[user] += score
            self.correct_answers[user] += 1
        except KeyError:
            self.scores[user] = score
            self.correct_answers[user] = 1
        return score

    async def start_phase(self, message, check, category=False, easy=False, hint=False):
        """ Start a phase by editing the message given. Returns the answer if solved. """
        # Manually create an embedded message.
        embed = discord.Embed()
        embed.set_thumbnail(url=SHOPKEEPER_IMAGE)
        embed.title = f"Shopkeeper's Quiz (round {self.round_number})"

        # Add the scrambled word.
        if easy:
            scrambled = self.current_word.easy_scrambled
        else:
            scrambled = self.current_word.scrambled
        description = f"**Unscramble:** {scrambled}"

        # Add the category.
        if category:
            description += f"\n**Category:** {self.current_word.category} "
            embed.set_footer(text="Here's a hint!")

        # Add the hint.
        if hint:
            description += f"\n**Hint:** {self.current_word.hint} "
            embed.set_footer(text="Here's another hint!")

        # Change the footer if it's easy scrambled.
        if easy:
            embed.set_footer(text="Spaces are in places!")

        # Edit the message for this round.
        embed.description = description
        await message.edit(embed=embed)

        # Wait for the answer.
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=self.round_time)
        except asyncio.TimeoutError:
            answer = None

        # Return the answer, or None.
        return answer, embed

    async def start_round(self):
        """ Start a round. """
        # Start the round timer (used to calculate score).
        start_time = time.perf_counter()

        # Send a message.
        text = f"Starting round **{self.round_number}**, sit tight!"
        message = await self.bot.send_embed(self.channel, text=text)

        # Grab the next word.
        self.next_word()

        # Keep track of guesses.
        self.guesses = {}

        # This is called for each response, returns True if the guess is correct
        def check(msg):
            # Make sure the message is from this server.
            if msg.channel.guild != self.channel.guild:
                return False

            # Keep track of guesses per user.
            try:
                self.guesses[msg.author].append(msg.content)
            except KeyError:
                self.guesses[msg.author] = [msg.content]

            return self.current_word.check(msg.content)

        # Begin phase 1: hard scramble.
        answer, embed = await self.start_phase(message, check)

        # Begin phase 2: hard scramble with a category.
        if answer is None:
            answer, embed = await self.start_phase(message, check, category=True)

        # Begin phase 3: easy scramble with the category.
        if answer is None:
            answer, embed = await self.start_phase(message, check, category=True, easy=True)

        # Begin phase 4 if we have a hint: easy scramble with a hint.
        if answer is None and self.current_word.hint is not None:
            answer, embed = await self.start_phase(message, check, category=True, easy=True, hint=True)

        #
        # Round is now over.
        #

        # Add the answer to the quiz message.
        embed.description += f"\n**Answer**: [{self.current_word.text}]({self.current_word.url})"

        # Add the image to the quiz message.
        if self.current_word.image is not None:
            embed.set_thumbnail(url=self.current_word.image)

        # Somebody answered!
        if answer:
            # Add a thumbs up to the correct answer.
            await answer.add_reaction("👍")

            # Increment user's score.
            elapsed_time = time.perf_counter() - start_time
            score = self.add_score(
                elapsed_time=elapsed_time, user=answer.author)

            # Add the user who guessed right to the footer of the quiz message.
            embed.set_footer(
                text=f"Answered by {answer.author.display_name} for {score} gold.")

        # Game over if nobody answered.
        if answer is None:
            # Send a thumbs down on the quiz message.
            await message.add_reaction("👎")

            # Set the footer.
            embed.set_footer(
                text="Nobody answered in time! Game over.")

            # End the quiz.
            self.in_progress = False

        # Edit the message.
        await message.edit(embed=embed)

    async def start(self):
        """ Start the quiz. """
        # Quiz is now in progress.
        self.in_progress = True

        # Reset scores and correct answers for this quiz.
        self.scores = {}
        self.correct_answers = {}

        # Keep starting rounds until the quiz is over.
        self.round_number = 1
        while self.in_progress:
            await self.start_round()
            self.round_number += 1

        # End the quiz.
        await self.end()

    async def end(self):
        """ Handles a game over. """
        # Find the top score.
        try:
            top_score = max(self.scores.values())
        except ValueError:
            top_score = 0
            return

        # Find the winners and losers. There may be more than one winner if tied.
        winners = []
        losers = []
        for user, score in self.scores.items():
            if score == top_score:
                winners.append(user)
            else:
                losers.append(user)
            # Increment user's gold amounts in the database.
            self.bot.database.user_add_gold(user, score)

        # If there are no winners, everybody lost!
        if len(winners) == 0:
            text = "Everybody lost!"

        # Single winner.
        elif len(winners) == 1:
            text = "Winner: **{}** earned **{}** gold with {} answers!\n".format(
                winners[0].display_name,
                top_score,
                self.correct_answers[winners[0]]
            )

        # Multiple winners!
        else:
            text = f"It's a tie! The following players earned **{top_score}** gold:\n"
            for winner in winners:
                text += " -- {}\n".format(winner)

        # Add the scores for everyone else.
        if len(losers) > 0:
            text += "Losers:\n"
            for user in losers:
                text += " -- {} got {} correct (**{}** gold)\n".format(
                    user.display_name,
                    self.correct_answers[user],
                    self.scores[user]
                )

        # Send the game over message.
        message = await self.bot.send_embed(
            channel=self.channel,
            title="Shopkeeper's Quiz Results",
            text=text,
            thumbnail=SHOPKEEPER_IMAGE,
            footer=f"To play again, press NEW or type /quiz"
        )
        await message.add_reaction("🆕")


def load_words(data) -> list:
    words = []

    # Add the heroes and abilities.
    for hero in data['heroes']:
        # Heroes do not have a hint.
        words.append(
            Word(
                text=hero['_name'],
                category="Heroes",
                image=hero['thumbnail'],
                url=hero['url']
            )
        )
        for ability in hero['abilities']:
            # Use the lore as the hint.
            words.append(
                Word(
                    text=ability['name'],
                    category="Abilities",
                    hint=ability['lore'],
                    image=ability['thumbnail'],
                    url=ability['url']
                )
            )

    # Add the items.
    for item in data['items']:
        # Use the lore as the hint.
        words.append(
            Word(
                text=item['_name'],
                category="Items",
                hint=item['lore'],
                image=item['thumbnail'],
                url=item['url']
            )
        )

    print(f"Loaded {len(words)} words.")

    return words


class ShopkeeperQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quizzes = {}  # key = guild, value = quiz

        # Load other cogs.
        self.database = self.bot.get_cog('Database')
        self.dota_wiki = self.bot.get_cog('DotaWiki')

        # Load the words and hints.
        self.words = load_words(self.dota_wiki.data)

    @ commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore own reactions
        if user == self.bot.user:
            return

        # Ignore messages not sent by the bot
        if reaction.message.author != self.bot.user:
            return

        # NEW quiz
        if reaction.emoji in "🆕":
            """ Remove own reaction and start quiz """
            try:
                await reaction.remove(self.bot.user)
            except discord.errors.NotFound:
                pass
            asyncio.ensure_future(
                self.shopkeeper_quiz(
                    bot=self.bot,
                    channel=reaction.message.channel
                ))
        else:
            # Unknown emoji, do nothing
            return

        # Remove the reaction once the job is done
        try:
            await reaction.remove(user)
        except discord.errors.NotFound:
            pass

    async def shopkeeper_quiz(self, bot, channel):
        # Try to find existing quiz.
        quiz = self.quizzes.get(channel.guild)

        # Don't start a new quiz if there's already a quiz happening.
        if quiz is not None and quiz.in_progress:
            await bot.send_embed(channel, text="A quiz is in progress!", color=0xFF0000)
            return

        # Initialize Quiz.
        self.quizzes[channel.guild] = Quiz(
            bot=bot, words=self.words, channel=channel)

        # Begin the quiz.
        asyncio.ensure_future(self.quizzes[channel.guild].start())

    @ slash_command(name="quiz", description="Play the Shopkeeper's quiz")
    async def quiz(self, ctx):
        await self.bot.send_embed(channel=ctx, text="Starting the quiz!")
        await self.shopkeeper_quiz(channel=ctx.channel, bot=ctx.bot)


def setup(bot):
    print("Loading Shopkeeper Quiz cog")
    bot.add_cog(ShopkeeperQuiz(bot))
    print("Loaded Shopkeeper Quiz cog")
