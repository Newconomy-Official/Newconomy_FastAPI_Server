from fastapi import FastAPI
from app.api import quiz
import app.api.news_term as news_term

app = FastAPI(title="Newconomy AI Server")

# 라우터 등록
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(news_term.router, prefix="/api/news-term", tags=["News Term"])

@app.get("/")
def root():
    return {"message": "FastAPI Server is Running"}