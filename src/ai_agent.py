from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.agents import create_agent
from typing import List, Dict, Any, Optional
from langdetect import detect
import os
from langgraph_checkpoint_firestore import FirestoreSaver


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

        self.tools = tools or [find_relevant_cruises, find_cruise_info, get_current_date]
        self.system_prompt = system_prompt or (
            "You are an intelligent travel assistant.\n"
            "- Always query the cruise tool in ENGLISH, even if the user is speaking another language.\n"
            "- Always respond in the user's language, but limit response answer languages to en, ru and ua\n"
            "- If no relevant cruises are found, politely inform the user in their language."
        )

    def ask(self, user_message: str, thread_id: str = "default"):
        config = {"configurable": {"thread_id": thread_id}}
        input_message = {"role": "user", "content": user_message}
        responses = []

        with FirestoreSaver.from_conn_info(project_id=os.environ.get("FIRESTORE_PROJECT_ID"), checkpoints_collection='langchain', writes_collection='langchain_writes') as checkpointer:
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
    print(agent._wrap_message_with_language("cruise to barcelona"))
