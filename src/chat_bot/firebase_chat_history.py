from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from google.cloud import firestore
import os
from typing import List


class FirestoreChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.collection_name = "chat_sessions"
        self.db = firestore.Client(database=os.getenv("FIRESTORE_DATABASE", "(default)"))

    @property
    def messages(self) -> List[BaseMessage]:
        doc_ref = self.db.collection(self.collection_name).document(self.session_id)
        doc = doc_ref.get()

        if not doc.exists:
            return []

        messages_data = doc.to_dict().get("messages", [])
        messages = []

        for msg_data in messages_data:
            if msg_data["type"] == "human":
                messages.append(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "ai":
                messages.append(AIMessage(content=msg_data["content"]))

        return messages

    def add_message(self, message: BaseMessage) -> None:
        doc_ref = self.db.collection(self.collection_name).document(self.session_id)

        message_data = {
            "type": "human" if isinstance(message, HumanMessage) else "ai",
            "content": message.content
        }

        # Create document if it doesn't exist, otherwise update
        doc_ref.set({
            "messages": firestore.ArrayUnion([message_data])
        }, merge=True)

    def clear(self) -> None:
        doc_ref = self.db.collection(self.collection_name).document(self.session_id)
        doc_ref.set({"messages": []})
