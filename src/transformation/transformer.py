import json
from src.transformation.semantic import get_descriptive_text_and_meta
import logging
import os

logging.basicConfig(level=logging.INFO)

def transform_data(cruise_data):
    """
    Orchestrates the data cleaning, translation, and semantic transformation for a single cruise.
    """
    # This is a simplified transformation. 
    # In a real-world scenario, you would iterate through the fields 
    # specified in FR-005 and apply cleaning and translation.
    
    # For now, we'll just apply it to the descriptive text generation

    if cruise_data.get("date_and_price_info", {}) is None:
        return None

    if len(cruise_data.get("date_and_price_info", {}).get("dates", [])) == 0:
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
            "min_price": cruise_data.get("date_and_price_info", {}).get("prices", [])[0],
            "max_price": cruise_data.get("date_and_price_info", {}).get("prices", [])[1],
            "dates": ", ".join(cruise_data.get("date_and_price_info", {}).get("dates", [])),
            "ranges": ", ".join(cruise_data.get("date_and_price_info", {}).get("ranges", []))
        }
    }

def main():
    """
    Main function to orchestrate the data transformation.
    """
    logging.info("Starting data transformation")
    with open("cruise_data.json", "r") as f:
        all_cruise_data = json.load(f)

    logging.info(f"Found {len(all_cruise_data)} cruises to transform")
    transformed_data = []
    if os.path.exists("transformed_cruise_data.json"):
        with open("transformed_cruise_data.json", "r") as f2:
            transformed_data = json.load(f2)
            logging.info(f"Loaded {len(transformed_data)} previously transformed cruises")

    # Load existing transformed IDs if file exists
    transformed_cruises = []
    if os.path.exists("transformed_cruise_ids.json"):
        with open("transformed_cruise_ids.json", "r") as f3:
            transformed_cruises = json.load(f3)
            logging.info(f"Loaded {len(transformed_cruises)} previously transformed cruises")
    
    for i, cruise in enumerate(all_cruise_data, 1):
        cruise_id = cruise.get("cruise_id")

        # Skip already transformed cruises
        if cruise_id in transformed_cruises:
            continue

        try:
            tr = transform_data(cruise)

            if tr is not None:
                transformed_data.append(tr)
                if i % 10 == 0 or i == len(all_cruise_data):
                    logging.info(f"Transformed: {i}/{len(all_cruise_data)}")
            transformed_cruises.append(cruise_id)
        except Exception as e:
            logging.error(f"Permission error on cruise {cruise_id}: {e}")
            break

    with open("transformed_cruise_data.json", "w", encoding="utf-8") as f:
        json.dump(transformed_data, f, ensure_ascii=False, indent=4)
    with open("transformed_cruise_ids.json", "w", encoding="utf-8") as f:
        json.dump(transformed_cruises, f, ensure_ascii=False, indent=4)
    logging.info("Data transformation completed")

if __name__ == "__main__":
    main()
