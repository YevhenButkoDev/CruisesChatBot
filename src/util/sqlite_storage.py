import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

class CruiseDataStorage:
    def __init__(self, db_path: str = "cruise_data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS raw_cruises (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transformed_cruises (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_ids (
                    cruise_id TEXT PRIMARY KEY,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_raw_cruises(self, cruises: List[Dict[str, Any]]):
        """Save raw cruise data."""
        with sqlite3.connect(self.db_path) as conn:
            for cruise in cruises:
                cruise_id = cruise.get('id', cruise.get('cruise_id'))
                conn.execute(
                    "INSERT OR REPLACE INTO raw_cruises (id, data) VALUES (?, ?)",
                    (cruise_id, json.dumps(cruise))
                )
    
    def get_raw_cruises_batch(self, batch_size: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get raw cruise data in batches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM raw_cruises LIMIT ? OFFSET ?", 
                (batch_size, offset)
            )
            return [json.loads(row[0]) for row in cursor.fetchall()]
    
    def get_raw_cruises_count(self) -> int:
        """Get total count of raw cruises."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM raw_cruises")
            return cursor.fetchone()[0]

    def get_raw_cruises(self) -> List[Dict[str, Any]]:
        """Get all raw cruise data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM raw_cruises")
            return [json.loads(row[0]) for row in cursor.fetchall()]
    
    def save_transformed_cruise(self, cruise: Dict[str, Any]):
        """Save a single transformed cruise."""
        cruise_id = cruise.get('id', cruise.get('cruise_id'))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO transformed_cruises (id, data) VALUES (?, ?)",
                (cruise_id, json.dumps(cruise))
            )
    
    def get_transformed_cruises(self) -> List[Dict[str, Any]]:
        """Get all transformed cruise data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM transformed_cruises")
            return [json.loads(row[0]) for row in cursor.fetchall()]
    
    def get_processed_ids(self) -> List[str]:
        """Get list of processed cruise IDs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT cruise_id FROM processed_ids")
            return [row[0] for row in cursor.fetchall()]
    
    def mark_as_processed(self, cruise_id: str):
        """Mark a cruise as processed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO processed_ids (cruise_id) VALUES (?)",
                (cruise_id,)
            )
    
    def clear_all_data(self):
        """Clear all data from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM raw_cruises")
            conn.execute("DELETE FROM transformed_cruises")
            conn.execute("DELETE FROM processed_ids")
