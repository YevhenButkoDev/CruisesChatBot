from src.transformation.translator import get_localized_text
from src.transformation.cleaner import remove_html_tags

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
        ]))).split()[:200]
    )

    start_port = get_i18n_text(cruise_info, ["portMaybe", "name_i18n"])
    start_port_desc = " ".join(remove_html_tags(get_i18n_text(cruise_info, ["portMaybe", "description_i18n"])).split()[:200])
    start_port_country = get_i18n_text(cruise_info, ["portMaybe", "country_gen_i18n"])

    cities = ", ".join(list(set(
        get_i18n_text(i, ["city", "name_i18n"])
        for i in (get_nested(cruise_info, ["itineraries"]) or [])
        if get_i18n_text(i, ["city", "name_i18n"])
    )))
    city_countries = ", ".join(list(set([get_i18n_text(i, ["city", "country_name_i18n"]) for i in get_nested(cruise_info, ["itineraries"]) or []])))
    city_country_descs = " ".join(
        ", ".join(list(set([
            remove_html_tags(get_i18n_text(i, ["city", "country_description_i18n"]))
            for i in get_nested(cruise_info, ["itineraries"]) or []
        ]))).split()[:200]
    )
    city_descs = " ".join(
        ", ".join([
            remove_html_tags(get_i18n_text(i, ["city", "description_i18n"]))
            for i in get_nested(cruise_info, ["itineraries"]) or []
        ]).split()[:200]
    )

    end_port = get_i18n_text(cruise_info, ["lastPortMaybe", "name_i18n"])
    end_port_country = get_i18n_text(cruise_info, ["lastPortMaybe", "country_name_i18n"])
    end_port_desc = remove_html_tags(get_i18n_text(cruise_info, ["lastPortMaybe", "description_i18n"]))

    categories = ", ".join([get_i18n_text(c, ["name_i18n"]) for c in get_nested(cruise_info, ["cruiseCategories"]) or []])
    category_descs = ", ".join([remove_html_tags(get_i18n_text(c, ["description_i18n"])) for c in get_nested(cruise_info, ["cruiseCategories"]) or []])
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
