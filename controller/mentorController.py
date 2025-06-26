from google import genai
from google.genai import types
import os
import dotenv 

dotenv.load_dotenv()
class Mentor:
    def __init__(self, userId):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.chat = self.client.chats.create(model="gemini-2.0-flash")
    
    def chat_with_mentor(self, userId, message):
        response = self.chat.send_message(
            message=message,
            config=types.GenerateContentConfig(
                system_instruction=os.getenv("MENTOR_SYSTEM_INSTRUCTION"),
            )
        )
        return response.text