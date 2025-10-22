from sentence_transformers import SentenceTransformer
import chromadb


class AllMpnetBaseV2EmbeddingFunction:
    def __init__(self, model_name="all-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input):
        # input is a list of strings
        embeddings = self.model.encode(input)
        # make sure to return a list of lists of floats
        return embeddings.tolist()


def get_chroma_client(data_dir="./chroma_data"):
    """Initializes and returns a Chroma DB client."""
    client = chromadb.PersistentClient(path=data_dir)
    return client


def create_collection(client, collection_name="cruise_collection"):
    """Creates a new collection in Chroma DB."""
    embedding_function = AllMpnetBaseV2EmbeddingFunction()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    return collection


def add_cruise_document(collection, cruise_document):
    """Adds a single cruise document to the collection."""
    collection.add(
        documents=[cruise_document["text_chunk"]],
        metadatas=[cruise_document["metadata"]],
        ids=[str(cruise_document["cruise_id"])]
    )
