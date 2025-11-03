import logging
import requests
from datetime import datetime
from src.util.sqlite_storage import CruiseDataStorage

logging.basicConfig(level=logging.INFO)


def get_enabled_cruise_ids():
    """Fetches all enabled cruise IDs from the API."""
    response = requests.get("http://uat.center.cruises/api/chatbot/cruises/enabled-ids/")
    response.raise_for_status()
    return response.json()


def persist_cruise_data_in_batches(cruise_ids, batch_size=1):
    """Fetches cruise data in batches from the API and persists to SQLite."""
    storage = CruiseDataStorage()
    
    for i in range(0, len(cruise_ids), batch_size):
        batch_ids = cruise_ids[i:i + batch_size]
        params = [f"cruiseId[]={cruise_id}" for cruise_id in batch_ids]
        url = f"http://uat.center.cruises/en/api/chatbot/cruises/batch-data?{'&'.join(params)}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data']
        
        grouped = {}
        for item in data:
            cruise_id = item['cruiseInfoJson']['cruise']['cruise_id']
            if cruise_id not in grouped:
                grouped[cruise_id] = {
                    'ufl': item['ufl'],
                    'cruiseInfoJson': item['cruiseInfoJson'],
                    'cruiseDateRangeInfoJson': []
                }
            grouped[cruise_id]['cruiseDateRangeInfoJson'].append(item['cruiseDateRangeInfoJson'])
        
        batch_data = []
        for cruise_data in grouped.values():
            cruise_record = {
                "id": cruise_data['cruiseInfoJson']['cruise']['cruise_id'],
                "cruise_id": cruise_data['cruiseInfoJson']['cruise']['cruise_id'],
                "ufl": cruise_data['ufl'],
                "cruise_info": cruise_data['cruiseInfoJson'],
                "date_and_price_info": get_date_and_price_info(cruise_data['cruiseDateRangeInfoJson']),
            }
            batch_data.append(cruise_record)
        
        storage.save_raw_cruises(batch_data)
        logging.info(f"Processed batch: {i} of {len(cruise_ids)}")


def get_date_and_price_info(data):
    """Fetches date and price information from the mv_cruise_date_range_info materialized view."""

    date_and_price_info = {}
    for row in data:
        cruise_id = row['dateRange']['cruise_id']
        cruise_date_range_id = row['dateRange']['cruise_date_range_id']

        if cruise_id not in date_and_price_info:
            date_and_price_info[cruise_id] = {"dates": [], "prices": [0, 0], "ranges": []}

        if row.get("minPrice") is not None:
            price = row.get("minPrice", {}).get("2")
            prev_min = date_and_price_info[cruise_id]["prices"][0]
            prev_max = date_and_price_info[cruise_id]["prices"][1]

            if price and (prev_min == 0 or price < prev_min):
                date_and_price_info[cruise_id]["prices"][0] = price
            elif price and price > prev_max:
                date_and_price_info[cruise_id]["prices"][1] = price

        date_range = row.get("dateRange")
        if date_range and date_range.get("begin_date") and date_range.get("end_date"):
            begin_date = datetime.fromisoformat(date_range["begin_date"].replace('Z', '+00:00'))
            is_valid = begin_date.date() >= datetime.now().date()
            if is_valid is True:
                date_and_price_info[cruise_id]["dates"].append(begin_date.date().strftime("%Y%m"))
                date_and_price_info[cruise_id]["ranges"].append(str(cruise_date_range_id))

    return date_and_price_info


def extract_data():
    """Orchestrates the data extraction process and saves the final data to SQLite."""
    logging.info("Starting data extraction")
    enabled_cruise_ids = get_enabled_cruise_ids()
    logging.info(f"Found {len(enabled_cruise_ids)} enabled cruises")

    persist_cruise_data_in_batches(enabled_cruise_ids)
    logging.info("Data extraction completed")


if __name__ == "__main__":
    extract_data()
