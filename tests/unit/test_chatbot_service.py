import unittest
import json
from unittest.mock import patch
from src.chatbot.services import handle_chat, conversation_context
from src.chatbot.models import ChatMessage

class TestChatbotService(unittest.TestCase):

    def setUp(self):
        # Clear the conversation context before each test
        conversation_context.clear()

    def test_identify_find_cruise_intent(self):
        chat_message = ChatMessage(message="I want to find a cruise to the Caribbean")
        response = handle_chat(chat_message)
        self.assertEqual(response.response, "I can help with that. What is your desired destination?")

    def test_asks_for_destination_if_intent_is_find_cruise(self):
        chat_message = ChatMessage(message="I want to find a cruise")
        response = handle_chat(chat_message)
        self.assertEqual(response.response, "I can help with that. What is your desired destination?")

    def test_asks_for_date_range_after_destination_is_provided(self):
        # First message to set the intent
        chat_message_1 = ChatMessage(message="I want to find a cruise")
        response_1 = handle_chat(chat_message_1)
        conversation_id = response_1.conversation_id

        # Second message to provide the destination
        chat_message_2 = ChatMessage(conversation_id=conversation_id, message="Caribbean")
        response_2 = handle_chat(chat_message_2)

        self.assertEqual(response_2.response, "Got it. When would you like to travel?")

    @patch('src.chatbot.services.query_chroma_db')
    def test_queries_db_and_returns_cruises(self, mock_query_chroma_db):
        # Mock the response from the vector database
        mock_query_chroma_db.return_value = {
            "ids": [["cruise1"]],
            "metadatas": [[{
                "destination": "Caribbean",
                "itinerary": json.dumps({}),
                "sailing_dates": json.dumps([]),
                "ship_information": json.dumps({}),
                "pricing": json.dumps({})
            }]]
        }

        # Set up the conversation context
        chat_message_1 = ChatMessage(message="I want to find a cruise")
        response_1 = handle_chat(chat_message_1)
        conversation_id = response_1.conversation_id

        chat_message_2 = ChatMessage(conversation_id=conversation_id, message="Caribbean")
        response_2 = handle_chat(chat_message_2)

        # Third message to provide the date range and trigger the db query
        chat_message_3 = ChatMessage(conversation_id=conversation_id, message="next summer")
        response_3 = handle_chat(chat_message_3)

        self.assertEqual(response_3.response, "Here are some cruises that match your criteria:")
        self.assertEqual(len(response_3.cruises), 1)
        self.assertEqual(response_3.cruises[0].cruise_id, "cruise1")

    @patch('src.chatbot.services.query_chroma_db')
    def test_flexible_date_searches_next_year(self, mock_query_chroma_db):
        # Mock the response from the vector database
        mock_query_chroma_db.return_value = {
            "ids": [["cruise2"]],
            "metadatas": [[{
                "destination": "Alaska",
                "itinerary": json.dumps({}),
                "sailing_dates": json.dumps([]),
                "ship_information": json.dumps({}),
                "pricing": json.dumps({})
            }]]
        }

        # Set up the conversation context
        chat_message_1 = ChatMessage(message="I want to find a cruise")
        response_1 = handle_chat(chat_message_1)
        conversation_id = response_1.conversation_id

        chat_message_2 = ChatMessage(conversation_id=conversation_id, message="Alaska")
        response_2 = handle_chat(chat_message_2)

        # Third message to indicate flexible date
        chat_message_3 = ChatMessage(conversation_id=conversation_id, message="I don't care about the date")
        response_3 = handle_chat(chat_message_3)

        # Verify that the query to the database includes "next year"
        mock_query_chroma_db.assert_called_with("Alaska in next year")

        self.assertEqual(response_3.response, "Here are some cruises that match your criteria:")
        self.assertEqual(len(response_3.cruises), 1)
        self.assertEqual(response_3.cruises[0].cruise_id, "cruise2")

    def test_answers_general_question(self):
        chat_message = ChatMessage(message="What is the luggage allowance?")
        response = handle_chat(chat_message)
        self.assertIn("luggage allowance", response.response.lower())

if __name__ == '__main__':
    unittest.main()
