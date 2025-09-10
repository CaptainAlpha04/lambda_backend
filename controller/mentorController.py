import google.generativeai as genai
from google.generativeai import types
import os
import dotenv 
import uuid
from datetime import datetime
from . import supabase  # Import the supabase client from __init__.py
from model.mentor_chats import MentorChatModel

dotenv.load_dotenv()

class Mentor:
    def __init__(self, userId):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.supabase = supabase  # Use the configured supabase client
        
        # Initialize the chat model and ensure table exists
        self.chat_model = MentorChatModel(self.supabase)
    
    def chat_with_mentor(self, userId, message, chat_id=None):
        try:
            # Get or create chat session
            if chat_id: 
                # Use specific chat if provided
                chat = self.chat_model.get_chat_by_id(chat_id)
                if not chat:
                    return "Sorry, the specified chat session was not found."
            else:
                # Get or create new chat session
                chat = self.chat_model.get_or_create_chat(userId)
                if not chat:
                    print(chat)
                    return "Sorry, there was an error creating chat session."
            
            current_chat_id = chat['id']
            
            # Get conversation history to provide context
            conversation_history = self.chat_model.get_conversation_history(userId, current_chat_id)
            
            # Build context from previous messages (last 10 exchanges for context)
            context_messages = []
            for exchange in conversation_history[-10:]:  # Last 10 exchanges
                context_messages.append(f"User: {exchange.get('user_message', '')}")
                context_messages.append(f"Assistant: {exchange.get('mentor_response', '')}")
            
            # Prepare the full prompt with context
            system_instruction = os.getenv("MENTOR_SYSTEM_INSTRUCTION", "You are a helpful AI mentor.")
            context_text = "\n".join(context_messages) if context_messages else ""
            
            full_message = f"{system_instruction}\n\nPrevious conversation:\n{context_text}\n\nUser: {message}"
            
            # Generate AI response
            response = self.model.generate_content(
                contents=full_message,
                generation_config=types.GenerationConfig(
                    # Add other config params here if needed
                )
            )
            
            ai_response = response.text
            
            # Save the new message exchange to conversation
            print(f"Attempting to save conversation to chat ID: {current_chat_id}")
            saved_conversation = self.chat_model.add_message_to_conversation(
                chat_id=current_chat_id,
                user_message=message,
                mentor_response=ai_response
            )
            
            if saved_conversation:
                print("Conversation saved successfully")
            else:
                print("Failed to save conversation, but continuing...")
                # Let's also try to verify the chat exists
                existing_chat = self.chat_model.get_chat_by_id(current_chat_id)
                if existing_chat:
                    print(f"Chat exists in database: {existing_chat['id']}")
                else:
                    print("Chat does not exist in database!")
            
            return ai_response
            
        except Exception as e:
            print(f"Error in chat_with_mentor: {e}")
            return "Sorry, there was an error processing your request."
    
    def get_chat_history(self, userId, limit=50):
        """Retrieve chat history for a user"""
        return self.chat_model.get_conversation_history(userId)
