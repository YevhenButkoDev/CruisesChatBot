import os
import logging
import chromadb
from chromadb.api.types import EmbeddingFunction
from src.vector_db.creator import AllMpnetBaseV2EmbeddingFunction  # adjust import if needed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------
# Wrapper to make your old embedder compatible with Chroma
# ------------------------------
class ChromaCompatibleEmbedding(EmbeddingFunction):
    def __init__(self, embedder):
        """
        Wraps your existing AllMpnetBaseV2EmbeddingFunction to satisfy
        the new Chroma EmbeddingFunction interface.
        """
        self.embedder = embedder

    def __call__(self, input: list[str]) -> list[list[float]]:
        """
        Chroma now expects __call__ with input: list[str] and must return
        list of embedding vectors (list of floats) corresponding to each string.
        """
        embeddings = []
        for text in input:
            vec = self.embedder(text)
            # convert to list if returned as numpy array
            if hasattr(vec, "tolist"):
                vec = vec.tolist()
            embeddings.append(vec)
        return embeddings


# ------------------------------
# Query function
# ------------------------------
def query_chroma_db(
    query_text: str,
    collection_name: str = "cruise_collection",
    n_results: int = 5,
    cruise_ids: list[str] | None = None
):
    """
    Queries the Chroma vector database using AllMpnetBaseV2EmbeddingFunction
    and returns the top n_results, optionally filtered by cruise IDs.

    :param query_text: English text to query against the Chroma vector store.
    :param collection_name: The name of the Chroma collection.
    :param n_results: Number of top results to return.
    :param cruise_ids: Optional list of cruise IDs to filter metadata.
    :return: Query results from Chroma.
    """
    logger.info(f"🔎 ChromaDB Query - Text: '{query_text}', Collection: {collection_name}, Results: {n_results}")
    logger.info(f"🔎 ChromaDB Filter - Cruise IDs: {len(cruise_ids) if cruise_ids else 0} IDs")
    
    try:
        # Connect to persistent Chroma client
        chroma_dir = os.getenv("CHROMA_DATA_DIR", "./chroma_data")
        logger.info(f"📁 Connecting to ChromaDB at: {chroma_dir}")
        client = chromadb.PersistentClient(chroma_dir)
        logger.info("✅ ChromaDB client connected")

        # Initialize embedding function
        logger.info("🧠 Initializing embedding function")
        embedding_function = ChromaCompatibleEmbedding(AllMpnetBaseV2EmbeddingFunction())
        logger.info("✅ Embedding function initialized")

        # Access the collection
        logger.info(f"📚 Accessing collection: {collection_name}")
        collection = client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )

        # Prepare filter if cruise_ids provided
        where_filter = None
        if cruise_ids:
            where_filter = {"cruise_id": {"$in": cruise_ids}}
            logger.info(f"🔍 Applied filter for {len(cruise_ids)} cruise IDs")
        else:
            logger.info("🔍 No cruise ID filter applied")

        # Query the collection
        logger.info("🔎 Executing ChromaDB query")
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )
        
        result_count = len(results.get("ids", [[]])[0])
        logger.info(f"✅ ChromaDB query completed - Found {result_count} results")

        return results
        
    except Exception as e:
        logger.error(f"❌ ChromaDB query error: {str(e)}")
        raise


def get_chunks_by_meta(filters: dict, collection_name: str = "cruise_collection"):
    """
    Retrieves all chunks (documents) from a Chroma collection
    that match the provided metadata filter.

    :param collection_name: Name of the Chroma collection.
    :param filters: Dictionary defining metadata filters (e.g. {"cruise_id": "CRUISE_123"}).
    :return: List of chunks (documents) matching the filter.
    """
    import chromadb

    # Connect to persistent Chroma client
    client = chromadb.PersistentClient(os.getenv("CHROMA_DATA_DIR", "./src/chroma_data"))

    # Get the collection
    collection = client.get_collection(name=collection_name)

    # Retrieve chunks by metadata
    results = collection.get(where=filters)

    # Example: results keys -> ids, documents, embeddings, metadatas
    chunks = []
    for i, doc_id in enumerate(results["ids"]):
        chunks.append({
            "id": doc_id,
            "document": results["documents"][i],
            "meta": results["metadatas"][i]
        })

    return chunks


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    print(query_chroma_db(query_text = "Cruise to Barcelona", n_results = 5))