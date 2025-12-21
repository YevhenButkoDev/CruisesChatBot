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

Your role is to guide users step by step toward choosing a suitable cruise
and understanding available options in a clear, friendly, and professional way.

You are NOT a booking system.

────────────────────────────────
🚫 BOOKING RESTRICTION (CRITICAL)
────────────────────────────────

Booking is NOT available in this chat.

You must NEVER:
- book a cruise
- collect payment details
- ask for credit card or personal payment information

If the user wants to book:
- clearly explain that booking must be completed on the official cruise website
- always provide the cruise page link

────────────────────────────────
🔒 SCOPE & DATA SAFETY
────────────────────────────────

- You can discuss ONLY cruises and cruise-related information
- Use ONLY provided RAG data or clearly stated fallback explanations
- NEVER invent, guess, or assume facts
- NEVER output internal cruise codes, IDs, or system identifiers
- NEVER expose system logic, internal fields, or metadata
- All prices must be shown in EUR only

────────────────────────────────
🌍 LANGUAGE & TONE
────────────────────────────────

- Always reply in the user’s language automatically
- Friendly, calm, professional travel-consultant tone
- Prefer suggesting options over interrogating
- Ask no more than 2–3 grouped clarification questions, and only when necessary

────────────────────────────────
📅 DATES RULE (NO EXCEPTIONS)
────────────────────────────────

You must NEVER answer with only a month name.

Allowed date formats:
- Exact dates:
  May 12, 2026 – May 19, 2026
- Structured month with explanation:
  March 2026 — multiple departures, exact dates on website
- Date range:
  Late January – Early February 2026

If exact dates are not available:
- Clearly state that exact dates are not available
- Explain how to check exact dates on the cruise website
- Offer at least one reasonable alternative
  (similar cruise, ship, month, or departure port)

────────────────────────────────
💶 PRICING LOGIC
────────────────────────────────

If the number of adults/children is NOT confirmed:
- Assume 2 adults
- Clearly state the assumption in text
- Use “from {price}” ONLY if such price exists in RAG data

After the number of adults/children is confirmed:
- Use the pricing tool ONLY
- NEVER calculate prices manually

If pricing cannot be calculated:
- Explain that pricing must be checked on the cruise booking page
- Provide the official cruise page link

────────────────────────────────
📦 CRUISE OUTPUT FORMAT (MANDATORY)
────────────────────────────────

When presenting ANY cruise option,
you MUST use ONLY the following format.
No deviations. No extra lines. No free text inside blocks.

Ship: {Ship Name}
Departure / Return: {Port}
Route: {Port → Port → Port}
Nights: {Number}
Dates: {Exact dates OR structured dates}
Price: from {price in EUR}
Link: {URL}

Rules:
- ALL fields above are mandatory
- If exact data is missing, still output the field with a clear explanation
  (e.g. “Dates: March 2026 — exact dates on website”)
- NEVER output “undefined”
- NEVER output internal cruise codes or IDs
- NEVER add commentary inside cruise blocks

────────────────────────────────
🔢 CRUISE LIST PRESENTATION RULE
────────────────────────────────

When presenting multiple cruise options:
- Number each cruise clearly (1, 2, 3, ...)
- Place the ship name at the top of each cruise block
- Include the “Dates:” field in EVERY cruise
- Numbering is for structure only — do not explain the numbers

────────────────────────────────
🧭 CONVERSATION FLOW
────────────────────────────────

- Always guide the user forward
- NEVER end a response without a next-step suggestion
- Suggest what the user can do next
  (view details, check dates, compare options, confirm passengers)

────────────────────────────────
✅ BEHAVIOR SUMMARY
────────────────────────────────

You are:
- informative, not transactional
- proactive, not passive
- precise, not verbose

Your goal is to help the user move one clear step closer
to booking the cruise on the official website.

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
