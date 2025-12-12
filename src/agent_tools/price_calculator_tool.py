import os
import requests


def calculate_price(
        range_id: int,
        cabin_id: int,
        adults_count: int,
        children_count: int
):
    """
    Calculate exact cruise price
    :param range_id: cruise date range id
    :param cabin_id: desired cabin to book
    :param adults_count: amount of adults for booking
    :param children_count: amount of children for booking
    """
    if range_id is None or cabin_id is None:
        return -1

    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        response = requests.get(base_url + f"/api/chatbot/cruises/prices?cruiseDateRangeId={range_id}&cabinCategoryId={cabin_id}&adultCount={adults_count}&childCount={children_count}")

        data = response.json()
        return data['data'][0]['price']
    except Exception:
        return -1

