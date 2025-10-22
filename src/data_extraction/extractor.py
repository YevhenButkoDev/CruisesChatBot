import json
import logging
from datetime import datetime
from src.data_extraction.db import get_db_connection

logging.basicConfig(level=logging.INFO)


def get_enabled_cruise_ids():
    """Fetches all enabled cruise IDs from the mv_cruise_info materialized view."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.cruise_id 
        FROM mv_cruise_info m
	    JOIN mv_cruise_date_range_info mcdri on mcdri.cruise_id = m.cruise_id  
        WHERE m.enabled = true
            and (mcdri.cruise_date_range_info->'dateRange'->>'begin_date')::date > NOW()::date
            """)
    cruise_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return cruise_ids


def get_cruise_data_in_batches(cruise_ids, batch_size=50):
    """Fetches cruise data in batches from the mv_cruise_info materialized view."""
    conn = get_db_connection()
    cur = conn.cursor()
    for i in range(0, len(cruise_ids), batch_size):
        batch_ids = cruise_ids[i:i + batch_size]
        cur.execute(
            "SELECT cruise_id, ufl, cruise_info FROM mv_cruise_info WHERE cruise_id = ANY(%s)",
            (batch_ids,),
        )
        yield cur.fetchall()
    cur.close()
    conn.close()


def get_date_and_price_info(cruise_ids):
    """Fetches date and price information from the mv_cruise_date_range_info materialized view."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT cruise_id, cruise_date_range_id, cruise_date_range_info FROM mv_cruise_date_range_info WHERE cruise_id = ANY(%s)",
        (cruise_ids,),
    )
    date_and_price_info = {}
    for row in cur.fetchall():
        cruise_id, cruise_date_range_id, info = row

        if cruise_id not in date_and_price_info:
            date_and_price_info[cruise_id] = {"dates": [], "prices": [0, 0], "ranges": []}

        if info.get("minPrice") is not None:
            price = info.get("minPrice", {}).get("2")
            prev_min = date_and_price_info[cruise_id]["prices"][0]
            prev_max = date_and_price_info[cruise_id]["prices"][1]

            if price and (prev_min == 0 or price < prev_min):
                date_and_price_info[cruise_id]["prices"][0] = price
            elif price and price > prev_max:
                date_and_price_info[cruise_id]["prices"][1] = price

        date_range = info.get("dateRange")
        if date_range and date_range.get("begin_date") and date_range.get("end_date"):
            begin_date = datetime.fromisoformat(date_range["begin_date"].replace('Z', '+00:00'))
            is_valid = begin_date.date() >= datetime.now().date()
            if is_valid is True:
                date_and_price_info[cruise_id]["dates"].append(begin_date.date().strftime("%Y%m"))
                date_and_price_info[cruise_id]["ranges"].append(str(cruise_date_range_id))

    cur.close()
    conn.close()
    return date_and_price_info


def extract_data():
    """Orchestrates the data extraction process and saves the final data to a JSON file."""
    logging.info("Starting data extraction")
    enabled_cruise_ids = get_enabled_cruise_ids()
    logging.info(f"Found {len(enabled_cruise_ids)} enabled cruises")

    all_cruise_data = []
    processed = 0
    skipped = 0

    for batch in get_cruise_data_in_batches(enabled_cruise_ids):
        batch_cruise_ids = [row[0] for row in batch]
        date_and_price_info = get_date_and_price_info(batch_cruise_ids)

        if date_and_price_info is None:
            skipped += len(batch)
            continue

        for row in batch:
            cruise_id, ufl, cruise_info = row
            all_cruise_data.append({
                "cruise_id": cruise_id,
                "ufl": ufl,
                "cruise_info": cruise_info,
                "date_and_price_info": date_and_price_info.get(cruise_id),
            })
            processed += 1

        # if processed > 200:
        #     break

        logging.info(
            f"Processed: {processed}, Skipped: {skipped}, Left: {len(enabled_cruise_ids) - processed - skipped}")

    with open("cruise_data.json", "w", encoding="utf-8") as f:
        json.dump(all_cruise_data, f, ensure_ascii=False, indent=4)
    logging.info("Data extraction completed")


if __name__ == "__main__":
    extract_data()
