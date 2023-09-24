import requests
import yaml
import json
from bs4 import BeautifulSoup
import time
import sys

DOTA_WIKI_URL = "https://dota2.fandom.com"

# Fix yaml indenting (https://stackoverflow.com/a/39681672/12757998).


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(Dumper, self).increase_indent(flow, False)


def _load_page(url) -> BeautifulSoup:
    # Load the page into BeautifulSoup.
    print(f"Loading: {url}")
    page = requests.get(url)
    return BeautifulSoup(page.text, 'html.parser')


def get_abilities(hero) -> list:
    abilities = []

    # Dota wiki page that lists all abilities for a hero.
    page = _load_page(hero.url)

    # Find the ability elements on the page.
    for element in page.find_all(class_='ability-background'):

        # Extract the lore text.
        lore = element.find(class_="ability-lore")
        if lore is not None:
            lore = lore.text

        # Extract the thumbnail.
        thumbnail = element.find(class_='image').get('href')

        # Remove extra text from the div containing the ability name.
        element.find('div').find('div').find('div').decompose()

        # Remove extra spaces from the div containing the ability name.
        name = element.find('div').find('div').text.strip()
        ability = {
            'name': name,
            'lore': lore,
            'thumbnail': thumbnail,
            'url': f"{hero.url}#Abilities"
        }
        abilities.append(ability)

    return abilities


def get_responses(hero) -> list:
    """ Returns a list of Response objects for a Hero """
    responses = []

    # Dota wiki page that lists all responses for a hero.
    page = _load_page(f"{hero.url}/Responses")

    # Find the main content on the page.
    content = page.find(class_='mw-parser-output')

    # Skip pages that don't have content.
    # (like https://dota2.fandom.com/wiki/Crystal_Maiden/Dragon%27s_Blood/Responses)
    if content is not None:

        # Find all of the response elements on the page.
        for element in content.find_all('li'):
            audio_element = element.find('audio')

            # Ignore elements that don't contain an audio element.
            if audio_element is None:
                continue

            # Ignore elements that don't contain an audio link.
            audio_source = audio_element.find('source')
            if audio_source is None:
                continue
            voice_line_url = audio_source.get('src')

            # Remove italicized text.
            for elem in element.find_all('span'):
                elem.decompose()

            # Remove extra spaces from the element.
            voice_line_text = element.text.strip()

            # Add the response to the dict.
            # responses[voice_line_text] = voice_line_url
            response = {
                'text': voice_line_text,
                'url': voice_line_url
            }
            responses.append(response)

    # Return the responses.
    return responses


def get_thumbnail(hero) -> str:
    """ hard coding the thumbnails here """
    name = hero.name

    # Default
    url = "https://icon-library.net/images/dota-2-icon/dota-2-icon-28.jpg"

    # Voice packs - get the text inside parens
    if "(" in name:
        name = name.split('(')[1].split(')')[0]

    # Other Responses
    if name == "Warlock's Golem":
        url = "https://i.imgur.com/F49q2Gf.png"
    elif name == "Shopkeeper":
        url = "https://i.imgur.com/Xyf1VjQ.png"
    elif name == "Announcer":
        url = "https://i.imgur.com/B8pD7m2.png"

    # Announcer Packs
    elif name == "Gabe Newell":
        url = "https://i.imgur.com/a1tnZusr/bin/python3.8 -u /opt/dotabot/dotabot.pyAw.png"

    # Heroes
    elif name == "Skeleton King":
        url = "https://i.imgur.com/WEwzR0Z.png"
    else:
        hero = name.replace(' ', '_').replace('-', '').lower()
        url = f"https://api.opendota.com/apps/dota2/images/heroes/{hero}_full.png"

    return url


class Hero:
    def __init__(self, element) -> None:
        # Hero name (e.g. 'Techies')
        # Replace escape code with space.
        self.name = element.text.replace('\xa0', ' ')

        # Dota wiki URL (e.g. 'https://dota2.fandom.com/wiki/Techies')
        self.url = f"{DOTA_WIKI_URL}{element.get('href').replace('/Lore', '')}"

        # Thumbnail URL.
        self.thumbnail = get_thumbnail(self)

        # Load responses.
        self.responses = get_responses(self)

        # Load abilities.
        self.abilities = get_abilities(self)

        print(
            f"{self.name} has {len(self.responses)} responses and {len(self.abilities)} abilities.")

    def to_dict(self) -> dict:
        return {
            '_name': self.name,
            'url': self.url,
            'thumbnail': self.thumbnail,
            'abilities': self.abilities,
            'responses': self.responses
        }


def get_heroes() -> list:
    """ Returns a list of Hero objects for all current heroes. """
    heroes = []

    # Dota wiki page that lists all heroes.
    page = _load_page(f"{DOTA_WIKI_URL}/wiki/Template:Lore_nav/heroes")

    # Find the main content on the page.
    content = page.find(class_='notanavbox-list notanavbox-odd')

    # Find all of the hero elements on the page.
    for hero_element in content.find_all('a'):
        # Create hero object.
        hero = Hero(hero_element)

        # Ignore hero variants (like "Terrorblade (Dragon's Blood)")
        if "(" in hero.name:
            continue

        # Ignore Mazzie (unreleased hero)
        if "Mazzie" in hero.name:
            continue

        heroes.append(hero)

    return heroes


def get_items() -> list:
    """ Returns a list of Item objects for all current items. """
    items = []

    # Dota wiki page that lists all items.
    page = _load_page(f"{DOTA_WIKI_URL}/wiki/Items")

    # Find the main content on the page.
    content = page.find(class_='mw-parser-output')

    # Remove stuff we do not need.
    content.find(id='pageTabber').decompose()
    content.find(id='toc').decompose()
    content.find('p').decompose()

    # Find all item lists on the page.
    itemlist_elements = content.find_all(class_='itemlist')

    # Find all items in the lists.
    for itemlist in itemlist_elements:
        for element in itemlist.find_all('div'):
            # Grab the name from the list.
            name = element.find_all('a')[1].text

            # Check if the element has a gold cost.
            gold_cost = element.find('span')
            if gold_cost is not None:
                gold_cost = int(gold_cost.text.strip())

            # Extract the thumbnail and name from the element.
            img = element.find('img')
            thumbnail = img.get('data-src')
            if thumbnail is None:
                thumbnail = img.get('src')

            # Load the item page.
            url = f"{DOTA_WIKI_URL}{element.find('a')['href']}"
            page = _load_page(url)

            # Find the info box on the page.
            info_box = page.find(class_='infobox')

            # Load the lore text
            lore = info_box.find('td', attrs={'style': 'font-style:italic; padding:6px 10px;'})

            # Some items don't have lore.
            if lore:
              lore = lore.text.strip()
            else:
              lore = "No lore found."

            item = {
                '_name': name,
                'url': url,
                'gold_cost': gold_cost,
                'lore': lore,
                'thumbnail': thumbnail,
            }

            print(f"Adding item {name} {gold_cost} - {lore}")
            items.append(item)

    return items


if __name__ == "__main__":
    # Convert list of heroes to yaml.
    data = {'heroes': [], 'items': []}

    # Get list of items.
    data['items'] = get_items()

    # Get list of heroes.
    for hero in get_heroes():
        data['heroes'].append(hero.to_dict())
        
    # Export as yaml file.
    with open('dota_wiki.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False, Dumper=Dumper,
                  width=float("inf"))
    
    # Export as json file.
    with open('dota_wiki.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)
