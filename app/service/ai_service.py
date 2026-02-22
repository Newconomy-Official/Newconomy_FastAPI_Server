import os
import json
from dotenv import load_dotenv
from google import genai
from app.schema.quiz import QuizRequest, TermQuizRequest

# 1. 환경 변수 로드
load_dotenv()

# 2. 공식 클라이언트 설정 (반드시 google-genai 라이브러리 필요)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_economy_quiz(data: QuizRequest):
    system_instruction = (
        "너는 경제 전문 퀴즈 출제 위원이야. "
        "뉴스 내용을 분석해 객관식(MULTIPLE_CHOICE) 또는 OX 퀴즈를 생성해. "
        "응답은 반드시 순수한 JSON 형식이어야 해."
    )
    
    user_prompt = f"""
    내용: {data.content}

    위 내용을 바탕으로 경제 퀴즈 3개를 생성해줘.
    결과는 반드시 다음 JSON 스키마를 따를 것:
    {{
      "quizList": [
        {{
          "quizType": "MULTIPLE_CHOICE 또는 OX",
          "question": "질문 내용",
          "correctAnswer": "정답인 보기의 텍스트",
          "explanation": "해설 내용",
          "difficultyLevel": 3,
          "quizOptionList": [
            {{"optionText": "보기1", "optionOrder": 1, "isCorrect": false}},
            {{"optionText": "보기2", "optionOrder": 2, "isCorrect": true}},
            {{"optionText": "보기3", "optionOrder": 3, "isCorrect": false}},
            {{"optionText": "보기4", "optionOrder": 4, "isCorrect": false}}
          ]
        }}
      ]
    }}
    * MULTIPLE_CHOICE: 반드시 4개의 보기를 만들고 정답인 보기의 isCorrect를 true로 설정해.
    * OX: quizOptionList는 빈 리스트 []로 보내고, correctAnswer에 'O' 또는 'X'를 넣어줘.
    """

    try:
        # 공식 SDK 호출 (404 에러 해결)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
            },
            contents=user_prompt
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"AI 생성 오류: {e}")
        raise e

async def generate_term_quiz(data: TermQuizRequest):
    selected_terms = data.terms    
    terms_text = ""
    for term in selected_terms:
        terms_text += (
            f"- 용어명: {term.termName}\n"
            f"  간단설명: {term.simpleExplanation}\n"
            f"  상세설명: {term.detailedExplanation}\n\n"
        )

    system_instruction = (
        "너는 금융/경제 전문가이자 퀴즈 출제 위원이야. "
        "응답은 반드시 지정된 JSON 형식으로만 해야 해."
    )
    
    user_prompt = f"""
    다음 경제 용어 정보를 바탕으로 퀴즈를 생성해줘.
    
    [학습 대상 용어 목록]
    {terms_text}

    [제약 사항]
    1. 각 용어당 1개의 문제를 만드시오.
    2. 'detailedExplanation' 내용을 참고하여 문제의 깊이를 더하시오.
    3. 정답은 반드시 제공된 용어 목록 안에 있는 것이어야 함.
    4. 보기는 4개(optionOrder 1~4)여야 하며, OX문제의 경우에는 quizOptionList를 빈 리스트([])로 만드시오.

    [결과 JSON 스키마]
    {{
      "quizList": [
        {{
          "quizType": "MULTIPLE_CHOICE",
          "question": "Q. (질문 내용)",
          "correctAnswer": "(정답인 보기의 텍스트)",
          "explanation": "(정답인 이유와 오답 풀이)",
          "difficultyLevel": 1,
          "quizOptionList": [
            {{"optionText": "보기1", "optionOrder": 1, "isCorrect": false}},
            {{"optionText": "보기2", "optionOrder": 2, "isCorrect": true}},
            {{"optionText": "보기3", "optionOrder": 3, "isCorrect": false}},
            {{"optionText": "보기4", "optionOrder": 4, "isCorrect": false}}
          ]
        }}
      ]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
            },
            contents=user_prompt
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"용어 퀴즈 생성 중 오류 발생: {e}")
        raise e

async def generate_news_term(content: str) -> dict:
    categories_info = """
    - MONETARY: 통화/금융
    - INVESTMENT: 투자/증시
    - REAL_ESTATE: 부동산
    - MACRO: 거시경제
    - MICRO: 미시경제
    - LIFE: 생활금융
    """
    system_instruction = (
        "너는 초고도로 전문화된 금융 경제 전문 모델이야. "
        "뉴스 본문에서 '전문적인 경제 지식'이 필요한 용어만 추출해. "
        "카테고리는 반드시"+categories_info+" 중에서 선택해. "
        "응답은 반드시 JSON 형식으로만 해야 해."
    )
    
    user_prompt = f"""
    내용: {content}
    위 뉴스 본문에서 핵심 경제 용어를 추출해줘. (10~20개 사이)
    [결과 JSON 스키마]
    {{
      "terms": [
        {{
          "termName": "용어명",
          "simpleExplanation": "간단 설명",
          "detailedExplanation": "상세 설명",
          "termCategory": "MONETARY", 
          "difficultyLevel": 3
        }}
      ]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
            },
            contents=user_prompt
        )
        
        result = json.loads(response.text)
        terms_list = result.get('terms', [])
        
        for term in terms_list:
            if term.get("termCategory") not in ["MONETARY", "INVESTMENT", "REAL_ESTATE", "MACRO", "MICRO", "LIFE"]:
                term["termCategory"] = "MACRO"

        if terms_list:
            terms_list = add_indices_to_terms(content, terms_list)
        
        return {"terms": terms_list}

    except Exception as e:
        print(f"용어 추출 중 오류 발생: {e}")
        return {"terms": []}

def add_indices_to_terms(content: str, terms: list):
    for term in terms:
        term_name = term.get("termName", "")
        start_index = content.find(term_name)
        if start_index != -1:
            term["startIndex"] = start_index
            term["endIndex"] = start_index + len(term_name)
        else:
            term["startIndex"] = -1
            term["endIndex"] = -1
        term["contextSentence"] = ""
    return terms