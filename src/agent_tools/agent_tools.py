import logging
import time
from datetime import date, timedelta
from typing import List, Tuple, Optional

from src.data_extraction.db import get_db_connection
from src.vector_db.query import query_chroma_db
from src.util.date_utils import validate_and_correct_date_range
from src.util.cruise_utils import build_cruise_url, parse_cruise_results

logger = logging.getLogger(__name__)


def get_current_date() -> str:
    """Get current date in ISO format."""
    try:
        return date.today().isoformat()
    except Exception:
        return "no data"


def filter_cruises_by_date_range(date_from: date, date_to: date) -> List[str]:
    """Filter enabled cruise IDs by date range."""
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


def find_cruise_info(cruise_id: str):
    """Get detailed cruise information by ID."""
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT
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


def find_relevant_cruises(user_question: str, date_from: str, date_to: str) -> str:
    """
    Find cruises relevant to user query within date range.
    
    :param user_question: English natural-language search query
    :param date_from: Start date in ISO format 'YYYY-MM-DD'
    :param date_to: End date in ISO format 'YYYY-MM-DD'
    :return: Parsed cruise results or "no data"
    """
    start_time = time.time()
    
    try:
        # Validate and correct date range
        date_from_corrected, date_to_corrected, is_valid = validate_and_correct_date_range(date_from, date_to)
        
        # Filter by date if valid range provided
        cruise_ids = []
        if is_valid:
            cruise_ids = filter_cruises_by_date_range(date_from_corrected, date_to_corrected)

        # Query vector database
        vector_start = time.time()
        results = query_chroma_db(query_text=user_question, cruise_ids=cruise_ids)
        vector_elapsed = time.time() - vector_start
        print(f"⏱️ Vector DB query: {vector_elapsed:.2f}s")
        
        # Parse and format results
        parsed_results = parse_cruise_results(results)

        total_elapsed = time.time() - start_time
        print(f"⏱️ Find relevant cruises: {total_elapsed:.2f}s")
        
        return parsed_results
        
    except Exception as e:
        logger.error(f"❌ Error finding relevant cruises: {str(e)}")
        return "no data"
