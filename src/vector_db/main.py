from src.vector_db.creator import get_chroma_client, create_collection, add_cruise_document
from src.util.sqlite_storage import CruiseDataStorage
import logging

logging.basicConfig(level=logging.INFO)

def create_vector_db():
    """Main function to orchestrate the vector database creation process using SQLite."""
    client = get_chroma_client()
    collection = create_collection(client)
    
    storage = CruiseDataStorage()
    transformed_data = storage.get_transformed_cruises()

    processed_count = 0
    for cruise_document in transformed_data:
        add_cruise_document(collection, cruise_document)
        processed_count += 1
        logging.info(f"Embedded: {processed_count}/{len(transformed_data)}")

if __name__ == "__main__":
    create_vector_db()
