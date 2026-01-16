from fastapi import APIRouter, HTTPException
from app.schema.news_term import NewsTermListResponse
from app.service.ai_service import generate_news_term
from app.schema.news_term import NewsTermRequest

router = APIRouter()

@router.post("/generate", response_model=NewsTermListResponse)
async def extract_news_terms(request: NewsTermRequest):
    """
    뉴스 기사 내용에서 경제 용어를 추출하여 반환함
    """
    try:
        # ai_service.py의 함수 호출
        result = await generate_news_term(request.content)
        
        # result는 {"terms": [...]} 형태의 딕셔너리여야 함
        return result 
        
    except Exception as e:
        # 에러 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=str(e))
