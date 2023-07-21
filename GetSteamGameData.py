import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

# ALL_GAME_URL = 'https://store.steampowered.com/search/results/?query&start=50&count=50&dynamic_data=&sort_by=_ASC&category1=998&supportedlang=english&snr=1_7_7_230_7&infinite=1'
ALL_GAME_URL = 'https://store.steampowered.com/search/results/?query&start=0&count=50'
HOVER_DATA_URL = 'https://store.steampowered.com/apphover/440'
GAME_URL_PATTERN = r'^https://store.steampowered.com/app'
# PUBLISHER_PATTERN = [r'^https://store.steampowered.com/publisher/', 
#                      r'^https://store.steampowered.com/search/\?publisher/']
EARLY_ACCESS_PATTERN = r"Early Access Release Date: \w+ \d+, \d+"
def get_all_game_data(url):
    r = requests.get(url)
    # data = dict(r.json())
    return r.text

def get_game_detail_data(url):
    r = requests.get(url)
    data = r.text
    return data

def get_language_string(table):    
    """
    Parses language <table> followed by multiple <tr> (table rows) and inner <td> (table data) tags. 
    returns all supported languages joined by ','. 
    Accepts only one <th> (table header/data) in the first row.
    """
    def rowgetDataText(tr, coltag='td'): # td (data) or th (header)       
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]  
    
    rows = []
    trs = table.find_all('tr')
    headerow = rowgetDataText(trs[0], 'th')
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    
    for tr in trs: # for every table row
        rows.append(rowgetDataText(tr, 'td') ) # data row 
    
    table_df = pd.DataFrame(rows[1:], columns=rows[0])
    language = ','.join(table_df.iloc[:, 0])
    
    return language

def parse_game_data(data):
    game_list = []
    soup = BeautifulSoup(data, 'html.parser')
    games = soup.find_all('a', href=re.compile(GAME_URL_PATTERN))
    
    for game in games:
        game_id = game.get('data-ds-appid')
        # game_tag_id = game.find()
        game_name = game.find('span', {'class': 'title'}).text
        # platform = game.find()
        link = f"https://store.steampowered.com/app/{game_id}"
        
        game_data = {
            'GameId': game_id,
            'GameName': game_name,
            'Link': link
        }

        game_list.append(game_data)
    
    return pd.DataFrame(game_list)

def parse_game_detail_data(data):
    soup = BeautifulSoup(data, 'html.parser')
    game_name = soup.find('div', {'class': 'apphub_AppName'}).text.strip()
    description = soup.find('div', {'class': 'game_description_snippet'}).text.strip()
    developer = soup.find('div', {'class': 'summary column', 'id': 'developers_list'}).text.strip()
    try:
        publisher = soup.find('a', href=re.compile(r'^https://store.steampowered.com/publisher/')).text
    except:
        try:
            publisher = soup.find('a', {'href': re.compile(r"https://store\.steampowered\.com/search/\?publisher=")}).text
        except:
            publisher = ''
    release_date = soup.find('div', {'class': 'date'}).text
    detail_block_text = soup.find('div', {'class': 'details_block'}).text.strip()
    string_match = re.search(EARLY_ACCESS_PATTERN, detail_block_text)
    if string_match:
        early_access_date = string_match.group()
    else:
        early_access_date = ''
    
    # TODO: memory and storage for different systems
    try:
        requirements = soup.find('div', {'class': 'game_area_sys_req_full'}).find_all('li')
        for requirement in requirements:
            if requirement.text.split(':')[0] == 'Memory':
                memory = requirement.text.split(':')[1]
            elif requirement.text.split(':')[0] in ['Storage', 'Hard Disk Space']:
                storage = requirement.text.split(':')[1]
    except:
        memory = ''
        storage = ''
        # requirement_name =  requirement.text.split(':')[0]
        # requirement_value = requirement.text.split(':')[1]
    
    genres = soup.find('div', {'class': 'details_block'}).find('span').text
    language_table = soup.find('table')
    language = get_language_string(language_table)
    tags = ','.join(soup.find('div', {'class': 'glance_tags'}).text.split())
    category = soup.find('div', {'class': 'block', 'id': 'category_block'}).text.strip()
    category = re.sub(r'([a-z])([A-Z])', r'\1,\2', category)
    try:
        rating_description = soup.find('p', {'class': 'descriptorText'}).text.replace('\r\n', ',')
    except:
        rating_description = ''
    
    game_detail_data = {
        'GameName': game_name,
        'Description': description,
        'Developer': developer,
        'Publisher': publisher,
        'ReleaseDate': release_date,
        'EarlyAccessDate': early_access_date,
        'Memory': memory,
        'Storage': storage,
        'Generes': genres,
        'Language': language,
        'Tags': tags,
        'Category': category,
        'RatingDescription': rating_description
    }

    return game_detail_data


game_df = parse_game_data(get_all_game_data(ALL_GAME_URL))
# print(game_df.head())
# game_df.to_csv('Data/AllGameData.csv', index=False)
game_detail_list = []
for index, row in game_df.iterrows():
    print(row)
    data = get_game_detail_data(row['Link'])
    # print(data)
    game_detail_list.append(parse_game_detail_data(data))

game_detail_df = pd.DataFrame(game_detail_list)
game_detail_df.to_csv('Data/GameDetail.csv', index=False)

# data = get_game_detail_data('https://store.steampowered.com/app/671860')
# detail_data = parse_game_detail_data(data)
# print(detail_data)