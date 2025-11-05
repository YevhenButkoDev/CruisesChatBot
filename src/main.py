from src.data_extraction.extractor import extract_data, get_enabled_cruise_ids
from src.transformation.transformer import main as transform_main
from src.util.cloud_storage import sync_chroma_data_to_gcs, upload_sqlite_db_to_gcs
from src.vector_db.main import create_vector_db
from src.util.sqlite_storage import CruiseDataStorage

def main():
    """Main orchestration logic."""
    print("Starting data extraction...")
    extract_data()
    print("Data extraction complete.")
    
    print("Starting data transformation...")
    transform_main()
    print("Data transformation complete.")
    
    print("Starting vector database creation...")
    create_vector_db()
    print("Vector database creation complete.")

    print("Uploading Vector database to GCS.")
    sync_chroma_data_to_gcs()
    print("Upload completed.")

    storage = CruiseDataStorage()
    storage.create_cruise_dates_table()

    print("Clearing SQLite data...")
    storage.clear_all_data()
    print("SQLite data cleared.")
    upload_sqlite_db_to_gcs()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    main()
