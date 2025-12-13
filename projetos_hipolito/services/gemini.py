import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv 

load_dotenv() 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) 
MODEL_ID = "gemini-2.0-flash-lite" 

SYSTEM_INSTRUCTION = (
    "Você é a Enfermeira Joy, uma assistente de IA especializada EXCLUSIVAMENTE em Pokémon. "
    "Suas respostas devem ser SEMPRE breves, diretas e focadas no universo Pokémon. "
    "Ignore perguntas que não sejam sobre Pokémon. "
    "Você deve ser capaz de: montar builds de Pokémon (com 4 ataques), recomendar ataques, e sugerir times de 6 Pokémon. "
    "Priorize informações oficiais do universo Pokémon (jogos, TCG, lore)."
)

generation_config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.7, 
    max_output_tokens=10000 
)

def get_pokemon_agent_response(prompt: str, history: list = None) -> str:
    contents = [
        types.Content(
            role="user", 
            parts=[types.Part.from_text(text=prompt)] 
        )
    ]

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents, 
            config=generation_config
        )
        
        if response.candidates and response.candidates[0].finish_reason == 'SAFETY':
             return "Desculpe, não posso responder a essa pergunta."
        
        return response.text.strip()
        
    except APIError as e:
        print(f"Erro na API Gemini: {e}")
        return "Erro de comunicação com a IA. Tente novamente."
        
    except Exception as e:
        print(f"Erro inesperado no Gemini: {e}")
        return "Desculpe, a Enfermeira Joy está ocupada no Centro Pokémon. Tente novamente mais tarde."