from pydantic import BaseModel
from typing import List, Optional

class QuizRequest(BaseModel):
    newsId: int
    content: str

# 1. 자식 모델을 먼저 선언해야 합니다.
class QuizOptionSchema(BaseModel):
    optionText: str
    optionOrder: int
    isCorrect: bool

# 2. 그 다음 부모 모델에서 참조합니다.
class QuizSchema(BaseModel):
    quizType: str           # "OX" 또는 "MULTIPLE_CHOICE"
    question: str           
    correctAnswer: str      
    explanation: str        
    difficultyLevel: int    
    # Optional로 선언하여 OX일 경우 None이나 빈 리스트가 가능하게 합니다.
    quizOptionList: Optional[List[QuizOptionSchema]] = None

class QuizListResponse(BaseModel):
    quizList: List[QuizSchema]

class EconomyTerm(BaseModel):
    termId: int
    termName: str
    simpleExplanation: str
    detailedExplanation: str

class TermQuizRequest(BaseModel):
    terms: List[EconomyTerm]