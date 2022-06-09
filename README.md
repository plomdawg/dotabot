# dotabot

dotabot is a Discord bot running in Heroku with some DotA 2 commands.

[Invite to a server](https://discordapp.com/oauth2/authorize?client_id=649351968623427640&scope=bot&permissions=1110453312)

## Running the bot locally

1. Get the Discord Client ID and secret token from the [Discord Developer Portal](https://discord.com/developers/applications/).

1. Rename `secrets.sh.example` to `secrets.sh` and insert your secret tokens.

1. Run the bot.
    ```bash
    source secrets.sh
    python bot/dotabot.py
    ```

## Updating dota wiki data

When a new patch hits, use the scraper script to generate `dota_wiki.yml`.

```bash
cd bot
python ./dota_wiki.py
```
