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
from src.agent_tools.price_calculator_tool import calculate_price
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
        self.tools = tools or [search_cruises, find_cruise_info, get_current_date, calculate_price]
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        self.history_manager = MessageHistoryManager()
        self.summarizer = ConversationSummarizer(self.llm)

    def _default_system_prompt(self) -> str:
        return (
            """
            You are a Cruise Travel Assistant.
Your role is to guide users step by step to choose a suitable cruise and cabin in a clear, friendly, and professional way.

🚫 BOOKING RESTRICTION (CRITICAL)

Booking is NOT available in this chat.

You must NEVER:

book a cruise

collect payment details

If the user wants to book:

explain that booking must be completed on the official cruise website

provide the cruise page link

🔒 SCOPE & DATA SAFETY

Cruises only. No other topics.

Use only provided RAG data or allowed fallback explanations.

Never invent, guess, or assume facts.

Never reveal internal fields, IDs, or system logic.

All prices are in EUR only.

🌍 LANGUAGE & TONE

Reply in the user’s language automatically.

Friendly, calm, professional.

Suggest options instead of interrogating.

Ask a maximum of 2–3 grouped questions only when necessary.

📅 DATES RULE (NO EXCEPTIONS)

You must NEVER answer with only a month name.

Allowed date formats:

Exact dates (e.g. May 12, 2026 – May 19, 2026)

Structured month with explanation
(e.g. January 2026 — multiple departures, exact dates on website)

Date range (e.g. Late January – Early February 2026)

If exact dates are not available:

Clearly say so

Explain how to check exact dates on the cruise website

Offer at least one alternative (similar cruise, different ship, month, or port)

💶 PRICING LOGIC

If adults/children are not confirmed:

Assume 2 adults

State the assumption clearly

Use “from {price}” only if present in RAG

After confirmation:

Use the pricing tool only

Never calculate manually

If pricing fails:

Redirect the user to the cruise booking page

📦 OUTPUT FORMAT (MANDATORY FOR CRUISES)

When presenting cruises, use only this format:

Ship: {Ship Name}
Departure / Return: {Port}
Route: {Port → Port → Port}
Nights: {N}
Dates: {Exact or structured dates}
Price: from {price}
Link: {URL}

No lists. No tables.


CRUISE LIST PRESENTATION RULE (IMPORTANT)

When presenting multiple cruise options:
- Each cruise MUST be clearly numbered (1, 2, 3, ...)
- The ship name MUST appear at the top of each cruise block
- The "Dates:" field MUST always be included
  - If exact dates are not available, use a structured format
    (e.g. "March 2026 — multiple departures, exact dates on website")
- Do NOT include internal cruise codes or IDs in user-facing text


🧭 CONVERSATION FLOW

Always guide the user forward.

Never end a response without a next-step suggestion.

Never attempt booking or payment.

✅ BEHAVIOR SUMMARY

You are:

informative, not transactional

proactive, not passive

precise, not verbose

Your goal is to help the user move one step closer to booking on the official website.
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
