from flask import Flask, render_template, request
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api_token = os.getenv('CR')
headers = {'Authorization': f'Bearer {api_token}'}
base_url = 'https://api.clashroyale.com/v1'

# Diccionario de imágenes de cofres
chest_images = {
    "Silver Chest": "/static/images/Silver_Chest.png",
    "Golden Chest": "/static/images/Golden_Chest.png",
    "Giant Chest": "/static/images/Giant_Chest.png",
    "Magical Chest": "/static/images/Magical_Chest.png",
    "Epic Chest": "/static/images/EpicChest.png",
    "Legendary Chest": "/static/images/LegendChest.png",
    "Mega Lightning Chest": "/static/images/MegaLightningChest.png",
    "Plentiful Gold Crate": "/static/images/Plentiful_Gold_Crate.png",
    "Overflowing Gold Crate": "/static/images/Overflowing_Gold_Crate.png",
    "Royal Wild Chest": "/static/images/King's_Chest.png",
    "Fortune Chest": "/static/images/Fortune_Chest.png",
    "Lightning Chest": "/static/images/Lightning_Chest.png",
    "Wooden Chest": "/static/images/Wooden_Chest.png",
    "Crown Chest": "/static/images/Crown_Chest.png",
    "Tower Troop Chest": "/static/images/Tower_Troop_Chest.png",
    "Legendary King's Chest": "/static/images/Legendary_King's_Chest.png",
    "Gold Crate": "/static/images/Gold_Crate.png",
    "Champion Chest": "/static/images/Champion_Chest.png"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player_info', methods=['GET', 'POST'])
def player_info():
    player_data = None
    chests_data = None
    if request.method == 'POST':
        player_tag_input = request.form['player_tag']
        player_tag = f'%23{player_tag_input}'
        
        response_player = requests.get(f'{base_url}/players/{player_tag}', headers=headers)
        response_chests = requests.get(f'{base_url}/players/{player_tag}/upcomingchests', headers=headers)
        
        if response_player.status_code == 200:
            player_data = response_player.json()
        else:
            print(f"Error fetching player data: {response_player.status_code} - {response_player.text}")
        
        if response_chests.status_code == 200:
            chests_data = response_chests.json()['items']
        else:
            print(f"Error fetching chests data: {response_chests.status_code} - {response_chests.text}")
    
    return render_template('player_info.html', player_data=player_data, chests_data=chests_data, chest_images=chest_images)

@app.route('/card_info', methods=['GET', 'POST'])
def card_info():
    cards_data = []
    if request.method == 'POST':
        search_term = request.form['card_name'].strip().lower()
        response = requests.get(f'{base_url}/cards', headers=headers)
        
        if response.status_code == 200:
            all_cards = response.json()['items']
            cards_data = [card for card in all_cards if card['name'].strip().lower().startswith(search_term)]
        else:
            print(f"Error fetching cards data: {response.status_code} - {response.text}")
    
    return render_template('card_info.html', cards_data=cards_data)

@app.route('/global_rankings', methods=['GET', 'POST'])
def global_rankings():
    rankings = []
    if request.method == 'POST':
        season_id = request.form['season_id']
        result_limit = int(request.form['result_limit'])
        
        url = f"{base_url}/locations/global/pathoflegend/{season_id}/rankings/players?limit={result_limit}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            rankings = response.json().get('items', [])
        else:
            print(f"Error fetching global rankings: {response.status_code} - {response.text}")
    
    return render_template('global_rankings.html', rankings=rankings)

@app.route('/regional_rankings', methods=['GET', 'POST'])
def regional_rankings():
    rankings = []
    if request.method == 'POST':
        region_name = request.form['region_name'].capitalize()
        result_limit = int(request.form['result_limit'])
        
        location_id = None
        is_country = None
        
        if region_name == "Global":
            location_id = 'global'
        else:
            url_locations = f"{base_url}/locations"
            response_locations = requests.get(url_locations, headers=headers)
            if response_locations.status_code == 200:
                locations = response_locations.json().get('items', [])
                for location in locations:
                    if location['name'].capitalize() == region_name:
                        location_id = location['id']
                        is_country = location['isCountry']
                        break
        
        if location_id and (is_country is not False or location_id == 'global'):
            url_ranking = f"{base_url}/locations/{location_id}/pathoflegend/players?limit={result_limit}"
            response_ranking = requests.get(url_ranking, headers=headers)
            if response_ranking.status_code == 200:
                rankings = response_ranking.json().get('items', [])
            else:
                print(f"Error fetching regional rankings: {response_ranking.status_code} - {response_ranking.text}")
    
    return render_template('regional_rankings.html', rankings=rankings)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
