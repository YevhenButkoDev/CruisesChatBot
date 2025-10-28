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
    """Upload ChromaDB data to Google Cloud Storage."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        return
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        local_path = os.getenv("CHROMA_DATA_DIR", "/app/chroma_data")
        
        if not os.path.exists(local_path):
            return
            
        # Upload all files to GCS
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                # Create blob path with chroma_data/ prefix
                relative_path = os.path.relpath(local_file, local_path)
                blob_name = f"chroma_data/{relative_path}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(local_file)
                
        logging.info(f"ChromaDB data synced to GCS bucket: {bucket_name} from {local_path}")
    except Exception as e:
        logging.error(f"Failed to sync to GCS: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    sync_chroma_data_from_gcs()