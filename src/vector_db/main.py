import json
from src.vector_db.creator import get_chroma_client, create_collection, add_cruise_document
import logging


logging.basicConfig(level=logging.INFO)

def create_vector_db():
    """Main function to orchestrate the vector database creation process."""
    client = get_chroma_client()
    collection = create_collection(client)
    
    with open("transformed_cruise_data.json", "r") as f:
        transformed_data = json.load(f)

    processed_count = 0
    for cruise_document in transformed_data:
        add_cruise_document(collection, cruise_document)
        processed_count += 1
        logging.info(f"Embedded: {processed_count}/{len(transformed_data)}")


if __name__ == "__main__":
    create_vector_db()
