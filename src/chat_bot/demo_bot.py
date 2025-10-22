from typing_extensions import TypedDict
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import chromadb

from src.chat_bot.firebase_chat_history import FirestoreChatMessageHistory

load_dotenv()

# === SETUP ===
llm = ChatOpenAI(model="gpt-4o-mini")


class MyGraphState(TypedDict):
  input: str
  destination: str


# === CHAINS ===
extract_prompt = PromptTemplate(
    input_variables=["input"],
    template="Extract the cruise destination mentioned in the user query if any. "
             "If none, respond with 'unknown'. Query: {input}"
)
extract_chain = LLMChain(llm=llm, prompt=extract_prompt)


def find_cruise(state):
    destination = state["destination"]
    if "unknown" in destination.lower():
        return {"result": "Please tell me where you'd like to cruise to!"}

    chroma_client = chromadb.PersistentClient(path="../chroma_data")
    collection = chroma_client.get_collection("cruise_collection")

    docs = collection.query(
        query_texts=[destination],
        n_results=5
    )
    if not docs:
        return {"result": f"Sorry, no cruises found for {destination}."}
    return {"result": f"Found a cruise for {destination}: {docs[0].metadata['details']}"}


offtopic_prompt = PromptTemplate(
    input_variables=["input"],
    template=(
        "You are a cruise booking assistant. The user asked: {input}\n"
        "If the question is unrelated to cruises, answer helpfully but end with this note:\n"
        "'(Note: I specialize in cruises, so this might be outside my expertise.)'"
    )
)
offtopic_chain = LLMChain(llm=llm, prompt=offtopic_prompt)

# === LANGGRAPH SETUP ===
def router(state):
    if "cruise" in state["input"].lower():
        return "find_cruise"
    return "offtopic"

graph = StateGraph(MyGraphState)
graph.add_node("extract_destination", lambda s: {"destination": extract_chain.run(s["input"])})
graph.add_node("find_cruise", find_cruise)
graph.add_node("offtopic", lambda s: {"result": offtopic_chain.run(s)})
graph.add_node("router", router)

graph.add_edge("find_cruise", END)
graph.add_edge("offtopic", END)
graph.set_entry_point("extract_destination")

cruise_agent = graph.compile()

# === FASTAPI SERVER ===
app = FastAPI(title="Cruise Finder Agent")


class ChatRequest(BaseModel):
    session_id: str
    user_input: str


@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests and persist to Firestore."""
    history = FirestoreChatMessageHistory(session_id=request.session_id)

    # Build history context string (optional - you can feed to prompt later)
    past_messages = "\n".join(
        [f"User: {m.content}" if m.type == "human" else f"AI: {m.content}" for m in history.messages]
    )

    # Call the agent
    result = cruise_agent.invoke({
        "input": request.user_input,
        "chat_history": past_messages
    })

    response = result["result"]

    # Save both sides of the conversation
    from langchain.schema import HumanMessage, AIMessage
    history.add_message(HumanMessage(content=request.user_input))
    history.add_message(AIMessage(content=response))

    return {"response": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
