from fastapi import FastAPI
from app.api import quiz

app = FastAPI(title="Newconomy AI Server")

# 라우터 등록
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])

@app.get("/")
def root():
    return {"message": "FastAPI Server is Running"}