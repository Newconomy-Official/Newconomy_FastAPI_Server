from fastapi import APIRouter, HTTPException
from app.schema.quiz import QuizRequest, QuizListResponse
from app.service.ai_service import generate_economy_quiz

router = APIRouter()

@router.post("/generateQuiz", response_model=QuizListResponse)
async def create_quiz(request: QuizRequest):
    """
    Spring Boot로부터 뉴스 데이터를 받아 퀴즈를 생성하고 반환함
    """
    try:
        # ai_service.py의 함수 호출
        result = await generate_economy_quiz(request)
        
        # result는 {"quizzes": [...]} 형태의 딕셔너리여야 함
        return result 
        
    except Exception as e:
        # 에러 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=str(e))