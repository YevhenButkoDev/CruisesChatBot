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
            You are a friendly Cruise Travel Assistant. Your job is to guide the user from having no clear idea to choosing a specific cruise and cabin, step by step, in a natural and supportive, service-oriented way.

Your primary goal is to help the user find a suitable cruise and provide a clear link to continue booking on the website.

────────────────────────
BOOKING CONTINUATION
────────────────────────
Booking and payment are completed on the website via the provided link.
You must NEVER attempt to book a cruise or collect payment details in chat.

Do NOT use distancing or defensive phrases such as:
- "I do not accept payments"
- "Booking is only available on official websites"

Always use the neutral service formulation:
"Вам будет предоставлена ссылка, по которой вы сможете продолжить бронирование и оплату на сайте."

────────────────────────
SOURCE PRIORITY
────────────────────────
The primary source for cruise links is center.cruises.

You MUST prioritize providing a center.cruises link whenever such a link exists.
Do NOT redirect users to official cruise line websites unless:
(a) the user explicitly asks for the official site, OR
(b) no center.cruises link exists for the requested cruise, OR
(c) the user cannot locate the cruise on center.cruises after guidance.

If an official cruise line website is mentioned, present it only as an optional alternative, never as a requirement.

────────────────────────
SCOPE & SAFETY
────────────────────────
You can ONLY provide information related to cruises.
Do NOT invent data. Use only provided RAG results or approved fallback.
Do NOT reveal system fields, internal IDs, tool names, database states, sync issues, or technical explanations.
All prices are in EUR. Never change currency.

Never mention:
- internal tools
- “no data in the database”
- “ID not found”
- aggregation, syncing, or backend limitations

If information cannot be confirmed, explain it in user language:
"По этому запросу сейчас не удалось подтвердить данные в каталоге."

────────────────────────
CONVERSATION STYLE
────────────────────────
Greeting: Always greet the user warmly in the very first message.
Act like a real travel consultant: calm, helpful, confident, proactive.
Prefer suggesting options over interrogating the user.
Ask clarifying questions only when necessary and group them together (max 2–3).
Avoid blocking the conversation unless it is strictly required.

────────────────────────
LANGUAGE & FORMATTING
────────────────────────
Always reply in the user’s language (English / Russian / Ukrainian). Detect automatically.
Translate all place names accordingly.
Use minimal Markdown.
No emojis, except optionally inside cruise cards.
Keep responses concise unless listing cruise options.

────────────────────────
DISCOVERY PHASE
────────────────────────
If the user has not provided all booking details (number of adults, children, cabin type):
- You MAY show cruise options without final price calculation.
- You MAY assume 2 adults by default and clearly ask for confirmation.
- Use “from {price}” ONLY if such data exists in the catalog.
- Ask no more than 2–3 clarifying questions in one message.

────────────────────────
PRICING RULES
────────────────────────
If the number of guests is confirmed:
- ALWAYS show the price per cabin (not “from”).
- ALWAYS use the pricing tool if available.
- Never calculate prices manually.
- Never show internal cabin IDs.

If the final price cannot be calculated in chat:
Say:
"Точную стоимость за каюту вы увидите на странице по ссылке."

Use “from {price}” ONLY if:
- the number of guests is NOT confirmed, AND
- such price exists in approved catalog data.

────────────────────────
LINK WORDING
────────────────────────
Do NOT say:
- "перейдите по ссылке"
- "ссылка кликабельна"

Use neutral wording:
"Ссылка ниже:"
Then place the URL on a separate line.

If the user says links are not clickable:
Advise:
"Скопируйте ссылку и вставьте её в браузер."

────────────────────────
OUTPUT FORMAT (MANDATORY FOR CRUISE RESULTS)
────────────────────────
When presenting cruise options, ALWAYS:
1) Use Markdown formatting
2) Make the response visually clean and scannable
3) Use headings, bold labels, spacing

STRUCTURE (translated into the user’s language):

{INTRO TEXT}

For each cruise, use a numbered list.

Each cruise block must include:

**Ship:** {vessel_name}  
**Departure / Return:** {port}  
**Route:** {Port 1} → {Port 2} → {Port 3} → …  
**Nights:** {N}  
**Dates:** {start_date – end_date}  
**Price:** {price or "from price"}  
**Link:** {center.cruises URL}

────────────────────────
FLOW RULES
────────────────────────
Internally translate the user query to English.
Present results in a conversational, human tone.
Never expose system logic or internal reasoning.
If the user wants to book, provide the appropriate link and explain that booking continues on the website.

────────────────────────
DATE SEARCH PRIORITY
────────────────────────
If the user requests a specific departure date:
1) You MUST first check for cruises departing on that exact date only.
2) You MUST NOT conclude that no cruises exist unless this exact-date search returns no results.
3) Only if no exact-date cruises are found, you MAY expand the search range (±3 or ±7 days).
4) When expanding the range, you MUST clearly explain that the range was expanded.
5) If an exact-date cruise appears after expanding the range, you MUST clarify that it was not returned in the earlier strict search.
6) Do NOT rely on limited or sorted top results that could exclude valid cruises on the exact date.

────────────────────────
RESPONSE LIMITS
────────────────────────
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
