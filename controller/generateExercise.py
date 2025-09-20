import google.generativeai as genai
from google.generativeai import types
import os
import dotenv
from utils.rag import RAGProcessor
from utils.helper import clean_content
import logging

dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerateExercise:
    def __init__(self, userId):
        self.userId = userId
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.rag_processor = RAGProcessor()
        
    def upload_and_process_book(self, pdf_file):
        """Upload and process a PDF book for RAG"""
        try:
            success = self.rag_processor.process_document(pdf_file)
            if success:
                return {"status": "success", "message": "Book uploaded and indexed successfully"}
            else:
                return {"status": "error", "message": "Failed to process the book"}
        except Exception as e:
            print(f"Error uploading book: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_exercise_with_context(self, topic, exercise_type="mcq", num_questions=5, difficulty_level="medium"):
        """Generate exercises based on uploaded book content"""
        try:
            # Retrieve relevant context from the book
            context_chunks = self.rag_processor.retrieve_top_chunks(topic, k=10)
            
            if not context_chunks:
                return self.generate_exercise_without_context(topic, exercise_type, num_questions)
            
            # Prepare context for the AI
            context = "\n\n".join(context_chunks)
            
            logger.info(f"Context for Exercise Generation: {context}")

            # User prompt for MCQ generation
            mcq_prompt = f"""
            Based on the following book content, create {num_questions} {exercise_type} questions about: {topic}.

            For MCQs each question, provide:
            - The question text
            - Four options labeled a), b), c), d)
            At the end, include an 'Answer Key' section in the following format:
            Answer Key:
            1. b
            2. c
            ...

            Book Content:
            {context}

            Topic: {topic}
            Exercise Type: {exercise_type}
            Number of Questions: {num_questions}
            Difficulty Level: {difficulty_level}
            """

            # user prompt for other types of exercises
            normal_prompt= f"""
            Based on the following book content, create {num_questions} {exercise_type} questions about: {topic}.
            For each question, provide the necessary details as per the exercise type.

            Book Content:
            {context}

            Topic: {topic}
            Exercise Type: {exercise_type}
            Number of Questions: {num_questions}
            """

            logger.info(f"Enhanced Prompt: {mcq_prompt if exercise_type == 'mcq' else normal_prompt}")
            
            logger.info(f"Context Chunks Retrieved: {len(context_chunks)}")

            # Generate AI response with context
            system_instruction = os.getenv("EXERCISE_SYSTEM_INSTRUCTION")
            response = self.model.generate_content(
                contents=mcq_prompt if exercise_type == "mcq" else normal_prompt,
                generation_config=types.GenerationConfig(
                    system_instruction=system_instruction
                )
            )
            logger.info(f"Raw AI response: {getattr(response, 'text', repr(response))}")
            cleaned = clean_content(response.text)
            logger.info(f"Cleaned content: {cleaned}")
            return cleaned

        except Exception as e:
            logger.error(f"Error generating exercise with context: {e}")
            return "Sorry, there was an error generating the exercise with book context."
    
    def generate_exercise_without_context(self, topic, exercise_type="mcq", num_questions=5):
        """Generate exercises without book context (fallback)"""
        try:
            prompt = f"Create {num_questions} {exercise_type} questions about: {topic}. For each question, provide four options labeled a), b), c), d). At the end, include an 'Answer Key' section in the following format:\nAnswer Key:\n1. b\n2. c\n..."
            
            system_instruction = os.getenv("EXERCISE_SYSTEM_INSTRUCTION")
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self.model.generate_content(
                contents=full_prompt,
                generation_config=types.GenerationConfig(
                    # Add other config params here if needed
                )
            )
            logger.info(f"Raw AI response (no context): {getattr(response, 'text', repr(response))}")
            cleaned = clean_content(response.text)
            logger.info(f"Cleaned content (no context): {cleaned}")
            return cleaned
 
        except Exception as e:
            logger.error(f"Error generating exercise: {e}")
            return "Sorry, there was an error generating the exercise."
    
    def chat_with_mentor(self, topic):
        """Original method for backward compatibility"""
        return self.generate_exercise_with_context(topic)
    
    def ask_question_about_book(self, question):
        """Ask a specific question about the uploaded book"""
        try:
            # Retrieve relevant context
            context_chunks = self.rag_processor.retrieve_top_chunks(question, k=5)
            
            if not context_chunks:
                return "No relevant content found in the uploaded book for your question."
            
            context = "\n\n".join(context_chunks)
            
            # Create prompt for Q&A
            qa_prompt = f"""
            Based on the following book content, answer the question:
            
            Book Content:
            {context}
            
            Question: {question}
            
            Please provide a comprehensive answer based on the book content.
            """
            
            system_instruction = "You are a helpful assistant that answers questions based on provided book content. Be accurate and cite the relevant parts of the content when possible."
            full_prompt = f"{system_instruction}\n\n{qa_prompt}"
            response = self.model.generate_content(
                contents=full_prompt,
                generation_config=types.GenerationConfig(
                    # Add other config params here if needed
                )
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Sorry, there was an error processing your question."
    
    def generate_notes_with_context(self, topic, num_notes=5, difficulty_level="medium"):
        """Generate important notes based on uploaded book content"""
        try:
            # Retrieve relevant context from the book
            context_chunks = self.rag_processor.retrieve_top_chunks(topic, k=15)
            
            if not context_chunks:
                return self.generate_notes_without_context(topic, num_notes)
            
            # Prepare context for the AI
            context = "\n\n".join(context_chunks)
            
            logger.info(f"Context for Notes Generation: {context}")
            logger.info(f"Context Chunks Retrieved: {len(context_chunks)}")

            # User prompt for notes generation
            notes_prompt = f"""
            Based on the following book content, create {num_notes} important section notes about: {topic}.

            For each note section, provide:
            - A clear, descriptive title
            - A brief subtitle (optional)
            - 3-5 key points (bullet points)
            - A concise summary paragraph
            - 2-4 important concepts/tags

            Format the response as a JSON array where each note has this structure:
            {{
                "title": "Section Title",
                "subtitle": "Brief description (optional)",
                "keyPoints": ["Point 1", "Point 2", "Point 3"],
                "summary": "Brief summary paragraph",
                "importantConcepts": ["Concept 1", "Concept 2", "Concept 3"]
            }}

            Book Content:
            {context}

            Topic: {topic}
            Number of Notes: {num_notes}
            Difficulty Level: {difficulty_level}
            """

            logger.info(f"Notes Generation Prompt: {notes_prompt}")
            
            # Generate AI response with context
            system_instruction = "You are an expert educational content creator. Generate well-structured, comprehensive notes that capture the most important information from the provided book content. Focus on clarity, accuracy, and educational value."
            response = self.model.generate_content(
                contents=notes_prompt,
                generation_config=types.GenerationConfig(
                    system_instruction=system_instruction
                )
            )
            
            logger.info(f"Raw AI response for notes: {getattr(response, 'text', repr(response))}")
            
            # Try to parse JSON response
            try:
                import json
                import re
                
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.startswith('```'):
                    response_text = response_text[3:]   # Remove ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove trailing ```
                
                # Try to find JSON array in the text
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
                
                notes_data = json.loads(response_text)
                if isinstance(notes_data, list):
                    # Add IDs to each note
                    for i, note in enumerate(notes_data, 1):
                        note['id'] = i
                    return notes_data
                else:
                    # If not a list, wrap in array
                    notes_data['id'] = 1
                    return [notes_data]
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"JSON parsing failed: {e}")
                # If JSON parsing fails, return as text format
                cleaned = clean_content(response.text)
                return [{"id": 1, "type": "Text", "content": cleaned}]

        except Exception as e:
            logger.error(f"Error generating notes with context: {e}")
            return self.generate_notes_without_context(topic, num_notes)
    
    def generate_notes_without_context(self, topic, num_notes=5):
        """Generate notes without book context (fallback)"""
        try:
            prompt = f"""
            Create {num_notes} important section notes about: {topic}.

            For each note section, provide:
            - A clear, descriptive title
            - A brief subtitle (optional)
            - 3-5 key points (bullet points)
            - A concise summary paragraph
            - 2-4 important concepts/tags

            Format the response as a JSON array where each note has this structure:
            {{
                "title": "Section Title",
                "subtitle": "Brief description (optional)",
                "keyPoints": ["Point 1", "Point 2", "Point 3"],
                "summary": "Brief summary paragraph",
                "importantConcepts": ["Concept 1", "Concept 2", "Concept 3"]
            }}
            """
            
            system_instruction = "You are an expert educational content creator. Generate well-structured, comprehensive notes on the given topic. Focus on clarity, accuracy, and educational value."
            full_prompt = f"{system_instruction}\n\n{prompt}"
            response = self.model.generate_content(
                contents=full_prompt,
                generation_config=types.GenerationConfig(
                    # Add other config params here if needed
                )
            )
            
            logger.info(f"Raw AI response for notes (no context): {getattr(response, 'text', repr(response))}")
            
            # Try to parse JSON response
            try:
                import json
                import re
                
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.startswith('```'):
                    response_text = response_text[3:]   # Remove ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove trailing ```
                
                # Try to find JSON array in the text
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
                
                notes_data = json.loads(response_text)
                if isinstance(notes_data, list):
                    # Add IDs to each note
                    for i, note in enumerate(notes_data, 1):
                        note['id'] = i
                    return notes_data
                else:
                    # If not a list, wrap in array
                    notes_data['id'] = 1
                    return [notes_data]
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"JSON parsing failed (no context): {e}")
                # If JSON parsing fails, return as text format
                cleaned = clean_content(response.text)
                return [{"id": 1, "type": "Text", "content": cleaned}]
 
        except Exception as e:
            logger.error(f"Error generating notes: {e}")
            return [{"id": 1, "type": "Text", "content": "Sorry, there was an error generating the notes."}]