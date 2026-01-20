import requests
import logging
import os

logger = logging.getLogger(__name__)

def get_company_id(company_name: str):
    """Get company ID by name."""
    try:
        companies = _get_companies_data()
        if not companies:
            return None

        company_lower = company_name.lower().strip()
        
        for company in companies:
            if company_lower == company['text'].lower():
                return company['id']

        return None

    except Exception as e:
        logger.error(f"Error in get_company_id: {e}")
        return None

def _get_companies_data():
    """Load companies data from API."""
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        response = requests.get(base_url + "/api/filter/cruise-companies.json")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error in _get_companies_data: {e}")
        return []

if __name__ == "__main__":
    print(get_company_id("test"))
