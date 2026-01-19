import os
import requests


def calculate_price(
        range_id: int,
        adults_count: int,
        children_count: int
):
    """
    Calculate exact cruise price
    :param range_id: cruise date range id
    :param adults_count: amount of adults for booking
    :param children_count: amount of children for booking
    """
    if range_id is None:
        return -1

    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'https://center.cruises')
        price_url = base_url + f"/api/chatbot/cruises/prices?cruiseDateRangeId={range_id}&adultCount={adults_count}&childCount={children_count}"
        response = requests.get(price_url)

        data = response.json()
        return data['data']
    except Exception as e:
        print(e)
        return -1


if __name__ == "__main__":
    print(calculate_price(30891534, 3, 0))