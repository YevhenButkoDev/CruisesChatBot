import logging
import time
import requests
import os
from datetime import date

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def get_current_date() -> str:
    """Get current date in ISO format."""
    try:
        return date.today().isoformat()
    except Exception:
        return "no data"


def build_cruise_url(range, ufl):
    base_url = os.getenv('CRUISE_BASE_URL', 'http://uat.center.cruises/cruise-')
    return f"{base_url}{range}-{ufl}"

def find_cruise_info(cruise_id: str, desired_date: date = date.today()):
    """
    Get detailed cruise information by ID.
    :param cruise_id: cruise unique identifier
    :param desired_date: desired date to search cruise info, all info will be found only after this specified date
    """
    start_time = time.time()
    
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'http://uat.center.cruises')
        url = f"{base_url}/en/api/chatbot/cruises/batch-data?cruiseId[]={cruise_id}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('data'):
            return "no data"
        
        # Find first cruise with date after desired_date
        cruise_data = None
        desired_date_str = desired_date.strftime('%Y-%m-%d') if desired_date else None
        
        if desired_date_str:
            for cruise in data['data']:
                begin_date = cruise.get('cruiseDateRangeInfoJson', {}).get('dateRange', {}).get('begin_date')
                if begin_date and begin_date >= desired_date_str:
                    cruise_data = cruise
                    break
        
        if not cruise_data:
            cruise_data = data['data'][0]
        cruise_info = cruise_data.get('cruiseInfoJson', {}).get('cruise', {})
        range_info = cruise_data.get('cruiseDateRangeInfoJson', {})
        vessel_info = cruise_data.get('vesselInfoJson', {}).get('vessel', {})
        cabins_info = cruise_data.get('vesselInfoJson', {}).get('cabinCategories', {})

        min_price_info = range_info.get('minPriceInfo', [])
        cabin_prices = [item for item in min_price_info if item.get('currency_id') == 2]

        cabins_info_result = []
        for c in cabin_prices:
            try:
                id = c.get('cabin_category_id')
                cabin_info = [info for info in cabins_info if info.get('category', {}).get('cabin_category_id') == id]
                cabins_info_result.append({
                    'price': c.get('price_value'),
                    'description': cabin_info[0].get('category', {}).get('description')
                })
            except Exception:
                cabins_info_result.append({
                    'minimal_price': 'none',
                    'description': 'none'
                })

        # Extract relevant information
        result = {
            'cruise_name': cruise_info.get('name_i18n', {}).get('en', cruise_info.get('name', '')),
            'vessel_name': vessel_info.get('name', ''),
            'vessel_dressing': vessel_info.get('dress', ''),
            'vessel_food': vessel_info.get('food', ''),
            'vessel_activities': vessel_info.get('activities', ''),
            'vessel_for_children': vessel_info.get('for_children', ''),
            'cabins_info': cabins_info_result,
            'min_price': range_info.get('minPrice').get('2'),
            'website': build_cruise_url(cruise_data.get('cruiseDateRangeId'), cruise_data.get('ufl')),
            'itineraries': []
        }
        
        # Extract itinerary information
        for itinerary in cruise_data.get('cruiseInfoJson', {}).get('itineraries', []):
            city = itinerary.get('city', {})
            itinerary_info = itinerary.get('itinerary', {})
            result['itineraries'].append({
                'day': itinerary_info.get('day'),
                'city_name': city.get('name_i18n', {}).get('en', city.get('name', '')),
                'country_name': city.get('country_name_i18n', {}).get('en', city.get('country_name', '')),
                'arrival_time': itinerary_info.get('arrival_time'),
                'departure_time': itinerary_info.get('departure_time')
            })
        
        elapsed = time.time() - start_time
        print(f"⏱️ API cruise info: {elapsed:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error finding cruise info for ID {cruise_id}: {str(e)}")
        return "no data"


if __name__ == "__main__":
    load_dotenv()
    find_cruise_info(cruise_id="1249652")