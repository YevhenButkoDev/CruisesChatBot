import logging
import time
import requests
import os
from datetime import date, timedelta
from typing import List, Tuple, Optional

from src.vector_db.query import query_chroma_db
from src.util.date_utils import validate_and_correct_date_range
from src.util.cruise_utils import parse_cruise_results
from src.util.sqlite_storage import CruiseDataStorage

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

def filter_cruises_by_date_range(date_from: date, date_to: date) -> List[str]:
    """Filter enabled cruise IDs by date range."""
    start_time = time.time()
    
    try:
        # Convert dates to yyyyMM format
        date_start = int(date_from.strftime("%Y%m"))
        date_end = int(date_to.strftime("%Y%m"))
        
        storage = CruiseDataStorage()
        cruise_ids = storage.get_cruise_ids_by_date_range(date_start, date_end)
        
        elapsed = time.time() - start_time
        print(f"⏱️ DB filter cruises: {elapsed:.2f}s")
        
        return cruise_ids
        
    except Exception as e:
        logger.error(f"❌ Database error in filter_cruises_by_date_range: {str(e)}")
        return []


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
        
        # Extract relevant information
        result = {
            'cruise_name': cruise_info.get('name_i18n', {}).get('en', cruise_info.get('name', '')),
            'vessel_name': vessel_info.get('name', ''),
            'vessel_dressing': vessel_info.get('dress', ''),
            'vessel_food': vessel_info.get('food', ''),
            'vessel_activities': vessel_info.get('activities', ''),
            'vessel_for_children': vessel_info.get('for_children', ''),
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


def find_relevant_cruises(user_question: str, date_from: str, date_to: str) -> str:
    """
    Find cruises relevant to user query within date range.
    
    :param user_question: English natural-language search query
    :param date_from: Start date in ISO format 'YYYY-MM-DD'
    :param date_to: End date in ISO format 'YYYY-MM-DD'
    :return: Parsed cruise results or "no data"
    """
    start_time = time.time()
    
    try:
        # Validate and correct date range
        date_from_corrected, date_to_corrected, is_valid = validate_and_correct_date_range(date_from, date_to)
        
        # Filter by date if valid range provided
        cruise_ids = []
        if is_valid:
            cruise_ids = filter_cruises_by_date_range(date_from_corrected, date_to_corrected)

        # Query vector database
        vector_start = time.time()
        results = query_chroma_db(query_text=user_question, cruise_ids=cruise_ids)
        vector_elapsed = time.time() - vector_start
        print(f"⏱️ Vector DB query: {vector_elapsed:.2f}s")
        
        # Parse and format results
        parsed_results = parse_cruise_results(results)

        total_elapsed = time.time() - start_time
        print(f"⏱️ Find relevant cruises: {total_elapsed:.2f}s")
        
        return parsed_results
        
    except Exception as e:
        logger.error(f"❌ Error finding relevant cruises: {str(e)}")
        return "no data"


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    print(find_cruise_info('1104706', desired_date=date.fromisoformat("2026-07-10")))