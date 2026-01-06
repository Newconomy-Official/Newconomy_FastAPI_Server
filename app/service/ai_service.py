import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
import random
from app.schema.quiz import QuizRequest, TermQuizRequest, EconomyTerm

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1/solar"
)

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
        response = await client.chat.completions.create(
            model="solar-pro",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            response_format={ "type": "json_object" }
        )

        ai_content = response.choices[0].message.content
        return json.loads(ai_content)

    except Exception as e:
        print(f"AI 생성 오류: {e}")
        raise e
    
import json
import random  # 필수!
from openai import AsyncOpenAI
# 위에서 정의한 스키마 import
from app.schema.quiz import TermQuizRequest

# (client 설정 코드는 기존과 동일하다고 가정)

async def generate_term_quiz(data: TermQuizRequest):
    """
    TermQuizRequest(Java DTO 리스트)를 받아 객관식 퀴즈를 생성하는 함수
    """
    
    # 1. 퀴즈 생성에 사용할 용어 3개 랜덤 추출 (데이터가 3개 미만이면 전체 사용)
    selected_terms = data.terms
    if len(data.terms) > 3:
        selected_terms = random.sample(data.terms, 3)

    # 2. 프롬프트에 넣을 텍스트 구성
    # Java DTO 필드명(termName, simpleExplanation 등)을 정확히 사용해야 합니다.
    terms_text = ""
    for term in selected_terms:
        terms_text += (
            f"- 용어명: {term.termName}\n"
            f"  간단설명: {term.simpleExplanation}\n"
            f"  상세설명: {term.detailedExplanation}\n\n"
        )

    # 3. 시스템 프롬프트 (역할 부여)
    system_instruction = (
        "너는 금융/경제 전문가이자 퀴즈 출제 위원이야. "
        "제공된 용어와 설명을 바탕으로 학습자가 용어를 확실히 이해했는지 확인할 수 있는 "
        "수준 높은 객관식(MULTIPLE_CHOICE) 퀴즈 3문제를 출제해. "
        "응답은 반드시 지정된 JSON 형식으로만 해야 해."
    )
    
    # 4. 유저 프롬프트 (데이터 주입)
    user_prompt = f"""
    다음 경제 용어 정보를 바탕으로 퀴즈 3개를 생성해줘.
    
    [학습 대상 용어 목록]
    {terms_text}

    [제약 사항]
    1. 각 용어당 1개의 문제를 만드시오. (총 3문제)
    2. 'detailedExplanation' 내용을 참고하여 문제의 깊이를 더하시오.
    3. 정답은 반드시 제공된 용어 목록 안에 있는 것이어야 함.
    4. 보기는 4개(optionOrder 1~4)여야 함.

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
        # 5. AI 요청
        response = await client.chat.completions.create(
            model="solar-pro", # 또는 사용하시는 모델명
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            response_format={ "type": "json_object" }
        )

        ai_content = response.choices[0].message.content
        return json.loads(ai_content)

    except Exception as e:
        print(f"용어 퀴즈 생성 중 오류 발생: {e}")
        # 필요 시 에러를 다시 던지거나 적절한 에러 응답 리턴
        raise e