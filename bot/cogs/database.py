import sqlite3

import discord
from discord.ext import commands
from discord.commands import slash_command


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = sqlite3.connect("database.sqlite")
        self.cursor = self.database.cursor()
        user_fields = ("id INT",
                       "name TEXT",
                       "gold INT",
                       )
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS users ({','.join(user_fields)})")
        self.emojis = self.bot.get_cog('Emojis')

    def add_user(self, user):
        """ Adds a new user to the database """
        query = "SELECT * from users WHERE id = ?"
        values = (user.id,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if not result:
            query = "INSERT or IGNORE INTO users (id, name, gold) VALUES (?,?,?)"
            values = (user.id, user.display_name, 0)
            print(query, values)
            self.cursor.execute(query, values)
            self.database.commit()

    def user_add_gold(self, user, gold):
        """ Adds gold to a user's account """
        self.add_user(user)
        query = f"UPDATE users SET gold = gold + ? WHERE id = ?"
        values = (gold, user.id)
        print(query, values)
        self.cursor.execute(query, values)
        self.database.commit()

    def user_get_gold(self, user):
        """ Returns the balance of a user """
        query = f"SELECT gold FROM users WHERE id = ?"
        values = (user.id,)
        self.cursor.execute(query, values)
        gold = self.cursor.fetchone()
        return 0 if gold is None else gold[0]

    @slash_command(name="top", description="List users with the most gold.")
    async def top(self, ctx):
        """ Sends a list of the users with the most gold """
        query = f"SELECT * FROM users ORDER BY gold DESC LIMIT 10"
        self.cursor.execute(query)
        users = self.cursor.fetchall()
        gold_icon = self.emojis.emojis.get('Gold', '*gold*')
        text = ""
        for i, user in enumerate(users):
            text += f"{i+1}. **{user[1]}** {user[2]} {gold_icon}" + "\n"
        embed = discord.Embed(title="Top Users")
        embed.set_thumbnail(
            url="https://api.opendota.com/apps/dota2/images/abilities/alchemist_goblins_greed_md.png")
        embed.description = text
        await ctx.respond(embed=embed)

    @slash_command(name="gold", description="Check your current gold balance.")
    async def gold(self, ctx):
        """ Sends the user's current gold balance """
        gold = self.user_get_gold(ctx.author)
        gold_icon = self.emojis.emojis.get('Gold', '*gold*')
        await ctx.respond(f"{ctx.author.mention}, you have **{gold}** {gold_icon}")


def setup(bot):
    print("Loading Database cog")
    bot.add_cog(Database(bot))
    print("Loaded Database cog")
