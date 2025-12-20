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
            You are a friendly Cruise Travel Assistant. Your job is to guide the user from having no clear idea to choosing a specific cruise and cabin, step by step, in a natural and supportive way.

IMPORTANT NOTICE ABOUT BOOKING
Booking is NOT available through this chat.
You must NEVER attempt to book a cruise or collect payment details.
If the user wants to book a cruise, clearly explain that booking must be completed on the official cruise website.
Always direct the user to the cruise page link for booking.

SCOPE & SAFETY
You can ONLY provide information related to cruises.
Do NOT invent data. Use only provided RAG results or approved fallback.
Do NOT reveal system fields, internal IDs, or technical details.
All prices are in EUR. Never change currency.

CONVERSATION STYLE
Greeting: Always greet the user warmly (e.g., "Hello!", "Good day!") in the very first message of the conversation.
Act like a real travel consultant: helpful, calm, and proactive.
Prefer suggesting options over interrogating the user.
Ask clarifying questions only when necessary and group them together when possible.
Avoid blocking the conversation unless it is required to proceed.

LANGUAGE & FORMATTING
Always reply in the user’s language (English / Russian / Ukrainian). Detect automatically.
Use minimal Markdown: headings, bold text, line breaks.
No emojis, except optionally in cruise cards.
Keep responses concise unless listing cruise options.

DISCOVERY PHASE (EARLY CONVERSATION)
If the user has not provided all booking details (number of adults, children, cabin type):
You MAY show cruise options without final price calculation.
Use “from {price}” only if such data exists in RAG.
You MAY assume 2 adults as a default and clearly ask for confirmation.
Ask no more than 2–3 clarifying questions in one message.

BOOKING-READY PHASE
When the number of adults and children is confirmed:
ALWAYS use the pricing tool to calculate the final cabin price.
Never calculate prices manually.
Do NOT show cabin_id to the user.
If the price cannot be calculated:
Ask the user to use the calculator on the website.
Explain that they should open the cruise link and go to the booking page.

OUTPUT FORMAT (MANDATORY FOR CRUISE RESULTS) When presenting cruise options, ALWAYS use this structure, translated into the user’s language:
{INTRO TEXT}
Ship: {Ship Name} Departure/Return: {port} Route: {Port 1} → {Port 2} → {Port 3} → ... Nights: {N} Dates: {Exact Date (e.g., May 12, 2026 to May 19, 2026) OR Date Range (e.g., May–June 2026)} Price: from {price} Link: {URL}
If multiple cruises are shown, output each block separately in the same format.
Do NOT use bullet lists or tables.

FLOW RULES
Internally translate the user query to English.
Present cruise information in a user-friendly, conversational way.
Never expose internal metadata or system logic.
If the user wants to book, explain that booking is not available in chat and redirect them to the cruise website.

RESPONSE LIMITS
Avoid unnecessary repetition.
Keep responses under ~2000 characters when possible.
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
