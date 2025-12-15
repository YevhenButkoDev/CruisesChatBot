import os
import requests

from src.agent_tools.playwright_scraper import scrape_custom_dropdown


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
        return scrape_custom_dropdown(base_url + '/cruise-booking/' + str(range_id), adults_count, children_count)
    except Exception:
        return -1


if __name__ == "__main__":
    print(calculate_price(30948807, 1, 3, 1))