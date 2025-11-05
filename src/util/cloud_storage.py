import os
import shutil
from google.cloud import storage
import logging

def sync_chroma_data_from_gcs():
    """Download ChromaDB data from Google Cloud Storage on startup."""
    logging.info("Starting ChromaDB data sync from GCS...")
    
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        logging.info("No GCS bucket configured, using local storage")
        return
    
    logging.info(f"Using GCS bucket: {bucket_name}")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        # Use /tmp for writable storage in Cloud Run
        local_path = "/tmp/chroma_data"
        
        logging.info(f"Syncing to local path: {local_path}")
        
        # Create local directory
        os.makedirs(local_path, exist_ok=True)
        
        # Download all files from GCS bucket
        blobs = bucket.list_blobs(prefix="chroma_data/")
        file_count = 0
        for blob in blobs:
            if not blob.name.endswith('/'):  # Skip directories
                # Remove the chroma_data/ prefix and use local_path
                relative_path = blob.name.replace("chroma_data/", "")
                local_file_path = os.path.join(local_path, relative_path)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                blob.download_to_filename(local_file_path)
                file_count += 1
                
        logging.info(f"ChromaDB data sync completed: {file_count} files synced from GCS bucket: {bucket_name} to {local_path}")
    except Exception as e:
        logging.error(f"Failed to sync from GCS: {e}")
        raise

def sync_chroma_data_to_gcs():
    """Upload ChromaDB data to Google Cloud Storage, replacing existing content."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        return
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        local_path = os.getenv("CHROMA_DATA_DIR", "./chroma_data")
        
        if not os.path.exists(local_path):
            return
        
        # Upload to temporary location first
        temp_prefix = "chroma_data_temp/"
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, local_path)
                blob_name = f"{temp_prefix}{relative_path}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(local_file)
        
        # Delete old files
        old_blobs = bucket.list_blobs(prefix="chroma_data/")
        for blob in old_blobs:
            blob.delete()

        # Move temp files to final location
        temp_blobs = bucket.list_blobs(prefix=temp_prefix)
        for temp_blob in temp_blobs:
            final_name = temp_blob.name.replace(temp_prefix, "chroma_data/")
            bucket.copy_blob(temp_blob, bucket, final_name)
            temp_blob.delete()
                
        logging.info(f"ChromaDB data synced to GCS bucket: {bucket_name} from {local_path}")
    except Exception as e:
        logging.error(f"Failed to sync to GCS: {e}")

def fetch_sqlite_db_from_gcs(db_filename: str = "cruise_data.db"):
    """Download SQLite database from Google Cloud Storage."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        logging.info("No GCS bucket configured")
        return
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(db_filename)
        
        local_db_path = f"/tmp/{db_filename}"
        blob.download_to_filename(local_db_path)
        logging.info(f"SQLite database downloaded from GCS to {local_db_path}")
        return local_db_path
    except Exception as e:
        logging.error(f"Failed to fetch SQLite DB from GCS: {e}")
        return None

def upload_sqlite_db_to_gcs(db_filename: str = "cruise_data.db"):
    """Upload SQLite database to Google Cloud Storage."""
    sqllite_path = os.getenv("SQLITE_DB_PATH")
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        logging.info("No GCS bucket configured")
        return False
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(db_filename)
        
        blob.upload_from_filename(sqllite_path)
        logging.info(f"SQLite database uploaded to GCS: {db_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to upload SQLite DB to GCS: {e}")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    sync_chroma_data_to_gcs()
