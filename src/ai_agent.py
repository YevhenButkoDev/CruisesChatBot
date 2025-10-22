from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.agents import create_agent
from datetime import date

from src.data_extraction.db import get_db_connection
from src.util.util import validate_and_correct_date_range
from src.vector_db.query import query_chroma_db, get_chunks_by_meta

load_dotenv()


def filter_cruises_by_date_range(date_from: date, date_to: date):
    """
    Fetches all enabled cruise IDs from the mv_cruise_info materialized view
    that fall within the specified date range.

    :param date_from: Start date (inclusive)
    :param date_to: End date (inclusive)
    :return: List of enabled cruise IDs within the given date range.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT m.cruise_id
        FROM mv_cruise_info m
        JOIN mv_cruise_date_range_info mcdri 
            ON mcdri.cruise_id = m.cruise_id
        WHERE m.enabled = TRUE
          AND (
                (mcdri.cruise_date_range_info->'dateRange'->>'begin_date')::date <= %s
                AND (mcdri.cruise_date_range_info->'dateRange'->>'end_date')::date >= %s
              )
    """

    # Execute safely with parameters
    cur.execute(query, (date_to, date_from))

    cruise_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return cruise_ids

def get_current_date():
    """
    Function provides current date
    :return: current date
    """
    return date.today().isoformat()

def find_cruise_info(cruise_id: str):
    """
        Retrieves detailed information for a specific cruise based on its unique cruise_id
        from the Chroma vector database.
        :param cruise_id unique cruise identifier
    """
    try:
        results = get_chunks_by_meta({ "cruise_id": cruise_id })
        print(results)
        return results
    except Exception as e:
        return "no data"

def find_relevant_cruises(user_question: str, date_from: str, date_to: str) -> str:
    """
    Retrieves cruise information relevant to the user's question within a specified date range.

    :param user_question: A natural-language question or search query used to retrieve relevant cruise data from the vector database.
    :param date_from: The start date of the desired cruise range (inclusive).
                      Must be in ISO format 'YYYY-MM-DD' (e.g., '2025-10-01').
                      If not provided or empty, no lower bound on the date range is applied.
    :param date_to: The end date of the desired cruise range (inclusive).
                    Must be in ISO format 'YYYY-MM-DD' (e.g., '2025-10-15').
                    If not provided or empty, no upper bound on the date range is applied.
    :return: A list of parsed cruise details including cruise_id, cruise_info, metadata, and relevance score.
             Returns "no data" if no results are found or an error occurs.
    """
    try:
        range = validate_and_correct_date_range(date_from, date_to)
        ids = []
        if range[2]:
            ids = filter_cruises_by_date_range(range[0], range[1])

        results = query_chroma_db(query_text=user_question, cruise_ids=ids)
        parsed_results = []
        for i, doc_id in enumerate(results["ids"][0]):
            parsed_results.append({
                "cruise_id": doc_id,
                "cruise_info": results["documents"][0][i],
                "meta": results["metadatas"][0][i],
                "score": results["distances"][0][i]
            })
        return parsed_results
    except Exception as e:
        print(e)
        return "no data"

tools = [find_relevant_cruises]
llm = ChatOpenAI(model = "gpt-4o-mini")
MONGODB_URI = "mongodb://admin:secret123@localhost:27017"
DB_NAME = "checkpoint_example"

with MongoDBSaver.from_conn_string(MONGODB_URI, DB_NAME) as checkpointer:
    cruises_info_agent = create_agent(
        llm,
        tools=[find_relevant_cruises, find_cruise_info, get_current_date],
        checkpointer=checkpointer,
        system_prompt = """You are an intelligent travel assistant. 
- Always query the cruise tool in ENGLISH, even if the user is speaking in another language. 
- Always respond to the user in the language they are using.
- If the tool returns no relevant data, politely inform the user in their language that no cruises were found.""")

    # Use the agent
    config = {"configurable": {"thread_id": "ac3"}}

    input_message = {
        "role": "user",
        "content": "tell me more about first one",
        # "content": "find cruises to france for me"
    }
    for step in cruises_info_agent.stream({"messages": [input_message]}, config, stream_mode="values"):
        step["messages"][-1].pretty_print()