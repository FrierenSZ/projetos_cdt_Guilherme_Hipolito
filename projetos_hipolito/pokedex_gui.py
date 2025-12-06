import customtkinter as ctk
import tkinter as tk
import sqlite3 
import requests 
import os
import json 
from PIL import Image
from io import BytesIO

# --- CONFIGURAÇÕES GERAIS ---
DB_PATH = os.path.join(os.path.dirname(__file__), "pokemons.db") 

# Define o diretório dos Sprites. Ele presume que 'assets/sprites' está na mesma pasta do 'pokemons.db'.
SPRITES_DIR = os.path.join(os.path.dirname(DB_PATH), "assets", "sprites")

# --- CONFIGURAÇÕES DE LAYOUT ---
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "assets", "images", "Pokedex2_background.png")
POKEMONS_PER_PAGE = 30
CURRENT_PAGE = 1

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

class PokedexPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.current_page = 1
        self.total_pokemons = 0
        
        # OTIMIZAÇÃO: Cache em RAM para evitar que as imagens baixadas sumam ao rolar.
        # Guarda a referência de CTkImage para cada ID de Pokémon.
        self.image_references = {} 
        
        # Carrega dados do DB e define a fonte da imagem (disco local ou URL)
        self.all_pokemon_data = self.load_all_pokemon_db()
        self.pokemon_names = self.load_pokemon_names() 

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.load_background_image()
        
        self.create_ai_sidebar()

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(2, weight=1)
        
        self.create_top_navigation(self.main_content_frame)

        self.cards_scrollable_frame = ctk.CTkScrollableFrame(self.main_content_frame, 
                                                               fg_color=("gray90", "gray15"), 
                                                               corner_radius=10,
                                                               label_text="Catálogo Pokémon",
                                                               label_font=("Arial", 18, "bold"))
        self.cards_scrollable_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        
        for i in range(5):
             self.cards_scrollable_frame.grid_columnconfigure(i, weight=1)

        self.pagination_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.pagination_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self.pagination_frame.grid_columnconfigure(0, weight=1)
        self.pagination_frame.grid_columnconfigure(1, weight=1)
        self.pagination_frame.grid_columnconfigure(2, weight=1)
        
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="", font=("Arial", 14))
        self.page_label.grid(row=0, column=1, padx=20)
        
        self.show_page(self.current_page)


    # ------------------------------------------------------------------
    # --- MÉTODOS DE ESTRUTURA E LAYOUT ---
    # ------------------------------------------------------------------
    
    def load_background_image(self):
        try:
            bg_image = Image.open(BACKGROUND_PATH)
            width, height = self.winfo_screenwidth(), self.winfo_screenheight() 
            bg_resized = bg_image.resize((width, height), Image.Resampling.LANCZOS)
            
            self.tk_background_image = ctk.CTkImage(light_image=bg_resized, dark_image=bg_resized, size=(width, height))
            
            self.background_label = ctk.CTkLabel(self, text="", image=self.tk_background_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.background_label.lower()
        except Exception as e:
            pass

    def create_ai_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=10, 
                                     fg_color=("white", "gray20"))
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        label_title = ctk.CTkLabel(self.sidebar, text="Assistente IA Pokémon", 
                                   font=("Arial", 18, "bold"), text_color="#3D79AE")
        label_title.grid(row=0, column=0, pady=10)

        self.ai_chat_box = ctk.CTkTextbox(self.sidebar, height=300, state="disabled",
                                          font=("Consolas", 13))
        self.ai_chat_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.ai_input = ctk.CTkEntry(self.sidebar, placeholder_text="Pergunte sobre um Pokémon...", 
                                     font=("Arial", 14), height=35)
        self.ai_input.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="s")
        
        btn_send = ctk.CTkButton(self.sidebar, text="Enviar", width=80)
        btn_send.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="s")

    def create_top_navigation(self, parent_frame):
        top_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)
        
        btn_back = ctk.CTkButton(top_frame, 
                                 text="<< Menu", 
                                 command=lambda: self.controller.show_frame("MainPage"),
                                 width=100, height=35, fg_color="#A51F1F", 
                                 hover_color="#7A0000", font=("Arial", 16, "bold"))
        btn_back.grid(row=0, column=0, padx=(0, 20), sticky="w")
        
        self.create_search_bar_widget(top_frame)

    def create_search_bar_widget(self, parent_frame):
        search_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(search_frame, 
                                         placeholder_text="Buscar Pokémon (Nome ou ID)",
                                         font=("Arial", 16),
                                         height=35,
                                         corner_radius=8)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        search_button = ctk.CTkButton(search_frame, 
                                      text="Buscar", 
                                      command=self.perform_search_from_entry,
                                      width=80, height=35,
                                      font=("Arial", 16, "bold"))
        search_button.grid(row=0, column=1)

        self.autocomplete_listbox = tk.Listbox(search_frame, height=5, bd=1, relief="flat",
                                              highlightthickness=0, fg="#333", font=("Arial", 14),
                                              selectbackground="#3D79AE", selectforeground="white")
        self.autocomplete_listbox.place(relx=0, rely=1.0, relwidth=1, y=5)
        self.autocomplete_listbox.lower()
        
        self.autocomplete_listbox.bind("<<ListboxSelect>>", self.select_autocomplete)
        self.search_entry.bind("<KeyRelease>", self.autocomplete_handler)
        self.search_entry.bind("<FocusOut>", lambda e: self.after(100, self.autocomplete_listbox.place_forget))

    # --- FUNÇÃO OTIMIZADA PARA LER CAMINHO ABSOLUTO DO DISCO ---
    def load_all_pokemon_db(self):
        try:
            conn = get_db_connection()
            # Seleciona o campo 'sprite_path_local' que contém o caminho relativo
            data = conn.execute("SELECT id, nome, tipos, sprite_url, sprite_path_local FROM pokemons ORDER BY id ASC").fetchall()
            conn.close()
            
            pokemon_list = []
            for row in data:
                sprite_relative_path = row['sprite_path_local']
                
                # Constrói o caminho ABSOLUTO usando o diretório base do projeto (onde está o DB)
                sprite_full_path = None
                if sprite_relative_path:
                    # Garantir que o separador de caminho funcione no Windows (\) ou Linux (/)
                    base_dir = os.path.dirname(DB_PATH)
                    sprite_full_path = os.path.join(base_dir, sprite_relative_path.replace('/', os.sep))
                
                # Define a fonte da imagem
                sprite_source = None
                if sprite_full_path and os.path.exists(sprite_full_path):
                    sprite_source = sprite_full_path # Usa o disco local (RÁPIDO)
                else:
                    sprite_source = row['sprite_url'] # Fallback para URL (LENTO)
                    
                pokemon_list.append({
                    'id': row['id'],
                    'name': row['nome'].capitalize(),
                    'types': json.loads(row['tipos']),
                    'sprite_source': sprite_source
                })
            
            self.total_pokemons = len(pokemon_list)
            return pokemon_list
        except Exception as e:
            return []
    # -------------------------------------------------------------

    def show_page(self, page_number):
        self.clear_cards()
        
        start_index = (page_number - 1) * POKEMONS_PER_PAGE
        end_index = start_index + POKEMONS_PER_PAGE
        
        pokemons_to_display = self.all_pokemon_data[start_index:end_index]
        total_pages = (self.total_pokemons + POKEMONS_PER_PAGE - 1) // POKEMONS_PER_PAGE
        
        self.page_label.configure(text=f"Página {page_number}/{total_pages}")
        
        row_idx, col_idx = 0, 0
        COLUMNS = 5

        for pokemon in pokemons_to_display:
            self.create_pokemon_card(self.cards_scrollable_frame, pokemon, row_idx, col_idx)
            
            col_idx += 1
            if col_idx >= COLUMNS:
                col_idx = 0
                row_idx += 1
                
        self.create_pagination_buttons(total_pages)

    def clear_cards(self):
        for widget in self.cards_scrollable_frame.winfo_children():
            widget.destroy()

    def create_pagination_buttons(self, total_pages):
        for widget in self.pagination_frame.winfo_children():
            if widget is not self.page_label:
                widget.destroy()

        btn_prev = ctk.CTkButton(self.pagination_frame, text="< Anterior", 
                                 command=lambda: self.navigate_page(-1), 
                                 state="normal" if self.current_page > 1 else "disabled",
                                 width=120)
        btn_prev.grid(row=0, column=0, padx=10, pady=5)

        btn_next = ctk.CTkButton(self.pagination_frame, text="Próxima >", 
                                 command=lambda: self.navigate_page(1), 
                                 state="normal" if self.current_page < total_pages else "disabled",
                                 width=120)
        btn_next.grid(row=0, column=2, padx=10, pady=5)

    def navigate_page(self, direction):
        new_page = self.current_page + direction
        total_pages = (self.total_pokemons + POKEMONS_PER_PAGE - 1) // POKEMONS_PER_PAGE
        
        if 1 <= new_page <= total_pages:
            self.current_page = new_page
            self.show_page(self.current_page)

    def create_pokemon_card(self, parent_frame, pokemon, row, column):
        card = ctk.CTkFrame(parent_frame, 
                            fg_color=("white", "gray25"), 
                            corner_radius=10, 
                            border_width=1, 
                            border_color="#FFCB05")
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        # Guarda o ID no objeto card para usarmos no cache
        card.pokemon_id = pokemon['id'] 

        name_text = f"#{pokemon['id']:04} {pokemon['name']}"
        name_label = ctk.CTkLabel(card, text=name_text, font=("Arial", 16, "bold"))
        name_label.grid(row=0, column=0, pady=(5, 0))
        
        types_text = ", ".join([t.capitalize() for t in pokemon['types']])
        types_label = ctk.CTkLabel(card, text=types_text, font=("Arial", 12), text_color="gray60")
        types_label.grid(row=2, column=0, pady=(0, 5))

        btn_details = ctk.CTkButton(card, 
                                    text="Ver Detalhes",
                                    command=lambda p_id=pokemon['id']: self.show_details_page(p_id),
                                    fg_color="#3D79AE",
                                    hover_color="#306085",
                                    height=25,
                                    font=("Arial", 14, "bold"))
        btn_details.grid(row=3, column=0, pady=(5, 10), padx=5, sticky="ew")

        # Chama a função que baixa ou pega do cache
        self.load_card_image(card, pokemon['sprite_source']) # Passando a fonte correta (local ou URL)

    # --- FUNÇÃO OTIMIZADA PARA CARREGAR IMAGEM DO DISCO OU URL ---
    def load_card_image(self, parent_card, sprite_source):
        pokemon_id = parent_card.pokemon_id 

        # 1. Tenta carregar do cache de memória temporário (RAM)
        if pokemon_id in self.image_references:
            image_obj = self.image_references[pokemon_id]
            image_label = ctk.CTkLabel(parent_card, text="", image=image_obj)
            image_label.grid(row=1, column=0, pady=5)
            
            # --- CORREÇÃO DE BUG DE ROLAGEM: ANEXAR AO LABEL ---
            image_label.image = image_obj # Anexa a referência forte ao widget
            # ----------------------------------------------------
            return

        try:
            image_data = None
            
            # Checa se é um caminho de arquivo local (termina em .png E o arquivo existe)
            if sprite_source.endswith(".png") and os.path.exists(sprite_source):
                # LEITURA RÁPIDA DO DISCO LOCAL (Instantâneo)
                image_data = Image.open(sprite_source).convert("RGBA")
            else:
                # FALLBACK: Se não existir localmente, baixa da internet (LENTO)
                image_response = requests.get(sprite_source, timeout=5)
                image_response.raise_for_status()
                image_data = Image.open(BytesIO(image_response.content)).convert("RGBA")
                
            if image_data:
                target_size = 100
                resized_image = image_data.resize((target_size, target_size), Image.Resampling.LANCZOS)
                
                pokemon_img_obj = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(target_size, target_size))
                
                # Guarda a referência da imagem no dicionário da página (cache em RAM)
                self.image_references[pokemon_id] = pokemon_img_obj 
                
                image_label = ctk.CTkLabel(parent_card, text="", image=pokemon_img_obj)
                image_label.grid(row=1, column=0, pady=5)
                
                # --- CORREÇÃO DE BUG DE ROLAGEM: ANEXAR AO LABEL ---
                image_label.image = pokemon_img_obj # Anexa a referência forte ao widget
                # ----------------------------------------------------
            else:
                raise Exception("Falha ao carregar imagem.")

        except Exception as e:
            # Em caso de erro, mostra um placeholder
            image_label = ctk.CTkLabel(parent_card, text="Sem Imagem", font=("Arial", 12))
            image_label.grid(row=1, column=0, pady=5)

    def show_details_page(self, pokemon_id):
        # Para exibir os detalhes, vamos criar e mostrar uma nova área de detalhes (se ela não existir)
        self.create_and_show_details_area()
        self.perform_search(str(pokemon_id))

    def create_and_show_details_area(self):
        # Se a área de detalhes já existe, apenas a mostramos
        if hasattr(self, 'detail_frame'):
            # Se já foi criado, só garantimos que está visível
            if not self.detail_frame.winfo_ismapped():
                self.detail_frame.grid()
        else:
            # Cria a área de detalhes (Nova Coluna 2)
            self.detail_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray15"), corner_radius=10, border_width=2, border_color="#FFCB05")
            self.detail_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 20), pady=20)
            self.detail_frame.grid_columnconfigure(0, weight=1)
            self.detail_frame.grid_rowconfigure(1, weight=1)

            ctk.CTkLabel(self.detail_frame, text="DETALHES DO POKÉMON", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

            # Placeholder para a imagem do Pokémon (ID: detail_image_label)
            self.detail_image_label = ctk.CTkLabel(self.detail_frame, text="", fg_color="transparent")
            self.detail_image_label.grid(row=0, column=0, sticky="n", pady=(40, 0))

            # Placeholder para os detalhes do Pokémon (ID: detail_text)
            self.detail_text = ctk.CTkTextbox(self.detail_frame, wrap="word", 
                                              font=("Consolas", 14), 
                                              state="disabled") 
            self.detail_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
            
            # Ajusta o grid do pai para acomodar a nova coluna
            self.grid_columnconfigure(2, weight=0) # Detalhes não crescem
            self.grid_columnconfigure(1, weight=1) # Main Content volta a crescer

    def load_pokemon_names(self):
        try:
            conn = get_db_connection()
            names = conn.execute("SELECT nome FROM pokemons ORDER BY id ASC").fetchall()
            conn.close()
            return [name['nome'].lower() for name in names]
        except Exception:
            return [] 

    def fetch_pokemon_data(self, search_term):
        conn = get_db_connection()
        data = None
        try:
            if search_term.isdigit():
                where_clause = f"id = {search_term}"
            else:
                where_clause = f"LOWER(nome) = '{search_term.lower()}'"

            main_data = conn.execute(f"""
                SELECT id, nome, tipos, stats_base, sprite_url, descricao 
                FROM pokemons
                WHERE {where_clause}
            """).fetchone()

            if main_data:
                data = {
                    'id': main_data['id'],
                    'name': main_data['nome'],
                    'types': json.loads(main_data['tipos']),
                    'stats': json.loads(main_data['stats_base']),
                    'sprite_url': main_data['sprite_url'],
                    'description': main_data['descricao'],
                }
            
            return data

        except Exception as e:
            return None
        finally:
            conn.close()

    def perform_search_from_entry(self):
        search_term = self.search_entry.get().lower().strip()
        self.autocomplete_listbox.place_forget()
        if search_term:
            # Certifica-se de que a área de detalhes está visível antes de buscar
            self.create_and_show_details_area() 
            self.perform_search(search_term)

    def perform_search(self, search_term):
        data = self.fetch_pokemon_data(search_term)
        
        if data:
            self.update_details(data)
            self.load_pokemon_image_for_details(data['sprite_url']) 
        else:
            self.show_error(f"Erro: Pokémon '{search_term}' não encontrado no banco de dados.")

    def update_details(self, data):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")

        pokemon_name = data['name'].upper()
        pokemon_id = data['id']
        types = [t.capitalize() for t in data['types']]
        stats = data['stats']
        
        detail_output = (
            f"ID: #{pokemon_id:03}\n"
            f"NOME: {pokemon_name}\n"
            f"TIPO(S): {', '.join(types)}\n"
            f"DESCRIÇÃO:\n  {data['description']}\n\n"
            "STATUS BASE:\n"
        )
        
        for stat_name, base_stat in stats.items():
            stat_name_clean = stat_name.replace('-', ' ').upper()
            detail_output += f"  {stat_name_clean}: {base_stat}\n"

        self.detail_text.insert("end", detail_output)
        self.detail_text.configure(state="disabled")

    def load_pokemon_image_for_details(self, url):
        # Faz o download ou usa o cache para a imagem grande do painel de detalhes
        # Nota: Idealmente, esta função também deveria checar o caminho local para consistência.
        try:
            image_response = requests.get(url, timeout=5)
            image_response.raise_for_status()
            
            image_data = Image.open(BytesIO(image_response.content)).convert("RGBA")
            target_size = 200 # Tamanho maior para a tela de detalhes
            resized_image = image_data.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Salva a imagem no atributo do objeto para garantir que não desrenderize
            self.detail_pokemon_img = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(target_size, target_size))
            
            self.detail_image_label.configure(image=self.detail_pokemon_img, text="")
            self.detail_image_label.image = self.detail_pokemon_img
        except Exception:
            self.detail_image_label.configure(image=None, text="❌ Imagem não disponível", font=("Arial", 16))


    def show_error(self, message):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end", f"ERRO NA BUSCA:\n\n{message}")
        self.detail_text.configure(state="disabled")
        if hasattr(self, 'detail_image_label'):
            self.detail_image_label.configure(image=None, text="❌", font=("Arial", 30))

    def autocomplete_handler(self, event):
        current_text = self.search_entry.get().lower()
        
        self.autocomplete_listbox.delete(0, tk.END)
        
        if not current_text:
            self.autocomplete_listbox.place_forget()
            return
        
        matches = [name for name in self.pokemon_names if name.startswith(current_text)]
        
        if matches:
            for match in matches:
                self.autocomplete_listbox.insert(tk.END, match.capitalize())
            
            self.autocomplete_listbox.lift()
            self.autocomplete_listbox.place(relx=0, rely=1.0, relwidth=1, y=5)
            
            if event.keysym == 'Return':
                if self.autocomplete_listbox.curselection():
                    self.select_autocomplete(None) 
                else:
                    self.perform_search_from_entry()
                self.autocomplete_listbox.place_forget()
        else:
            self.autocomplete_listbox.place_forget()

    def select_autocomplete(self, event):
        try:
            selected_index = self.autocomplete_listbox.curselection()[0]
            selected_pokemon = self.autocomplete_listbox.get(selected_index)
        except IndexError:
            return

        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, selected_pokemon.lower())
        
        self.autocomplete_listbox.place_forget()
        
        self.perform_search_from_entry()