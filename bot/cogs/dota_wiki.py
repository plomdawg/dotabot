import time

import json
from discord.ext import commands


class DotaWiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
        # Load and parse the json file into the table.
        json_file = "dota_wiki.json"
        start_time = time.time()
        with open(json_file, "r") as f:
            print(f"Loading json data from {json_file}")
            self.data = json.load(f)
            elapsed = time.time() - start_time
            print(f"Loaded json data in {elapsed} seconds")

def setup(bot):
    bot.add_cog(DotaWiki(bot))
