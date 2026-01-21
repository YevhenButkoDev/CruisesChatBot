import requests
import logging
import os

logger = logging.getLogger(__name__)

def get_vessel_id(vessel_name: str):
    """Get vessel ID by name."""
    try:
        vessels = _get_vessels_data()
        if not vessels:
            return None

        vessel_lower = vessel_name.lower().strip()
        
        for vessel in vessels:
            if vessel_lower == vessel['text'].lower():
                return vessel['id']

        return None

    except Exception as e:
        logger.error(f"Error in get_vessel_id: {e}")
        return None

def _get_vessels_data():
    """Load vessels data from API."""
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        response = requests.get(base_url + "/api/filter/cruise-vessels.json")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error in _get_vessels_data: {e}")
        return []

if __name__ == "__main__":
    print(get_vessel_id("Celebrity Ascent"))
