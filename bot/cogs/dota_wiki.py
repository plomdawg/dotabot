import requests
import yaml
from bs4 import BeautifulSoup
import time
import sys


# Fix yaml indenting (https://stackoverflow.com/a/39681672/12757998).
class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(Dumper, self).increase_indent(flow, False)


class Item:
    def __init__(self, element) -> None:

        # Check if the element has a gold cost.
        gold_element = element.find('span')
        if gold_element is None:
            self.gold_cost = None
        else:
            self.gold_cost = int(gold_element.text.strip())

        # Extract the thumbnail and name from the element.
        img = element.find('img')
        self.thumbnail = img.get('data-src')
        if self.thumbnail is None:
            self.thumbnail = img.get('src')

        self.name = element.find_all('a')[1].text

    def to_dict(self) -> dict:
        return {
            '_name': self.name,
            'gold_cost': self.gold_cost,
            'thumbnail': self.thumbnail,
        }


class Response:
    def __init__(self, text, url) -> None:
        self.text = text
        self.url = url

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'url': self.url
        }


class Ability:
    def __init__(self, element):
        # Extract the lore text.
        self.lore = element.find(class_="ability-lore").text

        # Extract the thumbnail.
        self.thumbnail = element.find(class_='image').get('href')

        # Remove extra text from the div containing the ability name.
        element.find('div').find('div').find('div').decompose()

        # Remove extra spaces from the div containing the ability name.
        self.name = element.find('div').find('div').text.strip()

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'lore': self.lore,
            'thumbnail': self.thumbnail,
        }


def get_abilities(hero) -> list:
    abilities = []

    # Dota wiki page that lists all abilities for a hero.
    url = f"{hero.url}"

    # Load the page into BeautifulSoup.
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the ability elements on the page.
    for element in soup.find_all(class_='ability-background'):
        abilities.append(Ability(element))

    return abilities


def get_responses(hero) -> list:
    """ Returns a list of Response objects for a Hero """
    responses = []

    # Dota wiki page that lists all responses for a hero.
    url = f"{hero.url}/Responses"

    # Load the page into BeautifulSoup.
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the main content on the page.
    content = soup.find(class_='mw-parser-output')

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
        responses.append(Response(voice_line_text, voice_line_url))

    # Return the responses.
    return responses


class Hero:
    def __init__(self, element) -> None:
        # Hero name (e.g. 'Techies')
        # Replace escape code with space.
        self.name = element.text.replace('\xa0', ' ')

        # Dota wiki URL (e.g. 'https://dota2.fandom.com/wiki/Techies')
        self.url = f"https://dota2.fandom.com{element.get('href').replace('/Lore', '')}"

        # Load responses.
        self.responses = get_responses(self)

        # Load abilities.
        self.abilities = get_abilities(self)

        print(
            f"{self.name} has {len(self.responses)} responses and {len(self.abilities)} abilities.")


def get_heroes() -> list:
    """ Returns a list of Hero objects for all current heroes. """
    heroes = []

    # Dota wiki page that lists all heroes.
    url = "https://dota2.fandom.com/wiki/Template:Lore_nav/heroes"

    # Load the page into BeautifulSoup.
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # Find the main content on the page.
    content = soup.find(class_='notanavbox-list notanavbox-odd')

    # Find all of the hero elements on the page.
    for hero_element in content.find_all('a'):
        # Create hero object.
        heroes.append(Hero(hero_element))

    return heroes


def get_items() -> list:
    """ Returns a list of Item objects for all current items. """
    items = []

    # Dota wiki page that lists all items.
    url = "https://dota2.fandom.com/wiki/Items"

    # Load the page into BeautifulSoup.
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # Find the main content on the page.
    content = soup.find(class_='mw-parser-output')

    # Remove stuff we do not need.
    content.find(id='pageTabber').decompose()
    content.find(id='toc').decompose()
    content.find('p').decompose()
    retired_element = content.find(id="Retired")
    for element in retired_element.find_all_next():
        element.decompose()
    retired_element.decompose()

    # Find all item lists on the page.
    itemlist_elements = content.find_all(class_='itemlist')
    for itemlist in itemlist_elements:
        for item_element in itemlist.find_all('div'):
            items.append(Item(item_element))

    return items


if __name__ == "__main__":
    # Convert list of heroes to yaml.
    data = {'heroes': [], 'items': []}

    # Get list of items.
    for item in get_items():
        data['items'].append(item.to_dict())

    # Get list of heroes.
    for hero in get_heroes():
        # Append name with _ so it shows at the top of the yaml block.
        hero_data = {'_name': hero.name}

        # Add abilities.
        ability_data = [a.to_dict() for a in hero.abilities]
        hero_data['abilities'] = ability_data

        # Add responses.
        response_data = [r.to_dict() for r in hero.responses]
        hero_data['responses'] = response_data

        data['heroes'].append(hero_data)

    with open('dota_wiki.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False, Dumper=Dumper,
                  width=float("inf"))
