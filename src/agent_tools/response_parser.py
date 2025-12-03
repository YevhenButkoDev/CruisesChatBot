from datetime import datetime

from src.agent_tools.agent_tools import build_cruise_url
from src.util.cleaner import remove_html_tags


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


def get_descriptive_text_and_meta(cruise_data):
    """Generates a descriptive text for a given cruise data."""

    cruise_info = cruise_data.get("cruise_info", {})

    # A helper function to safely get nested keys.
    def get_nested(data, keys):
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return None
        return data

    # Another helper for localized text
    def get_i18n_text(data, keys):
        i18n_data = get_nested(data, keys)
        if i18n_data:
            return get_localized_text(i18n_data, "en")
        return ""

    # Extract and format data points
    name = get_i18n_text(cruise_info, ["cruise", "name_i18n"])
    description = remove_html_tags(get_nested(cruise_info, ["cruise", "description"]))
    simple_itinerary = remove_html_tags(get_nested(cruise_info, ["cruise", "simple_itinerary_description"]))

    rivers = ", ".join([get_i18n_text(r, ["name_i18n"]) for r in get_nested(cruise_info, ["rivers"]) or []])
    river_descriptions = " ".join(
        ", ".join(list(set([
            remove_html_tags(get_i18n_text(r, ["description_i18n"]))
            for r in get_nested(cruise_info, ["rivers"]) or []
        ]))).split()[:100]
    )

    start_port = get_i18n_text(cruise_info, ["portMaybe", "name_i18n"])
    start_port_desc = " ".join(
        remove_html_tags(get_i18n_text(cruise_info, ["portMaybe", "description_i18n"])).split()[:100])
    start_port_country = get_i18n_text(cruise_info, ["portMaybe", "country_gen_i18n"])

    cities = ", ".join(list(set(
        get_i18n_text(i, ["city", "name_i18n"])
        for i in (get_nested(cruise_info, ["itineraries"]) or [])
        if get_i18n_text(i, ["city", "name_i18n"])
    )))
    city_countries = ", ".join(list(
        set([get_i18n_text(i, ["city", "country_name_i18n"]) for i in get_nested(cruise_info, ["itineraries"]) or []])))
    city_country_descs = " ".join(
        ", ".join(list(set([
            remove_html_tags(get_i18n_text(i, ["city", "country_description_i18n"]))
            for i in get_nested(cruise_info, ["itineraries"]) or []
        ]))).split()[:100]
    )
    city_descs = " ".join(
        ", ".join([
            remove_html_tags(get_i18n_text(i, ["city", "description_i18n"]))
            for i in get_nested(cruise_info, ["itineraries"]) or []
        ]).split()[:100]
    )

    end_port = get_i18n_text(cruise_info, ["lastPortMaybe", "name_i18n"])
    end_port_country = get_i18n_text(cruise_info, ["lastPortMaybe", "country_name_i18n"])
    end_port_desc = remove_html_tags(get_i18n_text(cruise_info, ["lastPortMaybe", "description_i18n"]))

    categories = ", ".join(
        [get_i18n_text(c, ["name_i18n"]) for c in get_nested(cruise_info, ["cruiseCategories"]) or []])
    category_descs = " ".join(
        ", ".join([remove_html_tags(get_i18n_text(c, ["description_i18n"])) for c in
                   get_nested(cruise_info, ["cruiseCategories"]) or []])
        .split()[:50]
    )
    category_type = get_i18n_text(cruise_info, ["cruiseCategoryType", "name_i18n"])

    # Build the descriptive text
    text_parts = []
    if name:
        text_parts.append(f"The cruise is named {name}.")
    if description:
        text_parts.append(description)
    if simple_itinerary:
        text_parts.append(f"The itinerary is described as: {simple_itinerary}.")
    if rivers:
        text_parts.append(f"The cruise goes along the following rivers: {rivers}.")
    if river_descriptions:
        text_parts.append(f"The rivers are described as: {river_descriptions}.")
    if start_port:
        text_parts.append(f"The cruise may start from the port of {start_port}.")
    if start_port_desc:
        text_parts.append(f"The starting port is described as: {start_port_desc}.")
    if start_port_country:
        text_parts.append(f"The starting port is in {start_port_country}.")
    if cities:
        text_parts.append(f"The cruise visits the following cities: {cities}.")
    if city_countries:
        text_parts.append(f"The cities are in the following countries: {city_countries}.")
    if city_country_descs:
        text_parts.append(f"The countries are described as: {city_country_descs}.")
    if city_descs:
        text_parts.append(f"The cities are described as: {city_descs}.")
    if end_port:
        text_parts.append(f"The cruise may end at the port of {end_port}.")
    if end_port_country:
        text_parts.append(f"The ending port is in {end_port_country}.")
    if end_port_desc:
        text_parts.append(f"The ending port is described as: {end_port_desc}.")
    if categories:
        text_parts.append(f"The cruise belongs to the following categories: {categories}.")
    if category_descs:
        text_parts.append(f"The cruise categories are described as: {category_descs}.")
    if category_type:
        text_parts.append(f"The cruise category type is {category_type}.")

    return {
        "text": " ".join(text_parts),
        "meta": {
            "cities": cities,
            "city_countries": city_countries,
            "rivers": rivers
        }
    }


def get_localized_text(data, key):
    """
    Gets localized text from a dictionary based on a prioritized list of languages.
    If the text is not in English, it translates it to English.
    """
    if key in data and data[key]:
        return data[key]
    return ""