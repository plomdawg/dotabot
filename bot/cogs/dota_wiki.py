import time

import yaml
from discord.ext import commands


class DotaWiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load and parse the yaml file into the table.
        yaml_file = "dota_wiki.yml"
        start_time = time.time()
        with open(yaml_file, "r") as f:
            print(f"Loading yaml data from {yaml_file}")
            self.data = yaml.safe_load(f)
            end = time.time()
            elapsed = time.time() - start_time
            print(f"Loaded yaml data in {elapsed} seconds")


def setup(bot):
    bot.add_cog(DotaWiki(bot))
