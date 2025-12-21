import requests
import logging
import os

logger = logging.getLogger(__name__)

# Direction/Region name mappings: English -> Russian alternatives
DIRECTION_MAPPINGS = {
    # Regions and directions
    'australia': ['Австралия / Новая Зеландия'],
    'new zealand': ['Австралия / Новая Зеландия'],
    'australia new zealand': ['Австралия / Новая Зеландия'],
    'asia': ['Азия'],
    'alaska': ['Аляска'],
    'bahamas': ['Багамы'],
    'bermuda': ['Бермуды'],
    'bermudas': ['Бермуды'],
    'europe': ['Европа'],
    'indian ocean': ['Индийский океан'],
    'caribbean': ['Карибы'],
    'caribbeans': ['Карибы'],
    'world cruise': ['Кругосветные круизы'],
    'world cruises': ['Кругосветные круизы'],
    'around the world': ['Кругосветные круизы'],
    'cuba': ['Куба / Доминикана'],
    'dominican republic': ['Куба / Доминикана'],
    'cuba dominican': ['Куба / Доминикана'],
    'uae': ['ОАЭ / Персидский залив'],
    'persian gulf': ['ОАЭ / Персидский залив'],
    'emirates': ['ОАЭ / Персидский залив'],
    'united arab emirates': ['ОАЭ / Персидский залив'],
    'panama canal': ['Панамский канал'],
    'panama': ['Панамский канал'],
    'usa': ['США / Канада / Мексика'],
    'canada': ['США / Канада / Мексика'],
    'mexico': ['США / Канада / Мексика'],
    'united states': ['США / Канада / Мексика'],
    'america': ['США / Канада / Мексика'],
    'north america': ['США / Канада / Мексика'],
    'northern europe': ['Северная Европа'],
    'north europe': ['Северная Европа'],
    'scandinavia': ['Северная Европа'],
    'baltic': ['Северная Европа'],
    'mediterranean': ['Средиземное море'],
    'mediterranean sea': ['Средиземное море'],
    'pacific ocean': ['Тихий океан'],
    'pacific': ['Тихий океан'],
    'pacific cruises': ['Тихоокеанские круизы'],
    'transatlantic': ['Трансатлантические круизы'],
    'transatlantic cruises': ['Трансатлантические круизы'],
    'trans atlantic': ['Трансатлантические круизы'],
    'south america': ['Южная Америка / Антарктида'],
    'antarctica': ['Южная Америка / Антарктида'],
    'antarctic': ['Южная Америка / Антарктида'],
    'south america antarctica': ['Южная Америка / Антарктида'],
}

def get_direction_id(direction_name: str):
    """Get direction ID by name with alternative name mapping."""
    try:
        directions = _get_directions_data()
        if not directions:
            return None

        direction_lower = direction_name.lower().strip()
        
        # Get Russian alternatives for this direction
        russian_names = DIRECTION_MAPPINGS.get(direction_lower, [])
        
        # Try exact matches with Russian alternatives
        for russian_name in russian_names:
            for direction in directions:
                if russian_name.lower() == direction['text'].lower():
                    return direction['id']
        
        # Fallback: translate input and try matching
        direction_ru = _translate_to_russian(direction_name)
        for direction in directions:
            if direction_ru.lower() in direction['text'].lower():
                return direction['id']

        return None

    except Exception as e:
        logger.error(f"Error in get_direction_id: {e}")
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

def _get_directions_data():
    """Load directions data from API or cache."""
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        response = requests.get(base_url + "/api/filter/cruise-categories.json")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error in _get_directions_data: {e}")
        return []

if __name__ == "__main__":
    print(get_direction_id("Mediterranean"))
