import asyncio
import logging
import time
from langdetect import detect
from googletrans import Translator

from src.data_extraction.db import get_db_connection
from src.util.util import validate_and_correct_date_range
from src.vector_db.query import query_chroma_db, get_chunks_by_meta
from datetime import datetime, date, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def translate_to_english(text: str) -> str:
#     """Translate text to English if it's not already in English."""
#     try:
#         detected_lang = detect(text)
#         if detected_lang != 'en':
#             translator = Translator()
#             return asyncio.run(translator.translate(text, dest='en')).text
#         return text
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return text  # Return original if translation fails


def validate_and_correct_date_range(date_from: str | None, date_to: str | None) -> tuple[date, date, bool]:
    """
    Validates and corrects a date range.

    Rules:
    - If either date is missing, default is used.
    - If date_from >= date_to, defaults are used.
    - Both dates must be after today.
    - Default date_from = today, date_to = today + 2 years.

    :param date_from: Start date in ISO format 'YYYY-MM-DD' or None.
    :param date_to: End date in ISO format 'YYYY-MM-DD' or None.
    :return: Tuple (corrected_date_from, corrected_date_to) as datetime.date objects.
    """
    today = date.today()
    default_from = today
    default_to = today + timedelta(days=365 * 2)

    # Parse safely
    try:
        from_dt = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
    except ValueError:
        from_dt = None

    try:
        to_dt = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None
    except ValueError:
        to_dt = None

    # Validation logic
    if not from_dt or not to_dt:
        return default_from, default_to, False

    if from_dt >= to_dt:
        return default_from, default_to, False

    if from_dt <= today or to_dt <= today:
        return default_from, default_to, False

    return from_dt, to_dt, True

def filter_cruises_by_date_range(date_from: date, date_to: date):
    """
    Fetches all enabled cruise IDs from the mv_cruise_info materialized view
    that fall within the specified date range.

    :param date_from: Start date (inclusive)
    :param date_to: End date (inclusive)
    :return: List of enabled cruise IDs within the given date range.
    """
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT m.cruise_id
            FROM mv_cruise_info m
            JOIN mv_cruise_date_range_info mcdri 
                ON mcdri.cruise_id = m.cruise_id
            WHERE m.enabled = TRUE
              AND (
                    (mcdri.cruise_date_range_info->'dateRange'->>'begin_date')::date <= %s
                    AND (mcdri.cruise_date_range_info->'dateRange'->>'end_date')::date >= %s
                  )
        """

        cur.execute(query, (date_to, date_from))
        cruise_ids = [row[0] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        elapsed = time.time() - start_time
        print(f"⏱️ DB filter cruises: {elapsed:.2f}s")
        
        return cruise_ids
        
    except Exception as e:
        logger.error(f"❌ Database error in filter_cruises_by_date_range: {str(e)}")
        return []


def get_current_date():
    """
    Function provides current date
    :return: current date
    """
    try:
        return date.today().isoformat()
    except Exception as e:
        return "no data"


def find_cruise_info(cruise_id: str):
    """
        Retrieves detailed information for a specific cruise based on its unique cruise_id
        from the Chroma vector database.
        :param cruise_id unique cruise identifier
    """
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
                SELECT
                  -- Cruise basic info (English)
                  cruise_info -> 'cruise' -> 'name_i18n' ->> 'en' AS cruise_name_en,
                  cruise_info -> 'cruise' -> 'simple_itinerary_description_i18n' ->> 'en' AS simple_itinerary_en,
                  cruise_info -> 'portMaybe' -> 'name_i18n' ->> 'en' AS port_name_en,
                  cruise_info -> 'portMaybe' -> 'country_name_i18n' ->> 'en' AS port_country_en,
                  cruise_info -> 'portMaybe' ->> 'latitude' AS port_latitude,
                  cruise_info -> 'portMaybe' ->> 'longitude' AS port_longitude,
                  (
                    SELECT json_agg(
                      json_build_object(
                        'day', i -> 'itinerary' ->> 'day',
                        'city_name_en', i -> 'city' -> 'name_i18n' ->> 'en',
                        'country_name_en', i -> 'city' -> 'country_name_i18n' ->> 'en',
                        'arrival_time', i -> 'itinerary' ->> 'arrival_time',
                        'departure_time', i -> 'itinerary' ->> 'departure_time'
                      )
                    )
                    FROM jsonb_array_elements(cruise_info -> 'itineraries') AS i
                  ) AS itineraries_en

                FROM mv_cruise_info
                WHERE cruise_id = %s;
            """

        cur.execute(query, (cruise_id,))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        elapsed = time.time() - start_time
        print(f"⏱️ DB cruise info: {elapsed:.2f}s")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error finding cruise info for ID {cruise_id}: {str(e)}")
        return "no data"


