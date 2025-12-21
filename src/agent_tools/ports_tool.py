import requests
import logging
import os

logger = logging.getLogger(__name__)

def get_port_id(city_name: str):
    """Get city ID by translating to Russian and searching."""
    try:
        cities = _get_ports_data()
        if not cities:
            return None

        # Try direct translation using requests to Google Translate API
        import urllib.parse

        encoded_text = urllib.parse.quote(city_name)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ru&dt=t&q={encoded_text}"

        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            city_ru = result[0][0][0] if result and result[0] and result[0][0] else city_name
        else:
            city_ru = city_name

        # Search in cities
        for city in cities:
            if city_ru.lower() in city['text'].lower() or city['text'].lower() in city_ru.lower():
                return city['id']

        return None

    except Exception as e:
        logger.error(f"Error in get_port_id: {e}")
        return None


def _get_ports_data():
    """Load cities data from API or cache."""
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        response = requests.get(base_url + "/api/filter/cruise-ports.json")

        data = response.json()
        return data
    except Exception as e:
        logger.error(f"Error in _get_ports_data: {e}")


if __name__ == "__main__":
    print(get_port_id("Arles"))