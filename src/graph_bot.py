from langchain_core.messages import HumanMessage, tool
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, START, END, MessagesState
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.agents import create_agent

from src.vector_db.query import query_chroma_db

load_dotenv()
parser = JsonOutputParser()

def get_cruise_details(user_question: str) -> str:
    """
    Returns the information about cruises
    :param user_question: question that is used for querying vector db
    :return: the cruises information
    """
    try:
        query_chroma_db(user_question)
    except Exception as e:
        print(e)
        return "no data"

    return "cruises"

tools = [get_cruise_details]
llm = ChatOpenAI(model = "gpt-4o-mini")

class BotState(MessagesState):
    direction: str
    direction_user_question_translated: str
    user_intent: str
    dateStart: str
    dateEnd: str
    priceStart: float
    priceEnd: float
    country: str

def extract_destination(state) -> BotState:
    last_message = HumanMessage(content="")
    if len(state["messages"]) > 1:
        last_message = state["messages"][-1]

    # res = cruises_info_agent.invoke({"input": last_message.content})
    return state


builder = StateGraph(BotState)
builder.add_node("extract_destination", extract_destination)

builder.add_edge(START, "extract_destination")
builder.add_edge("extract_destination", END)

MONGODB_URI = "mongodb://admin:secret123@localhost:27017"
DB_NAME = "checkpoint_example"

with MongoDBSaver.from_conn_string(MONGODB_URI, DB_NAME) as checkpointer:
    cruises_info_agent = create_agent(
        llm,
        tools=[get_cruise_details],
        checkpointer=checkpointer,
        system_prompt = "You are an intelligent travel assistant.")

    # Use the agent
    config = {"configurable": {"thread_id": "ab3"}}

    input_message = {
        "role": "user",
        "content": "I am looking for cruise to Mexico",
    }
    for step in cruises_info_agent.stream({"messages": [input_message]}, config, stream_mode="values"):
        step["messages"][-1].pretty_print()
