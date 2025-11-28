from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from typing import List, Any, Optional
import os
import logging

from src.agent_tools.advanced_api_search import search_cruises
from src.agent_tools.agent_tools import find_relevant_cruises, find_cruise_info, get_current_date
from src.util.agent_utils import AgentTimer, MessageHistoryManager, ConversationSummarizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CruiseAgent:
    """AI agent for cruise-related queries with conversation management."""

    def __init__(
        self,
        model_name: str = "gpt-5-mini",
        tools: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None
    ):
        load_dotenv()
        
        self.llm = ChatOpenAI(model=model_name)
        self.tools = tools or [search_cruises, find_cruise_info, get_current_date]
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        self.history_manager = MessageHistoryManager()
        self.summarizer = ConversationSummarizer(self.llm)

    def _default_system_prompt(self) -> str:
        return (
            """
            You are a cruise travel assistant. Your goal is to guide the user from having no idea what they want to choosing a specific cruise and cabin.
            LANGUAGE
            - Reply in the user’s language (en/ru/ua). Unknown → English.
            - Use minimal Markdown (bold + indentation). No emojis.
            - Keep answers brief unless listing cruise results.
            - Reduce response size to 2000 symbols maximum, but only when it is possible
            FLOW
            1) If the user is unsure what they want:
                 - Ask whether they prefer a sea or river cruise.
                 - If needed, briefly explain:
                     - Sea: big ships, oceans/seas, many activities, long routes.
                     - River: smaller ships, calm, cultural routes on rivers.
            2) For search:
                 - ALWAYS translate the user request to English internally.
                 - First use the vector database.
            3) Show user-friendly cruise info
               Never show IDs or system fields.
               If no results → politely inform the user.
            RULES
            - No hallucinations: use only data from RAG or fallback.
            - No revealing internal processes.
            """
        )

    def ask(self, user_message: str, thread_id: str = "default") -> List[Any]:
        timer = AgentTimer()
        config = {"configurable": {"thread_id": thread_id}}
        responses = []

        try:
            with timer.time("postgres_init"):
                with PostgresSaver.from_conn_string(os.getenv("POSTGRES_DB_URL", "")) as checkpointer:
                    
                    with timer.time("agent_creation"):
                        agent = self._create_agent(checkpointer)
                    
                    with timer.time("history_processing"):
                        input_messages = self._process_conversation_history(
                            checkpointer, config, thread_id, user_message, agent
                        )
                    
                    with timer.time("stream_processing"):
                        responses = self._stream_agent_response(agent, input_messages, config)

                    self.history_manager.save_messages([
                        HumanMessage(user_message),
                        responses[-1]
                    ], thread_id)
                    timer.print_summary()
                    
        except Exception as e:
            logger.error(f"❌ AI Agent error: {str(e)}")
            raise

        return responses

    def _create_agent(self, checkpointer):
        return create_agent(
            self.llm,
            tools=self.tools,
            checkpointer=checkpointer,
            system_prompt=self.system_prompt
        )

    def _process_conversation_history(self, checkpointer, config, thread_id, user_message, agent):
        state = checkpointer.get(config)
        
        if state and len(state['channel_values']['messages']) > 50:
            print("Summarizing chat history")

            summary_content = self.summarizer.summarize_conversation(agent, config)
            checkpointer.delete_thread(thread_id=thread_id)
            
            return [
                SystemMessage(content=summary_content),
                HumanMessage(content=user_message)
            ]
        
        return [HumanMessage(content=user_message)]

    def _stream_agent_response(self, agent, input_messages, config):
        responses = []
        for step in agent.stream({"messages": input_messages}, config, stream_mode="values"):
            responses.append(step["messages"][-1])
        return responses


if __name__ == "__main__":
    agent = CruiseAgent()
    agent.ask("Cruise to barcelona")