def build_cruise_url(results: dict, index: int, base_url: str = "https://uat.center.cruises/cruise-") -> str:
    try:
        # Safely extract metadata
        meta_list = results.get("metadatas", [[]])
        meta = meta_list[0][index] if meta_list and len(meta_list[0]) > index else {}

        ufl = str(meta.get("ufl", "")).strip()
        ranges_str = str(meta.get("ranges", "")).strip()

        # Validate ufl
        if not ufl:
            print(f"⚠️ Missing or invalid 'ufl' for index {index}")
            return ""

        # Validate and extract first range
        first_range = ""
        if ranges_str:
            ranges_parts = [r.strip() for r in ranges_str.split(",") if r.strip()]
            if ranges_parts:
                first_range = ranges_parts[0]

        if not first_range:
            print(f"⚠️ Missing or invalid 'ranges' for index {index}")
            return ""

        # Construct URL safely
        cruise_url = f"{base_url}{first_range}-{ufl}"
        return cruise_url

    except Exception as e:
        print(f"❌ Failed to build cruise URL for index {index}: {e}")
        return ""


def find_relevant_cruises(user_question: str, date_from: str, date_to: str) -> str:
    """
    Retrieves cruise information relevant to the user's question within a specified date range.

    :param user_question: An ENGLISH natural-language question or search query used to retrieve relevant cruise data from the vector database.
    :param date_from: The start date of the desired cruise range (inclusive).
                      Must be in ISO format 'YYYY-MM-DD' (e.g., '2025-10-01').
                      If not provided or empty, no lower bound on the date range is applied.
    :param date_to: The end date of the desired cruise range (inclusive).
                    Must be in ISO format 'YYYY-MM-DD' (e.g., '2025-15').
                    If not provided or empty, no upper bound on the date range is applied.
    :return: A list of parsed cruise details including cruise_id, cruise_info, metadata, and relevance score.
             Returns "no data" if no results are found or an error occurs.
    """
    start_time = time.time()
    
    try:
        # Validate and correct date range
        range_result = validate_and_correct_date_range(date_from, date_to)

        ids = []
        if range_result[2]:
            ids = filter_cruises_by_date_range(range_result[0], range_result[1])

        vector_start = time.time()
        results = query_chroma_db(query_text=user_question, cruise_ids=ids)
        vector_elapsed = time.time() - vector_start
        print(f"⏱️ Vector DB query: {vector_elapsed:.2f}s")
        
        parsed_results = []
        for i, doc_id in enumerate(results["ids"][0]):
            cruise_url = build_cruise_url(results, i)
            parsed_result = {
                "cruise_id": doc_id,
                "cruise_info": results["documents"][0][i],
                "meta": results["metadatas"][0][i],
                "score": results["distances"][0][i],
                "link_to_website": cruise_url
            }
            parsed_results.append(parsed_result)

        total_elapsed = time.time() - start_time
        print(f"⏱️ Find relevant cruises: {total_elapsed:.2f}s")
        
        return parsed_results
        
    except Exception as e:
        logger.error(f"❌ Error finding relevant cruises: {str(e)}")
        return "no data"