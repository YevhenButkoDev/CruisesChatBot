import requests
import logging
import os

logger = logging.getLogger(__name__)

# River name mappings: English -> Russian alternatives
RIVER_MAPPINGS = {
    # Major rivers with common alternative names
    'danube': ['Дунай'],
    'rhine': ['Рейн'],
    'rhone': ['Рона'],
    'seine': ['Сена'],
    'elbe': ['Эльба'],
    'nile': ['Нил'],
    'mekong': ['Меконг'],
    'ganges': ['Ганг'],
    'amazon': ['Мараньон', 'Укаяли'],
    'douro': ['Дору'],
    'loire': ['Луара'],
    'main': ['Майн'],
    'moselle': ['Мозель'],
    'neckar': ['Неккар'],
    'po': ['По'],
    'saar': ['Саар'],
    'saone': ['Сона'],
    'oder': ['Одра'],
    'garonne': ['Гаронна', 'Горонна'],
    'dordogne': ['Дордонь'],
    'gironde': ['Жиро́нда'],
    'guadalquivir': ['Гвадалквивир'],
    'havel': ['Хафель'],
    'marne rhine canal': ['Канал Марна-Рейн'],
    'belgian canals': ['Каналы Бельгии'],
    'dutch canals': ['Каналы Голландии'],
    'holland canals': ['Каналы Голландии'],
    'netherlands canals': ['Каналы Голландии'],
    'venetian lagoon': ['Венецианская лагуна'],
    'venice lagoon': ['Венецианская лагуна'],
    'black sea': ['Черное море'],
    'ucayali': ['Укаяли'],
    'maranon': ['Мараньон'],
}

def get_river_id(river_name: str):
    """Get river ID by name with alternative name mapping."""
    try:
        rivers = _get_rivers_data()
        if not rivers:
            return None

        river_lower = river_name.lower().strip()
        
        # Get Russian alternatives for this river
        russian_names = RIVER_MAPPINGS.get(river_lower, [])
        
        # Try exact matches with Russian alternatives
        for russian_name in russian_names:
            for river in rivers:
                if russian_name.lower() == river['text'].lower():
                    return river['id']
        
        # Fallback: translate input and try matching
        river_ru = _translate_to_russian(river_name)
        for river in rivers:
            if river_ru.lower() in river['text'].lower():
                return river['id']

        return None

    except Exception as e:
        logger.error(f"Error in get_river_id: {e}")
        return None

def _translate_to_russian(text: str) -> str:
    """Translate text to Russian using Google Translate API."""
    try:
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ru&dt=t&q={encoded_text}"
        
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result[0][0][0] if result and result[0] and result[0][0] else text
        return text
    except:
        return text

def _get_rivers_data():
    """Load rivers data from API or cache."""
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        response = requests.get(base_url + "/api/filter/cruise-rivers.json")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error in _get_rivers_data: {e}")
        return []

if __name__ == "__main__":
    print(get_river_id("Rhine"))
