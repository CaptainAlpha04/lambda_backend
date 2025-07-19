from controller.generateExercise import GenerateExercise
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

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
        exercise_generator = GenerateExercise(request.userId)
        exercises = exercise_generator.generate_exercise_with_context(
            topic=request.topic,
            exercise_type=request.exercise_type,
            num_questions=request.num_questions
        )
        
        print("Generated Exercises:", exercises)
        
        return {"exercises": exercises}
    except Exception as e:
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