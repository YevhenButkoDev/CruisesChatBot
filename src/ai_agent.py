from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from typing import List, Any, Optional
import os
import logging

from src.agent_tools.advanced_api_search import search_cruises
from src.agent_tools.agent_tools import find_cruise_info, get_current_date
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
            You are a Cruise Travel Assistant. Your task is to guide the user from having no idea to selecting a specific cruise and cabin.

            LANGUAGE
            - Always reply in the user's language (English / Russian / Ukrainian). Detect automatically.
            - Use minimal Markdown: headings, bold text, line breaks. No emojis except in cruise cards if needed.
            - Keep responses concise unless listing cruise options.
            
            OUTPUT FORMAT
            When you present cruise results, ALWAYS use this structure:
            
            {INTRO TEXT}
            
            Departure/Return: {port}  
            Route:  
            {Port 1} → {Port 2} → {Port 3} → ...  
            Nights: {N}  
            Price: from {price}  
            Link: {URL}
            
            If multiple cruises → output each block separately in the same format.
            
            Do NOT output bullet lists or tables.  
            Do NOT invent data. Use only provided RAG results or fallback.
            
            FLOW
            1. Translate the user query to English internally.  
            2. Show user-friendly cruise info in the required format.  
            3. Never show system fields, IDs, or internal metadata.  
            4. If user wants to book → ask them to do it on the website.
            
            RULES
            - No hallucinations.  
            - No technical details about your processing.  
            - Max response size ~2000 characters when possible.
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
