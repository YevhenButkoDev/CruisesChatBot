from src.transformation.semantic import get_descriptive_text_and_meta
from src.util.sqlite_storage import CruiseDataStorage
import logging
import os

logging.basicConfig(level=logging.INFO)

def transform_data(cruise_data):
    """
    Orchestrates the data cleaning, translation, and semantic transformation for a single cruise.
    """
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
    Main function to orchestrate the data transformation using SQLite storage with batch processing.
    """
    logging.info("Starting data transformation")
    
    storage = CruiseDataStorage()
    
    # Get total count and existing processed IDs
    total_cruises = storage.get_raw_cruises_count()
    transformed_cruises = set(storage.get_processed_ids())
    logging.info(f"Found {total_cruises} total cruises, {len(transformed_cruises)} already processed")
    
    batch_size = 100
    offset = 0
    processed_count = 0
    
    while True:
        # Get batch of raw cruise data
        cruise_batch = storage.get_raw_cruises_batch(batch_size, offset)
        
        if not cruise_batch:
            break
            
        for cruise in cruise_batch:
            cruise_id = cruise.get("cruise_id")

            # Skip already transformed cruises
            if cruise_id in transformed_cruises:
                continue

            try:
                tr = transform_data(cruise)

                if tr is not None:
                    storage.save_transformed_cruise(tr)
                    processed_count += 1
                    if processed_count % 10 == 0:
                        logging.info(f"Transformed: {processed_count}")
                
                storage.mark_as_processed(cruise_id)
                transformed_cruises.add(cruise_id)
            except Exception as e:
                logging.error(f"Error processing cruise {cruise_id}: {e}")
                break
        
        offset += batch_size
        logging.info(f"Processed batch {offset//batch_size}, total processed: {processed_count}")

    logging.info("Data transformation completed")

if __name__ == "__main__":
    main()
