from src.data_extraction.extractor import extract_data
from src.transformation.transformer import main as transform_main
from src.vector_db.main import create_vector_db

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

if __name__ == "__main__":
    main()
