from controller.mentorController import Mentor
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ChatRequest(BaseModel):
    userId: str
    message: str
    chat_id: Optional[str] = None

class NewChatRequest(BaseModel):
    userId: str
    title: Optional[str] = None

class RenameChatRequest(BaseModel):
    chat_id: str
    title: str

class DeleteChatRequest(BaseModel):
    chat_id: str
    user_id: str

@router.post("/mentor/chat")
async def chat_with_mentor(request: ChatRequest):
    try:
        mentor = Mentor(request.userId)
        response = mentor.chat_with_mentor(request.userId, request.message, request.chat_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mentor/new-chat")
async def create_new_chat(request: NewChatRequest):
    try:
        mentor = Mentor(request.userId)
        chat = mentor.chat_model.create_new_chat(request.userId, request.title)
        if chat:
            return {"chat": chat}
        else:
            raise HTTPException(status_code=500, detail="Failed to create new chat")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentor/chats/{user_id}")
async def get_user_chats(user_id: str, limit: int = 10):
    try:
        mentor = Mentor(user_id)
        chats = mentor.chat_model.get_user_chats(user_id, limit)
        return {"chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentor/history/{user_id}")
async def get_chat_history(user_id: str, chat_id: Optional[str] = None):
    try:
        mentor = Mentor(user_id)
        history = mentor.chat_model.get_conversation_history(user_id, chat_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mentor/rename-chat")
async def rename_chat(request: RenameChatRequest):
    """Rename the title of an existing chat session"""
    try:
        # We can use any user_id for initialization since we're just updating title
        mentor = Mentor("temp")  # Temporary user ID for initialization
        success = mentor.chat_model.update_chat_title(request.chat_id, request.title)
        
        if success:
            return {"message": "Chat title updated successfully", "chat_id": request.chat_id, "new_title": request.title}
        else:
            raise HTTPException(status_code=404, detail="Chat not found or failed to update")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/mentor/delete-chat")
async def delete_chat(request: DeleteChatRequest):
    """Delete an existing chat session"""
    try:
        mentor = Mentor(request.user_id)
        success = mentor.chat_model.delete_chat(request.chat_id, request.user_id)
        
        if success:
            return {"message": "Chat deleted successfully", "chat_id": request.chat_id}
        else:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentor/test-db")
async def test_database_connection():
    """Test endpoint to verify database connection"""
    try:
        from controller import supabase
        # Test mentor_chats table
        mentor_result = supabase.table("mentor_chats").select("id").limit(1).execute()
        
        # Test if users table exists
        try:
            users_result = supabase.table("users").select("id").limit(1).execute()
            users_status = "exists"
            users_data = users_result.data
        except Exception as e:
            users_status = f"error: {str(e)}"
            users_data = []
        
        return {
            "status": "success", 
            "message": "Database connection working", 
            "mentor_chats_data": mentor_result.data,
            "users_table_status": users_status,
            "users_data": users_data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/mentor/test-user-schema")
async def test_user_schema():
    """Test endpoint to understand users table schema"""
    try:
        from controller import supabase
        
        # Get existing users to see what fields they have
        result = supabase.table("users").select("*").limit(1).execute()
        
        return {
            "status": "success",
            "sample_user": result.data[0] if result.data else "No users found",
            "user_count": len(result.data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/mentor/test-direct-insert")
async def test_direct_insert():
    """Test direct database insert to mentor_chats table"""
    try:
        from controller import supabase
        import uuid
        
        # Get existing user
        users_result = supabase.table("users").select("id").limit(1).execute()
        if not users_result.data:
            return {"status": "error", "message": "No users found"}
        
        user_id = users_result.data[0]["id"]
        
        # Try direct insert
        chat_data = {
            "user_id": user_id,
            "title": "Direct Test Chat",
            "conversation": []
        }
        
        print(f"Attempting direct insert with data: {chat_data}")
        result = supabase.table("mentor_chats").insert(chat_data).execute()
        
        return {
            "status": "success" if result.data else "error",
            "message": "Direct insert test",
            "result_data": result.data,
            "result_count": result.count if hasattr(result, 'count') else 'unknown',
            "user_id": user_id
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": str(type(e))}

@router.post("/mentor/test-full-flow")
async def test_full_flow():
    """Test the complete flow: create user, create chat, send message"""
    try:
        from controller import supabase
        from controller.mentorController import Mentor
        
        # Use existing user from database
        users_result = supabase.table("users").select("id").limit(1).execute()
        if not users_result.data:
            return {"status": "error", "message": "No users found in database"}
        
        test_user_id = users_result.data[0]["id"]
        results = {"steps": [], "user_id": test_user_id}
        results["steps"].append(f"Using existing user: {test_user_id}")
        
        # Step 1: Test chat creation directly
        try:
            mentor = Mentor(test_user_id)
            chat = mentor.chat_model.create_new_chat(test_user_id, "Test Chat")
            if chat:
                results["steps"].append(f"Successfully created chat: {chat['id']}")
                results["chat_id"] = chat['id']
            else:
                results["steps"].append("Failed to create chat - no data returned")
                return {"status": "error", "results": results}
        except Exception as e:
            results["steps"].append(f"Chat creation error: {str(e)}")
            return {"status": "error", "results": results}
        
        # Step 2: Test adding a message
        try:
            if "chat_id" in results:
                success = mentor.chat_model.add_message_to_conversation(
                    results["chat_id"], 
                    "Test message", 
                    "Test response"
                )
                results["steps"].append(f"Message added: {success}")
        except Exception as e:
            results["steps"].append(f"Message adding error: {str(e)}")
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}