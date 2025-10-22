from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory.chat_message_histories import FirestoreChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import chromadb
from datetime import datetime, timedelta
import json


class CruiseChatBot:
    def __init__(self, openai_api_key, session_id, chroma_db_path="./chroma_data"):
        self.llm = OpenAI(openai_api_key=openai_api_key, temperature=0.3)
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.chroma_client.get_collection("cruise_collection")
        
        # Initialize Firestore chat history
        self.chat_history = FirestoreChatMessageHistory(
            session_id=session_id,
            collection_name="chat_sessions"
        )
        self.memory = ConversationBufferMemory(
            chat_memory=self.chat_history,
            return_messages=True
        )
        
        # Intent recognition prompt
        self.intent_prompt = PromptTemplate(
            input_variables=["chat_history", "user_message"],
            template="""
            Chat History: {chat_history}
            
            Analyze the user message and determine if they want to find a cruise.
            Extract the following information if available:
            - destination (required for cruise search)
            - date_range (optional)
            - additional_details (any other preferences)
            
            User message: {user_message}
            
            Respond with JSON format:
            {{"intent": "find_cruise" or "other", "destination": "extracted destination or null", "date_range": "extracted dates or null", "additional_details": "other preferences or null"}}
            """
        )
        
        # Response generation prompts
        self.destination_request_prompt = PromptTemplate(
            input_variables=["chat_history", "user_message"],
            template="""
            Chat History: {chat_history}
            
            The user wants to find a cruise but didn't specify a destination. Politely ask them to specify their desired cruise destination. 
            User message: {user_message}
            """
        )
        
        self.general_response_prompt = PromptTemplate(
            input_variables=["chat_history", "user_message"],
            template="""
            Chat History: {chat_history}
            
            Answer the user's question helpfully. If it's not cruise-related, still be helpful but mention you specialize in cruise information. 
            User message: {user_message}
            """
        )
        
        self.intent_chain = LLMChain(llm=self.llm, prompt=self.intent_prompt)
        self.destination_chain = LLMChain(llm=self.llm, prompt=self.destination_request_prompt)
        self.general_chain = LLMChain(llm=self.llm, prompt=self.general_response_prompt)
    
    def get_default_date_range(self):
        """Return next calendar year as default date range"""
        next_year = datetime.now().year + 1
        return f"January 1, {next_year} to December 31, {next_year}"
    
    def search_cruises(self, destination, date_range=None, additional_details=None):
        """Search Chroma DB for cruise information"""
        query_text = f"cruise to {destination}"

        if additional_details:
            query_text += f" {additional_details}"
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=5
        )
        
        return results
    
    def process_message(self, user_message):
        """Process user message and return appropriate response"""
        try:
            # Save user message to history
            self.chat_history.add_user_message(user_message)
            
            # Load memory variables
            memory_variables = self.memory.load_memory_variables({})
            chat_history_str = memory_variables.get('history', '')

            # Get intent and extract information
            intent_response = self.intent_chain.run(chat_history=chat_history_str, user_message=user_message)
            intent_data = json.loads(intent_response.strip())
            
            if intent_data["intent"] == "find_cruise":
                destination = intent_data.get("destination")
                
                if not destination:
                    # Use LLM to politely ask for destination
                    response_message = self.destination_chain.run(chat_history=chat_history_str, user_message=user_message)
                    self.chat_history.add_ai_message(response_message)
                    return {"intent": "find_cruise", "message": response_message}
                
                date_range = intent_data.get("date_range") or self.get_default_date_range()
                additional_details = intent_data.get("additional_details")
                
                # Search for cruises
                search_results = self.search_cruises(destination, date_range, additional_details)
                
                response = {
                    "intent": "find_cruise",
                    "destination": destination,
                    "date_range": date_range,
                    "results": search_results
                }
                
                # Save AI response to history
                self.chat_history.add_ai_message(json.dumps(response))
                return response
            else:
                # Use LLM to answer other questions
                response_message = self.general_chain.run(chat_history=chat_history_str, user_message=user_message)
                self.chat_history.add_ai_message(response_message)
                return {"intent": "other", "message": response_message}
                
        except Exception as e:
            error_response = f"Error processing request: {str(e)}"
            self.chat_history.add_ai_message(error_response)
            return {"error": error_response}

