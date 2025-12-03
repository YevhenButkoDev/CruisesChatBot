from datetime import datetime

import requests

from src.agent_tools.city_tool import get_city_id
from src.agent_tools.country_tool import get_country_id
from src.agent_tools.cruise_type_tool import get_type_id
from src.agent_tools.ports_tool import get_port_id
from src.agent_tools.response_parser import extract_cruise_summary
from src.agent_tools.rivers_tool import get_river_id
import os


def search_cruises(
        cruise_type: str = None,
        rivers: list[str] = None,
        port_from: str = None,
        port_to: str = None,
        cities_to_visit: list[str] = None,
        country_from: str = None,
        country_to: str = None,
        time_duration: int = None,
        time_from_date: str = None,
        time_to_date: str = None,
        price_min: int = None,
        price_max: int = None
):
    """
    Search for cruises using advanced filtering criteria.
    :param cruise_type: Type of cruise to search for, sea/river
    :param rivers: List of river names for river cruises
        - Examples: ["Rhine", "Danube", "Seine", "Nile"]
    :param port_from: Departure port/city name
        - Examples: "Barcelona", "Miami", "Amsterdam"
    :param port_to: Arrival port/city name
        - Examples: "Rome", "Venice", "Southampton"
    :param cities_to_visit: List of cities/ports the cruise should visit
        - Examples: ["Naples", "Santorini", "Dubrovnik"]
    :param country_from: Departure country name
        - Examples: "Spain", "USA", "Germany", "United Kingdom"
    :param country_to: Destination country name
        - Examples: "Italy", "Greece", "Norway"
    :param time_duration: Cruise duration category (0-6)
        - 0: 1-2 days
        - 1: 3-5 days  
        - 2: 6-9 days
        - 3: 10-14 days
        - 4: 15-35 days
        - 5: 36-99 days
        - 6: 100+ days
    :param time_from_date: Earliest departure date
        - Format: "YYYY-MM-DD" (e.g., "2025-06-15")
    :param time_to_date: Latest departure date
        - Format: "YYYY-MM-DD" (e.g., "2025-08-31")
    :param price_min: Minimum price in specified currency
    :param price_max: Maximum price in specified currency
    :return Formatted cruise search results
    """
    search_parameters = []
    if cruise_type is not None:
        search_parameters.append(_convert_to_request_params("cruiseType[]", get_type_id(cruise_type)))

    if rivers is not None:
        search_parameters.append(_convert_to_request_params("rivers[]", [get_river_id(r) for r in rivers]))

    if port_from is not None:
        search_parameters.append(_convert_to_request_params("location.ports[]", get_port_id(port_from)))

    if port_to is not None:
        search_parameters.append(_convert_to_request_params("location.lastPorts[]", get_port_id(port_to)))

    if cities_to_visit is not None:
        search_parameters.append(_convert_to_request_params("location.cities[]", [get_city_id(c) for c in cities_to_visit]))

    if country_from is not None:
        search_parameters.append(_convert_to_request_params("location.countries[]", get_country_id(country_from)))

    if country_to is not None:
        search_parameters.append(_convert_to_request_params("location.countriesTo[]", get_country_id(country_to)))

    if time_from_date is not None:
        search_parameters.append(_convert_to_request_params("time.fromDate", time_from_date))
    else:
        search_parameters.append(_convert_to_request_params("time.fromDate", datetime.now().strftime("%Y-%m-%d")))

    if time_to_date is not None:
        search_parameters.append(_convert_to_request_params("time.toDate", time_to_date))

    if time_duration is not None:
        search_parameters.append(_convert_to_request_params("time.durations", time_to_date))

    if price_min is not None:
        search_parameters.append(_convert_to_request_params("price.price", price_min))

    if price_max is not None:
        search_parameters.append(_convert_to_request_params("price.maxPrice", price_max))

    search_parameters = [x for x in search_parameters if x is not None]

    base_url = os.getenv('CRUISE_API_BASE_URL', 'http://uat.center.cruises') + '/api/chatbot/cruises/batch-data?'
    search_url = base_url + '&'.join(search_parameters)
    print(search_url)

    response = requests.get(search_url).json()
    return extract_cruise_summary(response['data'])


def _convert_to_request_params(param_name: str, values):
    """Convert values into request parameters format."""
    if values is None:
        return None

    if isinstance(values, list):
        # Handle list of values: param[]=value1&param[]=value2
        if not values:
            return None
        # Filter out None values
        return "&".join([f"{param_name}={v}" for v in values if v is not None])
    else:
        # Handle single value: param=value
        return f"{param_name}={values}"

search_cruises()