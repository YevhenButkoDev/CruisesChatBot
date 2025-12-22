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
        sergey_api_key = os.getenv('SERGEY_API', 'cruise_prc_9F7aKQ2mWJ8xP4D6C3LhZBvYtR5eNUs')
        response = requests.get(f"https://unfossiliferous-terry-drolly.ngrok-free.dev/price?url=https://center.cruises/cruise-booking/msc/{range_id}&adults={adults_count}&children={children_count}&api_key={sergey_api_key}").json()
        return response
    except Exception:
        return -1



if __name__ == "__main__":
    print(calculate_price(30936434,1, 2, 0))