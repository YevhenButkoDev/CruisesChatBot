from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any, Optional
import os
import logging
import time

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph_checkpoint_firestore import FirestoreSaver


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def _save_messages_to_history(self, messages: List[Any], thread_id: str):
        """Save messages to messages_history table before summarization."""
        try:
            import psycopg2
            conn = psycopg2.connect(os.getenv("POSTGRES_DB_URL"))
            cursor = conn.cursor()
            
            for msg in messages:
                msg_type = 1 if msg.type == 'human' else 2  # 1 for human, 2 for AI
                cursor.execute(
                    "INSERT INTO messages_history(msg_type, thread_id, message, created_at) VALUES (%s, %s, %s, now())",
                    (msg_type, thread_id, msg.content)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Saved {len(messages)} messages to history for thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Failed to save messages to history: {str(e)}")

    def _summarize_messages(self, messages: List[Any]) -> str:
        """Use AI to summarize the last 5 messages."""
        if len(messages) <= 5:
            return ""
        
        start_time = time.time()
        last_5 = messages[-5:]
        conversation = "\n".join([f"{'User' if msg.type == 'human' else 'Assistant'}: {msg.content}" for msg in last_5])
        
        summary_prompt = f"Summarize this conversation in 500-1000 symbols, focusing on key cruise search criteria and preferences, also mention human conversation language(en, ru, uk, etc):\n\n{conversation}"
        summary_response = self.llm.invoke([HumanMessage(content=summary_prompt)])
        
        elapsed = time.time() - start_time
        print(f"⏱️ Summarization: {elapsed:.2f}s")
        
        return f"Previous conversation summary: {summary_response.content}"

    def ask(self, user_message: str, thread_id: str = "default"):
        total_start = time.time()
        
        config = {"configurable": {"thread_id": thread_id}}
        responses = []

        try:
            checkpoint_start = time.time()
            DB_URI = os.getenv("POSTGRES_DB_URL", "")
            with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
                checkpoint_elapsed = time.time() - checkpoint_start
                print(f"⏱️ Firestore init: {checkpoint_elapsed:.2f}s")
                
                agent_start = time.time()
                agent = create_agent(
                    self.llm,
                    tools=self.tools,
                    checkpointer=checkpointer,
                    system_prompt=self.system_prompt
                )
                agent_elapsed = time.time() - agent_start
                print(f"⏱️ Agent creation: {agent_elapsed:.2f}s")

                history_start = time.time()
                state = checkpointer.get(config)

                if state and len(state['channel_values']['messages']) > 5:
                    print("Summarizing chat history")
                    # Save all messages to history before summarization
                    self._save_messages_to_history(state['channel_values']['messages'], thread_id)
                    
                    summary = agent.invoke({"messages": [SystemMessage(content="Summarize this conversation in 500-1000 symbols, the summary should include basic cruise information(name, ids, internary, prices, dates), focusing on key cruise search criteria and preferences, also mention human conversation language(en, ru, uk, etc)")]}, config)
                    summary_content = summary["messages"][-1]
                    checkpointer.delete_thread(thread_id=thread_id)

                    input_messages = [
                        SystemMessage(content=summary_content.content),
                        HumanMessage(content=user_message)
                    ]
                else:
                    input_messages = [HumanMessage(content=user_message)]
                
                history_elapsed = time.time() - history_start
                print(f"⏱️ History processing: {history_elapsed:.2f}s")

                stream_start = time.time()
                step_count = 0
                for step in agent.stream({"messages": input_messages}, config, stream_mode="values"):
                    step_count += 1
                    responses.append(step["messages"][-1])

                stream_elapsed = time.time() - stream_start
                total_elapsed = time.time() - total_start
                print(f"⏱️ Stream processing: {stream_elapsed:.2f}s")
                print(f"⏱️ Total time: {total_elapsed:.2f}s")
                
        except Exception as e:
            logger.error(f"❌ AI Agent error: {str(e)}")
            raise

        return responses


if __name__ == "__main__":
    agent = CruiseAgent()

    # Or collect responses programmatically
    agent.ask("Cruise to barcelona")
