import unittest
import json
from fastapi.testclient import TestClient
from src.api import app
import chromadb
from src.vector_db.creator import AllMpnetBaseV2EmbeddingFunction

class TestApi(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        # Set up a test collection in ChromaDB
        client = chromadb.PersistentClient("./chroma_data")
        embedding_function = AllMpnetBaseV2EmbeddingFunction()
        try:
            client.delete_collection(name="cruise_collection")
        except ValueError:
            pass # Collection does not exist
        collection = client.create_collection(
            name="cruise_collection",
            embedding_function=embedding_function
        )
        collection.add(
            ids=["cruise1"],
            documents=["A beautiful cruise to the Caribbean"],
            metadatas=[{
                "destination": "Caribbean",
                "itinerary": json.dumps({}),
                "sailing_dates": json.dumps([]),
                "ship_information": json.dumps({}),
                "pricing": json.dumps({})
            }]
        )

    def test_full_conversation_flow(self):
        # Start the conversation
        response = self.client.post("/chat", json={"message": "I want to find a cruise"})
        self.assertEqual(response.status_code, 200)
        conversation_id = response.json()["conversation_id"]
        self.assertEqual(response.json()["response"], "I can help with that. What is your desired destination?")

        # Provide destination
        response = self.client.post("/chat", json={"conversation_id": conversation_id, "message": "Caribbean"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Got it. When would you like to travel?")

        # Provide date range and get results
        response = self.client.post("/chat", json={"conversation_id": conversation_id, "message": "next summer"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Here are some cruises that match your criteria:", response.json()["response"])
        self.assertEqual(len(response.json()["cruises"]), 1)
        self.assertEqual(response.json()["cruises"][0]["cruise_id"], "cruise1")

if __name__ == '__main__':
    unittest.main()
