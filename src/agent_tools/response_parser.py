from datetime import datetime

from src.agent_tools.agent_tools import build_cruise_url
from src.transformation.semantic import get_descriptive_text_and_meta


def extract_cruise_summary(data):
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
        transformed = transform_data(cruise_record)
        batch_data.append(transformed)
    return batch_data

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

def transform_data(cruise_data):
    """
    Orchestrates the data cleaning, translation, and semantic transformation for a single cruise.
    """
    if cruise_data.get("date_and_price_info", {}) is None:
        return None

    data_and_price_info = cruise_data.get("date_and_price_info", {}).get(cruise_data.get("cruise_id"))
    if len(data_and_price_info.get("dates", [])) == 0:
        return None

    descriptive_text = get_descriptive_text_and_meta(cruise_data)

    return {
        "cruise_id": cruise_data["cruise_id"],
        "text_chunk": descriptive_text["text"],
        "metadata": {
            "cruise_id": cruise_data["cruise_id"],
            "ufl": cruise_data["ufl"],
            "cities": descriptive_text["meta"]["cities"],
            "city_countries": descriptive_text["meta"]["city_countries"],
            "rivers": descriptive_text["meta"]["rivers"],
            "sea_cruise": descriptive_text["meta"]["rivers"] == "",
            "min_price": data_and_price_info.get("prices", [])[0],
            "max_price": data_and_price_info.get("prices", [])[1],
            "dates": ", ".join(data_and_price_info.get("dates", [])),
            "ranges": ", ".join(data_and_price_info.get("ranges", [])),
            "website_urls": ", ".join([build_cruise_url(r, cruise_data["ufl"]) for r in data_and_price_info.get("ranges", [])])
        }
    }
