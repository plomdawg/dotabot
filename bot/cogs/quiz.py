""" Shopkeeper Quiz """
import asyncio
import random
import time

import discord
from discord.commands import slash_command
from discord.ext import commands


def scramble(word) -> str:
    """ Randomly scrambles a word """
    char_list = list(word)
    random.shuffle(char_list)
    return ''.join(char_list)


class Word:
    def __init__(self, text, category, image, hint=None) -> None:
        self.text = text
        self.category = category
        self.image = image
        self.hint = hint

        # Remove quotes and dashes from the text.
        self.clean_text = self.text.replace("'", "").replace("-", " ")

    @property
    def scrambled(self) -> str:
        """ Returns the scrambled text """
        return scramble(self.clean_text.upper())

    @property
    def easy_scrambled(self) -> str:
        """ Returns the scrambled text, with spaces in place """
        scrambled = ""
        for word in self.clean_text.split(" "):
            scrambled += scramble(word) + " "
        return scrambled[:-1].upper()  # remove trailing space


def load_words(data) -> list:
    words = []

    # Add the heroes and abilities.
    for hero in data['heroes']:
        # Heroes do not have a hint.
        words.append(
            Word(
                text=hero['_name'],
                category="Heroes",
                image=hero['thumbnail']
            )
        )
        for ability in hero['abilities']:
            # Use the lore as the hint.
            words.append(
                Word(
                    text=ability['name'],
                    category="Abilities",
                    hint=ability['lore'],
                    image=ability['thumbnail']
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
                image=item['thumbnail']
            )
        )

    print(f"Loaded {len(words)} words.")

    return words


class ShopkeeperQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quiz_in_progress = {}  # key = guild.id, value = Bool

        # Load other cogs.
        self.database = self.bot.get_cog('Database')
        self.dota_wiki = self.bot.get_cog('DotaWiki')

        # Load the words and hints.
        self.words = load_words(self.dota_wiki.data)

    def in_progress(self, guild):
        """ Returns True if a quiz is currently in progress """
        return self.quiz_in_progress.get(guild.id, False)

    def get_next_word(self, avoidlist):
        """ Gets the next word, avoiding words in the avoidlist. """
        word = random.choice(self.words)

        # Keep trying if the word is in the avoidlist.
        while word in avoidlist:
            word = random.choice(self.words)

        return word

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
                    channel=reaction.message.channel,
                    guild=reaction.message.guild
                ))
        else:
            # Unknown emoji, do nothing
            return

        # Remove the reaction once the job is done
        try:
            await reaction.remove(user)
        except discord.errors.NotFound:
            pass

    async def shopkeeper_quiz(self, bot, channel, guild, game_state=None, respond=False):
        # Initialize Game State.
        if game_state is None:
            # scores contains users' scores (key is user.id)
            # correct_answers contains users' number of correct answers (key is user.id)
            # words contains the index of words we have seen before to avoid duplicates in the same quiz
            game_state = dict(round=1, scores={}, correct_answers={}, words=[])

        # Don't start a new quiz if there's already a quiz happening.
        if game_state['round'] == 1 and self.in_progress(guild):
            if respond:
                await channel.respond("A quiz is in progress!")
            else:
                await channel.send("A quiz is in progress!")
            return

        # Begin the quiz.
        self.quiz_in_progress[guild.id] = True
        game_over = False

        # Grab the next word that we haven't seen yet.
        word = self.get_next_word(avoidlist=game_state['words'])

        # Keep track of the words we have seen.
        game_state['words'].append(word)

        # Total possible gold for this answer.
        max_gold = 20

        # Each round has three phases that last 30 seconds each.
        # If all 3 phases end without a correct answer, the game is over.
        round_time = 23

        # Keep track of how many people are guessing.
        guesses = {}

        # Called for each response, returns True if the guess is correct
        def check(msg):
            # Make sure the message is from this server.
            if msg.channel.guild != channel.guild:
                return False

            # Convert the guess to lower case.
            guess = msg.content.lower().replace("'", "").replace("-", " ").strip()

            # Keep track of guesses per user.
            try:
                guesses[msg.author].append(guess)
            except KeyError:
                guesses[msg.author] = [guess]

            return guess == word.text.lower()

        # Phase 1: hard scramble
        embed = discord.Embed()
        embed.title = f"Shopkeeper's Quiz (round {game_state['round']})"
        embed.description = f"**Unscramble:** {word.scrambled}"
        if respond:
            quiz_message = await channel.respond(embed=embed)
            quiz_message = await quiz_message.original_message()
        else:
            quiz_message = await channel.send(embed=embed)
        start_time = time.perf_counter()

        try:
            # Wait another 30 seconds after sending the message
            correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))

        except asyncio.TimeoutError:
            # Phase 2: another hard scramble + category hint
            embed.description = f"**Unscramble:** {word.scrambled}\n**Category:** {word.category} "
            embed.set_footer(text="Here's a hint!")
            await quiz_message.edit(embed=embed)

            try:
                # Wait another 30 seconds after hint was given
                correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))
            except asyncio.TimeoutError:
                # Phase 3: easy scramble + category hint
                embed.description = f"**Unscramble:** {word.easy_scrambled}\n**Category:** {word.category}"
                embed.set_footer(text="Here's another hint!")
                await quiz_message.edit(embed=embed)
                try:
                    # Wait another 30 seconds after the last hint is given
                    correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))
                except asyncio.TimeoutError:
                    # Phase 4: easy scramble + category hint + lore hint
                    if word.hint is not None:
                        embed.description = f"**Unscramble:** {word.easy_scrambled}\n**Category:** {word.category}\n**Hint:** {word.hint}"
                        embed.set_footer(text="Here's some lore!")
                        await quiz_message.edit(embed=embed)
                        try:
                            # Wait another 30 seconds after the last hint is given
                            correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))

                        except asyncio.TimeoutError:
                            # Timed out, nobody answered - stop the quiz
                            game_over = True

                    else:
                        # Timed out, nobody answered - stop the quiz
                        game_over = True

        if game_over:
            await quiz_message.add_reaction("👎")
            embed.description += "\n**Answer**: {}".format(word.text)
            if word.image is not None:
                embed.set_thumbnail(url=word.image)
            embed.set_footer(
                text="Nobody answered in time! Game over.")
            try:
                await quiz_message.edit(embed=embed)
            except discord.errors.NotFound:
                pass

            # Find the winner(s)
            try:
                top_score = max(game_state['scores'].values())
            except ValueError:
                top_score = 0
            winners = [self.bot.get_user(
                k) for k, v in game_state['scores'].items() if v == top_score]
            if len(winners) == 0:
                text = "Everybody lost!"
            elif len(winners) == 1:
                correct = game_state['correct_answers'][winners[0].id]
                text = "Winner: **{}** earned **{}** gold with {} answers!\n".format(
                    winners[0].display_name, top_score, correct)
            else:
                text = "It's a tie! The following players earned **{}** gold:\n".format(
                    (top_score))
                for winner in winners:
                    text += " -- {}\n".format(winner)

            # Find the loser(s)
            losers = [self.bot.get_user(
                k) for k, v in game_state['scores'].items() if v != top_score]
            if len(losers) > 0:
                text += "Losers:\n"
                for user in losers:
                    correct = game_state['correct_answers'][user.id]
                    gold = game_state['scores'][user.id]
                    text += " -- {} got {} correct (**{}** gold)\n".format(
                        user.display_name, correct, gold)

            winner_embed = discord.Embed()
            winner_embed.description = text
            winner_embed.title = "Shopkeeper's Quiz Results"
            winner_embed.set_thumbnail(
                url="https://i.imgur.com/Xyf1VjQ.png")
            winner_embed.set_footer(
                text=f"To play again, press NEW or type /quiz")
            winner_message = await channel.send(embed=winner_embed)
            await winner_message.add_reaction("🆕")

            # Increment user's gold amounts
            for user in winners + losers:
                gold = game_state['scores'][user.id]
                self.database.user_add_gold(user, gold)

            game_state['round'] = 1
            game_state['scores'] = dict()
            self.quiz_in_progress[guild.id] = False
            return

        # Calculate score.
        elasped_time = time.perf_counter() - start_time
        score = int(max_gold - (elasped_time * max_gold / (round_time * 4)))

        # Add bonus points if more people guessed.
        print(guesses)
        print(score)
        score += (len(guesses.keys()) * 3) - 3
        print(score)

        # Increment user's score in the game state
        user = correct_msg.author
        try:
            game_state['scores'][user.id] += score
            game_state['correct_answers'][user.id] += 1
        except KeyError:
            game_state['scores'][user.id] = score
            game_state['correct_answers'][user.id] = 1

        await correct_msg.add_reaction("👍")
        embed.description += f"\n**Answer**: {word.text}"
        if word.image is not None:
            embed.set_thumbnail(url=word.image)
        embed.set_footer(
            text=f"Answered by {user.display_name} for {score} gold.")
        await quiz_message.edit(embed=embed)

        # Continue the quiz!
        game_state['round'] += 1
        asyncio.ensure_future(self.shopkeeper_quiz(
            channel=channel, bot=bot, guild=guild, game_state=game_state))

    @ slash_command(name="quiz", description="Play the Shopkeeper's quiz")
    async def quiz(self, ctx):
        await self.shopkeeper_quiz(channel=ctx, bot=ctx.bot, guild=ctx.guild, respond=True)


def setup(bot):
    print("Loading Shopkeeper Quiz cog")
    bot.add_cog(ShopkeeperQuiz(bot))
    print("Loaded Shopkeeper Quiz cog")
