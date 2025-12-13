import os
from flask import app, json, jsonify, request
import requests
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed 

BASE_URL = "https://pokeapi.co/api/v2"

@lru_cache(maxsize=1500)
def get_pokemon_list(limit=20, offset=0):
    try:
        url = f"{BASE_URL}/pokemon?limit={limit}&offset={offset}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=600)
def get_all_pokemon():
    try:
        url = f"{BASE_URL}/pokemon?limit=1"
        response = requests.get(url)
        response.raise_for_status()
        total_count = response.json()['count']
        
        url = f"{BASE_URL}/pokemon?limit={total_count}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=1000)
def get_pokemon_details(name_or_id):
    try:
        url = f"{BASE_URL}/pokemon/{name_or_id}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        

        moves_list = [{'name': m['move']['name'], 'url': m['move']['url']} 
             for m in data.get('moves', [])]
        
        parsed_data = {
            'id': data['id'],
            'name': data['name'],
            'height': data['height'],
            'weight': data['weight'],
            'types': [t['type']['name'] for t in data['types']],
            'stats': {s['stat']['name']: s['base_stat'] for s in data['stats']},
            'abilities': [a['ability']['name'] for a in data['abilities']],
            'moves': moves_list, 
            'sprites': {
                'front_default': data['sprites']['front_default'],
                'front_shiny': data['sprites']['front_shiny'],
                'back_default': data['sprites']['back_default'],
                'back_shiny': data['sprites']['back_shiny'],
                'artwork_default': data['sprites']['other']['official-artwork']['front_default'],
                'artwork_shiny': data['sprites']['other']['official-artwork']['front_shiny'],
                'dream_world': data['sprites']['other']['dream_world']['front_default']
            }
        }
        return parsed_data
    except requests.RequestException as e:
        print(f"Erro ao buscar detalhes do Pokémon {name_or_id}: {e}")
        return None

@lru_cache(maxsize=800)
def get_pokemon_species(name_or_id):
    try:
        url = f"{BASE_URL}/pokemon-species/{name_or_id}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        flavor_text = None
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'pt-BR':
                flavor_text = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                break
        
        if not flavor_text:
            for entry in data['flavor_text_entries']:
                if entry['language']['name'] == 'en':
                    flavor_text = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                    break
        
        parsed_data = {
            'id': data['id'],
            'name': data['name'],
            'flavor_text': flavor_text,
            'evolution_chain_url': data['evolution_chain']['url'] if data.get('evolution_chain') else None,
            'genera': next((g['genus'] for g in data['genera'] if g['language']['name'] == 'pt-BR'), 
                             next((g['genus'] for g in data['genera'] if g['language']['name'] == 'en'), None)),
            'varieties': data.get('varieties', [])
        }
        return parsed_data
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=800)
def get_pokemon_varieties_details(name_or_id):
    species_data = get_pokemon_species(name_or_id)
    if not species_data or not species_data.get('varieties'):
        return []

    varieties_details = []
    base_name = species_data['name']

    for variety in species_data['varieties']:
        if not variety['is_default']:
            variety_name = variety['pokemon']['name']
            details = get_pokemon_details(variety_name)
            if details:
                readable_name = variety_name.replace(base_name, '').replace('-', ' ').strip().title()
                if not readable_name:
                    readable_name = "Alternative Form"
                details['form_name'] = readable_name
                varieties_details.append(details)
    
    return varieties_details

@lru_cache(maxsize=1) 
def get_generic_z_moves_local():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'zmoves.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Z-Moves genéricos carregados com sucesso do arquivo: {file_path}")
            return data
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo zmoves.json não encontrado em: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ ERRO ao decodificar zmoves.json: {e}")
        return []

@lru_cache(maxsize=800)
def get_evolution_chain(chain_url):
    try:
        response = requests.get(chain_url)
        response.raise_for_status()
        data = response.json()
        
        def extract_chain(chain_data):
            current = {
                'name': chain_data['species']['name'],
                'url': chain_data['species']['url']
            }
            
            evolutions = []
            for evolution in chain_data.get('evolves_to', []):
                evolutions.append(extract_chain(evolution))
            
            if evolutions:
                current['evolves_to'] = evolutions
            
            return current
        
        return extract_chain(data['chain'])
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=800)
def get_ability_description(ability_name):
    try:
        url = f"{BASE_URL}/ability/{ability_name}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        description = None
        for entry in data.get('effect_entries', []):
            if entry['language']['name'] == 'en':
                description = entry['short_effect']
                break
        
        return {
            'name': data['name'],
            'description': description or "Descrição não disponível"
        }
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return {'name': ability_name, 'description': "Descrição não disponível"}

@lru_cache(maxsize=1000)
def get_move_details(name_or_id):
    try:
        url = f"{BASE_URL}/move/{name_or_id}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        effect = None
        for entry in data.get('effect_entries', []):
            if entry['language']['name'] == 'en':
                effect = entry['short_effect']
                break
        
        parsed_data = {
            'id': data['id'],
            'name': data['name'],
            'accuracy': data['accuracy'],
            'power': data['power'],
            'pp': data['pp'],
            'type': data['type']['name'],
            'damage_class': data['damage_class']['name'],
            'effect': effect or "No description available"
        }
        return parsed_data
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None


MAX_CONCURRENT_REQUESTS = 20 

def get_abilities_details_in_parallel(ability_names, translator_func=None):

    abilities_with_desc = []
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:

        future_to_ability = {
            executor.submit(get_ability_description, name): name 
            for name in ability_names
        }
        
        for future in as_completed(future_to_ability):
            ability_data = future.result()
            
            if ability_data and ability_data.get('description') and translator_func:
                try:
                    ability_data['description'] = translator_func(ability_data['description'])
                except Exception:
                    pass
            
            abilities_with_desc.append(ability_data)
            
    return abilities_with_desc

def get_moves_details_in_parallel(move_list, translator_func=None):

    move_details_list = []
    move_names = [move['name'] for move in move_list]
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        future_to_move = {
            executor.submit(get_move_details, name): name 
            for name in move_names 
        }
        
        for future in as_completed(future_to_move):
            move_data = future.result()
            
            if move_data and move_data.get('effect') and translator_func:
                try:
                    move_data['effect'] = translator_func(move_data['effect'])
                except Exception:
                    pass
            
            if move_data:
                move_details_list.append(move_data)
                
    return move_details_list