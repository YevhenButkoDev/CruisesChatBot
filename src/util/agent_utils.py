import time
import logging
import psycopg2
from contextlib import contextmanager
from typing import List, Any
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class AgentTimer:
    """Context manager for timing agent operations."""
    
    def __init__(self):
        self.timings = {}
    
    @contextmanager
    def time(self, operation_name: str):
        start = time.time()
        try:
            yield
        finally:
            self.timings[operation_name] = time.time() - start
    
    def print_summary(self):
        total = sum(self.timings.values())
        print(f"⏱️ Total time: {total:.2f}s")
        for operation, duration in self.timings.items():
            print(f"⏱️ {operation.replace('_', ' ').title()}: {duration:.2f}s")


class MessageHistoryManager:
    """Manages conversation history persistence."""
    
    def save_messages(self, messages: List[Any], thread_id: str):
        """Save messages to PostgreSQL history table."""
        try:
            import os
            conn = psycopg2.connect(os.getenv("POSTGRES_DB_URL"))
            cursor = conn.cursor()
            
            for msg in messages:
                msg_type = 1 if msg.type == 'human' else 2
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


class ConversationSummarizer:
    """Handles conversation summarization."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def summarize_conversation(self, agent, config) -> str:
        """Generate conversation summary using the agent."""
        summary_prompt = (
            "Summarize this conversation in 500-1000 symbols, "
            "the summary should include basic cruise information(name, ids, itinerary, prices, dates), "
            "focusing on key cruise search criteria and preferences, "
            "also mention human conversation language(en, ru, uk, etc)"
        )
        
        summary = agent.invoke({
            "messages": [SystemMessage(content=summary_prompt)]
        }, config)
        
        return summary["messages"][-1].content
