from supabase import Client
import logging

class ChatConversationModel:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = "chat_conversations"
    
    def ensure_table_exists(self):
        #? Check if table exists, create if it doesn't
        try:
            # Try to query the table - if it doesn't exist, this will fail
            self.supabase.table(self.table_name).select("id").limit(1).execute()
            print(f"Table '{self.table_name}' already exists")
            return True
        except Exception as e:
            print(f"Table '{self.table_name}' doesn't exist or error occurred: {e}")
            return self.create_table()
    
    def create_table(self):
        #? Create the chat_conversations table
        try:
            # Execute SQL to create table
            sql_query = """
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                mentor_response TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations(user_id);
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_created_at ON chat_conversations(created_at);
            """
            
            result = self.supabase.rpc('exec_sql', {'sql': sql_query}).execute()
            print(f"Table '{self.table_name}' created successfully")
            return True
        except Exception as e:
            print(f"Error creating table '{self.table_name}': {e}")
            # Alternative method using direct SQL execution
            return self.create_table_alternative()
    
    def create_table_alternative(self):
        #? Alternative method to create table using individual SQL statements
        try:
            # Since direct SQL execution might not work, we'll use a different approach
            # First, try to create a dummy record to trigger table creation
            dummy_data = {
                "user_id": "dummy_user",
                "user_message": "dummy_message",
                "mentor_response": "dummy_response"
            }
            
            # This will fail if table doesn't exist, but we'll catch and handle
            try:
                self.supabase.table(self.table_name).insert(dummy_data).execute()
                # If successful, delete the dummy record
                self.supabase.table(self.table_name).delete().eq("user_id", "dummy_user").execute()
                return True
            except:
                # Table doesn't exist, log the schema needed
                print(f"""
                Please create the table manually in Supabase dashboard with this SQL:
                
                CREATE TABLE {self.table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    mentor_response TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX idx_chat_conversations_user_id ON {self.table_name}(user_id);
                CREATE INDEX idx_chat_conversations_created_at ON {self.table_name}(created_at);
                """)
                return False
        except Exception as e:
            print(f"Error in alternative table creation: {e}")
            return False
    
    def insert_conversation(self, user_id: str, user_message: str, mentor_response: str):
        """Insert a new conversation record"""
        try:
            conversation_data = {
                "user_id": user_id,
                "user_message": user_message,
                "mentor_response": mentor_response
            }
            
            result = self.supabase.table(self.table_name).insert(conversation_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error inserting conversation: {e}")
            return None
    
    def get_user_conversations(self, user_id: str, limit: int = 50):
        """Get conversations for a specific user"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []