from supabase import Client
import logging
import json
from typing import List, Dict, Optional
import uuid
from datetime import datetime

class MentorChatModel:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = "mentor_chats"
        # Test the connection
        self.test_connection()
    
    def test_connection(self):
        """Test the Supabase connection and table access"""
        try:
            print("Testing Supabase connection...")
            result = self.supabase.table(self.table_name).select("id").limit(1).execute()
            print(f"Connection test successful. Table access: OK")
        except Exception as e:
            print(f"Connection test failed: {e}")
    
    def get_chat_by_id(self, chat_id: str) -> Optional[Dict]:
        """Get a specific chat by its ID"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("id", chat_id)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting chat by ID: {e}")
            return None
    
    def get_or_create_chat(self, user_id: str, title: Optional[str] = None) -> Optional[Dict]:
        """Get existing chat or create a new one for the user"""
        try:
            # Try to get the most recent chat for this user
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]
            else:
                # Create new chat if none exists
                return self.create_new_chat(user_id, title)
                
        except Exception as e:
            print(f"Error getting or creating chat: {e}")
            return None
    
    def create_new_chat(self, user_id: str, title: Optional[str] = None) -> Optional[Dict]:
        """Create a new chat session"""
        try:
            # Check if user_id is in valid UUID format
            try:
                uuid.UUID(user_id)
            except ValueError:
                print(f"Invalid UUID format for user_id: {user_id}")
                return None
            
            # Check if user exists in users table
            user_check = self.supabase.table("users").select("id").eq("id", user_id).execute()
            if not user_check.data:
                print(f"User {user_id} does not exist in users table")
                return None
            
            chat_data = {
                "user_id": user_id,
                "title": title or "New Conversation",
                "conversation": []
            }
            
            print(f"Creating new chat for user: {user_id}")
            result = self.supabase.table(self.table_name).insert(chat_data).execute()
            
            if result.data and len(result.data) > 0:
                print(f"Successfully created chat with ID: {result.data[0]['id']}")
                return result.data[0]
            else:
                print("No data returned from insert operation")
                print(f"Full result: {result}")
                return None
        except Exception as e:
            print(f"Error creating new chat: {e}")
            print(f"Error type: {type(e)}")
            return None
    
    def add_message_to_conversation(self, chat_id: str, user_message: str, mentor_response: str) -> bool:
        """Add a new message exchange to the conversation"""
        try:
            print(f"Adding message to chat ID: {chat_id}")
            
            # Get current chat
            chat_result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("id", chat_id)\
                .execute()
            
            if not chat_result.data:
                print(f"Chat with id {chat_id} not found")
                return False
            
            chat = chat_result.data[0]
            conversation = chat.get("conversation", [])
            print(f"Current conversation has {len(conversation)} messages")
            
            # Add new message exchange
            new_exchange = {
                "id": str(uuid.uuid4()),
                "user_message": user_message,
                "mentor_response": mentor_response,
                "timestamp": datetime.now().isoformat()
            }
            
            conversation.append(new_exchange)
            print(f"Adding new exchange, conversation now has {len(conversation)} messages")
            
            # Update the chat with new conversation
            update_result = self.supabase.table(self.table_name)\
                .update({"conversation": conversation})\
                .eq("id", chat_id)\
                .execute()
            
            if update_result.data and len(update_result.data) > 0:
                print("Successfully updated conversation in database")
                return True
            else:
                print("Update operation returned no data")
                return False
            
        except Exception as e:
            print(f"Error adding message to conversation: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, chat_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history for a user or specific chat"""
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            if chat_id:
                query = query.eq("id", chat_id)
            else:
                query = query.eq("user_id", user_id)
            
            result = query.order("created_at", desc=True).execute()
            
            if result.data:
                # Return the conversation array from the most recent chat
                return result.data[0].get("conversation", [])
            return []
            
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def get_user_chats(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get all chats for a user"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("id, title, created_at")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data or []
        except Exception as e:
            print(f"Error retrieving user chats: {e}")
            return []
    
    def update_chat_title(self, chat_id: str, title: str) -> bool:
        """Update the title of a chat"""
        try:
            result = self.supabase.table(self.table_name)\
                .update({"title": title})\
                .eq("id", chat_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating chat title: {e}")
            return False

    def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Delete a specific chat session"""
        try:
            # First verify that the chat belongs to the user for security
            chat_result = self.supabase.table(self.table_name)\
                .select("user_id")\
                .eq("id", chat_id)\
                .execute()
            
            if not chat_result.data:
                print(f"Chat with id {chat_id} not found")
                return False
            
            # Verify ownership
            if chat_result.data[0]["user_id"] != user_id:
                print(f"Chat {chat_id} does not belong to user {user_id}")
                return False
            
            # Delete the chat
            result = self.supabase.table(self.table_name)\
                .delete()\
                .eq("id", chat_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting chat: {e}")
            return False
