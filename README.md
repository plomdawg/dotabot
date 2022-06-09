# dotabot

[Invite to a server](https://discordapp.com/oauth2/authorize?client_id=649351968623427640&scope=bot&permissions=1110453312)

dotabot is a Discord bot running in Heroku that plays hero responses when typed in chat.

![image](https://user-images.githubusercontent.com/6510862/172931649-3ea306e2-2787-4225-9797-295d5aaca392.png)

It also features the Shopkeeper's Quiz `/quiz`

![image](https://user-images.githubusercontent.com/6510862/172955073-6d0a00af-bb11-4899-80f7-87478426f516.png)

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

```console
avalon@homer:~/dotabot/bot$ python dota_wiki.py 
Loading: https://dota2.fandom.com/wiki/Items
Loading: https://dota2.fandom.com/wiki/Template:Lore_nav/heroes
Loading: https://dota2.fandom.com/wiki/Abaddon/Responses
Loading: https://dota2.fandom.com/wiki/Abaddon
Abaddon has 315 responses and 4 abilities.
Loading: https://dota2.fandom.com/wiki/Alchemist/Responses
Loading: https://dota2.fandom.com/wiki/Alchemist
Alchemist has 387 responses and 7 abilities.
...
```
