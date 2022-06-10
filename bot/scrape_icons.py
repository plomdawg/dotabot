import requests
from bs4 import BeautifulSoup
from time import sleep
import os


def get_hero_icons():
    responses = []
    url = f'https://dota2.gamepedia.com/Hero_complexity'
    print(f"Loading data from {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find(class_='wikitable')
    icons = table.find_all('img')
    for icon in icons:
        name = icon.get('alt').replace(' ', '_').replace('_minimap_icon', '')
        url = icon.get('data-src')
        if url is None:
            url = icon.get('src')
        print(f"icon: {name} url: {url}")
        req = requests.get(url)
        path = os.path.join('assets', 'icons', name)
        with open(path, 'wb') as f:
            f.write(req.content)


def get_rune_icons():
    icons = []
    url = f'https://dota2.gamepedia.com/Runes#List'
    print(f"Loading data from {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    icons = [icon for icon in soup.find_all(
        'img') if "minimap_icon" in icon.get('src')]
    for icon in icons:
        name = icon.get('alt').replace(' ', '_').replace('_minimap_icon', '')
        url = icon.get('data-src')
        if url is None:
            url = icon.get('src')
        print(f"icon: {name} url: {url}")
        req = requests.get(url)
        path = os.path.join('assets', 'icons', name)
        with open(path, 'wb') as f:
            f.write(req.content)


get_hero_icons()
get_rune_icons()
