import sqlite3
import requests
import os
import json
from time import sleep

# --- CONFIGURAÇÕES ---
DB_PATH = 'pokemons.db' 
SPRITES_DIR = 'assets/sprites/' # Onde os arquivos PNG serão salvos

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def download_and_cache_sprites():
    """Baixa as imagens dos sprites da URL e salva no disco local."""
    
    # 1. Cria a pasta se não existir
    if not os.path.exists(SPRITES_DIR):
        os.makedirs(SPRITES_DIR)
        print(f"Pasta '{SPRITES_DIR}' criada.")

    print("Conectando ao banco de dados...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Adiciona a coluna 'sprite_path_local' se ela não existir
    try:
        cursor.execute("ALTER TABLE pokemons ADD COLUMN sprite_path_local TEXT")
        print("Coluna 'sprite_path_local' adicionada à tabela.")
    except sqlite3.OperationalError:
        # A coluna já existe, ignora o erro
        pass

    # 2. Seleciona todos os Pokémons
    data = conn.execute("SELECT id, sprite_url, sprite_path_local FROM pokemons ORDER BY id ASC").fetchall()
    
    total_pokemons = len(data)
    print(f"Encontrados {total_pokemons} Pokémon no DB. Iniciando download...")

    for index, row in enumerate(data):
        pokemon_id = row['id']
        sprite_url = row['sprite_url']
        local_path = os.path.join(SPRITES_DIR, f"{pokemon_id}.png")
        
        # Se a imagem local já existe E o caminho local já foi salvo no DB, ignora
        if os.path.exists(local_path) and row['sprite_path_local'] == local_path:
            # print(f"[{pokemon_id:03}/{total_pokemons}] Sprite já cacheado. Ignorando.")
            continue
            
        if sprite_url:
            print(f"[{pokemon_id:03}/{total_pokemons}] Baixando sprite de {sprite_url}...")
            try:
                response = requests.get(sprite_url, timeout=10)
                response.raise_for_status()
                
                # Salva o arquivo PNG
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                # Atualiza o DB com o novo caminho local
                cursor.execute("""
                    UPDATE pokemons SET sprite_path_local = ? WHERE id = ?
                """, (local_path, pokemon_id))
                
            except requests.exceptions.RequestException as e:
                print(f"Erro ao baixar sprite para Pokémon {pokemon_id}: {e}")
            
            # Adicione um pequeno delay para evitar sobrecarregar a API
            sleep(0.05) 
        
    conn.commit()
    conn.close()
    print("\n✅ Cache de sprites concluído!")

if __name__ == "__main__":
    download_and_cache_sprites()