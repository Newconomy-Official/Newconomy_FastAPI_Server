import json
from typing import List 
from pydantic import BaseModel

class NewsTermResponse(BaseModel):
    termName: str
    simpleExplanation: str
    detailedExplanation: str
    termCategory: str
    difficultyLevel: int
    startIndex: int
    endIndex: int
    contextSentence: str
class NewsTermListResponse(BaseModel):
    terms: List[NewsTermResponse]

class NewsTermRequest(BaseModel):
    content: str