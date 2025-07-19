from controller.generateExercise import GenerateExercise
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from typing import Optional
import logging
from controller import supabase

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExerciseRequest(BaseModel):
    userId: str
    topic: str
    exercise_type: Optional[str] = "mcq"
    num_questions: Optional[int] = 5

class QuestionRequest(BaseModel):
    userId: str
    question: str

@router.post("/exercise/upload-book")
async def upload_book(userId: str = Form(...), file: UploadFile = File(...)):
    """Upload and process a PDF book for exercise generation"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        exercise_generator = GenerateExercise(userId)
        result = exercise_generator.upload_and_process_book(file.file)
        
        if result["status"] == "success":
            return {"message": result["message"]}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise/generate")
async def generate_exercise(request: ExerciseRequest):
    """Generate exercises based on uploaded book content"""
    try:
        logger.info(f"Received generate_exercise request: {request}")
        exercise_generator = GenerateExercise(request.userId)
        exercises = exercise_generator.generate_exercise_with_context(
            topic=request.topic,
            exercise_type=request.exercise_type,
            num_questions=request.num_questions
        )
        logger.info(f"Generated exercises: {exercises}")
        if not exercises:
            exercises = "Sorry, no exercises could be generated."
        return {"exercises": exercises}
    except Exception as e:
        logger.error(f"Error in generate_exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise/ask")
async def ask_question_about_book(request: QuestionRequest):
    """Ask a question about the uploaded book"""
    try:
        exercise_generator = GenerateExercise(request.userId)
        answer = exercise_generator.ask_question_about_book(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise/generate-simple")
async def generate_simple_exercise(request: ExerciseRequest):
    """Generate exercises without book context"""
    try:
        exercise_generator = GenerateExercise(request.userId)
        exercises = exercise_generator.generate_exercise_without_context(
            topic=request.topic,
            exercise_type=request.exercise_type,
            num_questions=request.num_questions
        )
        return {"exercises": exercises}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise/save")
async def save_exercise(
    exerciseType: str = Body(...),
    exerciseData: list = Body(...),
    grade: str = Body(None),
    subject: str = Body(None),
    topic: str = Body(None),
    sub_topic: str = Body(None)
):
    """Save generated exercises to the appropriate table."""
    try:
        if exerciseType.lower() in ["multiple choice", "mcq", "mcqs"]:
            for ex in exerciseData:
                if not ex.get("question"):
                    continue
                mcq = {
                    "grade": grade,
                    "subject": subject,
                    "topic": topic,
                    "sub_topic": sub_topic,
                    "question": ex["question"]
                }
                mcq_result = supabase.table("mcqs").insert(mcq).execute()
                mcq_id = mcq_result.data[0]["id"]
                for opt in ex.get("options", []):
                    supabase.table("mcq_options").insert({
                        "mcq_id": mcq_id,
                        "option": opt,
                        "is_correct": (opt == ex.get("correct"))
                    }).execute()
        elif exerciseType.lower() in ["fill in the blanks", "fill_blanks", "fill blank"]:
            for ex in exerciseData:
                if not ex.get("question"):
                    continue
                fill_blank = {
                    "grade": grade,
                    "subject": subject,
                    "topic": topic,
                    "sub_topic": sub_topic,
                    "question": ex["question"],
                    "answer": ex.get("answer", "")
                }
                fb_result = supabase.table("fill_blanks").insert(fill_blank).execute()
                fb_id = fb_result.data[0]["id"]
                for opt in ex.get("blanks", []):
                    supabase.table("fill_blank_options").insert({
                        "fill_blank_id": fb_id,
                        "option": opt
                    }).execute()
        elif exerciseType.lower() in ["short answer", "short_questions", "short question"]:
            for ex in exerciseData:
                if not ex.get("question"):
                    continue
                short_q = {
                    "grade": grade,
                    "subject": subject,
                    "topic": topic,
                    "sub_topic": sub_topic,
                    "question": ex["question"],
                    "answer": ex.get("answer", ""),
                    "diagram": ex.get("diagram", "")
                }
                supabase.table("short_questions").insert(short_q).execute()
        elif exerciseType.lower() in ["essay", "long_questions", "long question"]:
            for ex in exerciseData:
                if not ex.get("question"):
                    continue
                long_q = {
                    "grade": grade,
                    "subject": subject,
                    "topic": topic,
                    "sub_topic": sub_topic,
                    "question": ex["question"],
                    "definition": ex.get("definition", ""),
                    "explanation": ex.get("explanation", ""),
                    "diagram": ex.get("diagram", "")
                }
                supabase.table("long_questions").insert(long_q).execute()
        else:
            print("Saving as generic exercise:", exerciseData)
        return {"message": "Exercises saved successfully!"}
    except Exception as e:
        print(f"Error saving exercises: {e}")
        raise HTTPException(status_code=500, detail=str(e))