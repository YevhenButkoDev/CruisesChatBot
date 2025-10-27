from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.agents import create_agent
from typing import List, Dict, Any, Optional
from langdetect import detect
import os

from src.agent_tools.agent_tools import (
    find_relevant_cruises,
    find_cruise_info,
    get_current_date
)


class CruiseAgent:
    """
    A reusable class that creates and manages a LangChain AI agent
    for querying and interacting with cruise-related data.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        mongodb_uri: str = "mongodb://admin:secret123@localhost:27017",
        db_name: str = "checkpoint_example",
        tools: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the CruiseAgent with model, MongoDB checkpointing, and available tools.

        :param model_name: Name of the OpenAI model to use.
        :param mongodb_uri: MongoDB connection string.
        :param db_name: MongoDB database name for storing checkpoints.
        :param tools: List of tools (functions) available to the agent.
        :param system_prompt: Optional custom system prompt for the agent.
        """
        load_dotenv()

        self.llm = ChatOpenAI(model=model_name)
        # Use environment variables if no values are provided
        self.mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://admin:secret123@localhost:27017")
        self.db_name = os.environ.get("MONGO_DB_NAME", "checkpoint_example")

        self.tools = tools or [find_relevant_cruises, find_cruise_info, get_current_date]
        self.system_prompt = system_prompt or (
            "You are an intelligent travel assistant.\n"
            "- Always query the cruise tool in ENGLISH, even if the user is speaking another language.\n"
            "- Always respond in the user's language.\n"
            "- If no relevant cruises are found, politely inform the user in their language."
        )

    def _detect_language(self, text: str) -> str:
        """Detect the language of the input text."""
        try:
            return detect(text)
        except:
            return "en"  # Default to English if detection fails

    def _wrap_message_with_language(self, user_message: str) -> str:
        """Wrap user message with detected language information."""
        detected_lang = self._detect_language(user_message)
        return f"User message language: {detected_lang}\nUser message: {user_message}"

    def ask(self, user_message: str, thread_id: str = "default"):
        # Wrap message with language detection
        wrapped_message = self._wrap_message_with_language(user_message)
        
        config = {"configurable": {"thread_id": thread_id}}
        input_message = {"role": "user", "content": wrapped_message}
        responses = []

        with MongoDBSaver.from_conn_string(self.mongodb_uri, self.db_name) as checkpointer:
            agent = create_agent(
                self.llm,
                tools=self.tools,
                checkpointer=checkpointer,
                system_prompt=self.system_prompt
            )

            for step in agent.stream({"messages": [input_message]}, config, stream_mode="values"):
                responses.append(step["messages"][-1])

        # return responses[-1]["content"]
        return responses


if __name__ == "__main__":
    agent = CruiseAgent()

    # Or collect responses programmatically
    responses = agent.ask(user_message = "is it possible to get a cruise from barcelona to usa?", thread_id = "abc108")
    for msg in responses:
        print(msg)