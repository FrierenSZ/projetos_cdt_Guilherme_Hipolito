from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from services.pokeapi import (
    get_all_pokemon, 
    get_pokemon_details, 
    get_pokemon_species, 
    get_evolution_chain, 
    get_ability_description,
    get_pokemon_varieties_details, 
    get_move_details,
    get_generic_z_moves_local
)

from services.translator import translate_to_portuguese

from services.gemini import get_pokemon_agent_response 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pokedex')
def pokedex():
    page = int(request.args.get('page', 1))
    per_page = 70
    
    all_data = get_all_pokemon()
    if not all_data:
        return render_template('pokedex.html', pokemon_list=[], page=page, total_pages=0)
    
    pokemon_list = all_data['results']
    total_items = len(pokemon_list)
    total_pages = (total_items + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    page_items = []
    for p in pokemon_list[start:end]:
        p_id = p['url'].split('/')[-2]
        page_items.append({
            'name': p['name'],
            'url': p['url'],
            'id': p_id,
            'image': f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p_id}.png"
        })
        
    return render_template('pokedex.html', 
                            pokemons=page_items, 
                            page=page, 
                            total=total_items,
                            total_pages=total_pages)
    
    
@app.route('/api/search_pokemon')
def search_pokemon_api():
    query = request.args.get('query', '').lower().strip()
    
    if len(query) < 2:
        return jsonify([])
    
    all_pokemon_data = get_all_pokemon()
    
    if not all_pokemon_data or not all_pokemon_data.get('results'):
        return jsonify([])

    results = []
    
    for pokemon in all_pokemon_data['results']:
        name = pokemon['name']
        
        url_parts = pokemon['url'].split('/')
        pokemon_id = url_parts[-2]
        
        if query in name or query == pokemon_id:
            results.append({
                'name': name,
                'id': pokemon_id,
                'url': pokemon['url'] 
            })
            if len(results) >= 10:
                break
    return jsonify(results)

def calculate_stats_range(stats_data):
    if isinstance(stats_data, list):
        base_stats = {item['stat']['name']: item['base_stat'] for item in stats_data}
    else:
        base_stats = stats_data

    ranges = {}
    for stat, base in base_stats.items():
        if stat == 'hp':
            min_val = 2 * base + 110
            max_val = 2 * base + 204
        else:
            min_val = int((2 * base + 5) * 0.9)
            max_val = int((2 * base + 99) * 1.1)
            
        
        if base < 60:
            color = '#ff4e4e' 
        elif base < 90:
            color = '#f0932b' 
        elif base < 120:
            color = '#f1c40f' 
        else:
            color = '#6ab04c' 
            
        ranges[stat] = {'base': base, 'min': min_val, 'max': max_val, 'color': color}
    return ranges

@app.route('/pokemon/<name_or_id>')
def pokemon_detail(name_or_id):
    
    pokemon = get_pokemon_details(name_or_id)
    if not pokemon:
        return "Pokemon não encontrado", 404
    
    pokemon['stats_ranges'] = calculate_stats_range(pokemon['stats'])

    
    species = None
    if 'species' in pokemon and 'url' in pokemon['species']:
        species_url = pokemon['species']['url']
        species = get_pokemon_species(species_url) 
    elif pokemon.get('id'):
          species = get_pokemon_species(pokemon['id'])

    
    evolution_chain = None
    varieties = []
    
    if species:
        if species.get('evolution_chain') and species['evolution_chain'].get('url'):
            evolution_chain = get_evolution_chain(species['evolution_chain']['url'])
        
        if species.get('flavor_text'):
            try:
                species['flavor_text'] = translate_to_portuguese(species['flavor_text'])
            except:
                pass 

        if species.get('id'):
            varieties = get_pokemon_varieties_details(species['id']) 


    abilities_with_desc = []
    for ability_name in pokemon['abilities']:
        ability_data = get_ability_description(ability_name)
        
        if ability_data and ability_data.get('description'):
            try:
                ability_data['description'] = translate_to_portuguese(ability_data['description'])
            except:
                pass 
                
        abilities_with_desc.append(ability_data)
        
    
    return render_template('detail.html', 
                            pokemon=pokemon, 
                            species=species,
                            evolution_chain=evolution_chain,
                            abilities=abilities_with_desc,
                            varieties=varieties) 

@app.route('/api/move/<move_name>')
def get_move_info(move_name):
    
    move_details = get_move_details(move_name)
    if move_details:
        if move_details.get('effect'):
            try:
                move_details['effect'] = translate_to_portuguese(move_details['effect'])
            except:
                pass 
                
        return jsonify(move_details)
    return jsonify({'error': 'Move not found'}), 404

@app.route('/api/z_moves_generic', methods=['GET'])
def get_z_moves_api():
    z_moves_data = get_generic_z_moves_local() 
    return jsonify(z_moves_data)


@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Nenhum prompt fornecido'}), 400
        
        response_text = get_pokemon_agent_response(prompt)
        
        return jsonify({'response': response_text})

    except Exception as e:
        print(f"Erro no processamento da requisição /api/ai_chat: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    
    from livereload import Server
    server = Server(app.wsgi_app)

    server.watch('templates/*.html')
    server.watch('static/css/*.css')
    server.watch('static/js/*.js')
    
    print("Iniciando servidor com LiveReload na porta 5000...")
    server.serve(port=5000)