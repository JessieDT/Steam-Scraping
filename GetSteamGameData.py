import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

ALL_GAME_URL = 'https://store.steampowered.com/search/results/?query&start=0&count=50'
HOVER_DATA_URL = 'https://store.steampowered.com/apphover/440'

def get_all_game_data(url):
    r = requests.get(url)
    # data = dict(r.json())
    return r.text

def get_game_detail_data(url):
    r = requests.get(url)
    data = r.text
    return data

def parse_game_data(data):
    game_list = []
    soup = BeautifulSoup(data, 'html.parser')
    game_url_pattern = r'^https://store.steampowered.com/app'
    games = soup.find_all('a', href=re.compile(game_url_pattern))
    for game in games:
        game_id = game.get('data-ds-appid')
        # game_tag_id = game.find()
        title = game.find('span', {'class': 'title'}).text
        # platform = game.find()
        link = f"https://store.steampowered.com/app/{game_id}"
        
        game_data = {
            'Id': game_id,
            'Title': title,
            'Link': link
        }

        game_list.append(game_data)
    
    return pd.DataFrame(game_list)

def parse_game_detail_data(data):
    soup = BeautifulSoup(data, 'html.parser')
    description = soup.find('div', {'class': 'game_description_snippet'}).text
    developer = soup.find('div', {'class': 'summary column', 'id': 'developers_list'}).text.strip()
    publisher_pattern = r'^https://store.steampowered.com/publisher/'
    publisher = soup.find('a', href=re.compile(publisher_pattern)).text
    release_date = soup.find('div', {'class': 'date'}).text
    requirements = soup.find('div', {'class': 'game_area_sys_req_full'}).find_all('li')
    for requirement in requirements:
        requirement_name =  requirement.text.split(':')[0]
        requirement_value = requirement.text.split(':')[1]
    genres = soup.find('div', {'class': 'details_block'}).find('span').text

# game_df = parse_game_data(get_all_game_data(ALL_GAME_URL))
# game_df.to_csv('Data/AllGameData.csv', index=False)