from deep_translator import GoogleTranslator
from functools import lru_cache

@lru_cache(maxsize=512)
def translate_to_portuguese(text):
    if not text:
        return text
    
    try:
        translator = GoogleTranslator(source='en', target='pt')
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Erro ao traduzir: {e}")
        return text

def translate_ability_description(description, language='pt'):
    if language == 'pt' and description and description != "Descrição não disponível":
        return translate_to_portuguese(description)
    return description
