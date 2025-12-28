import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.schema.quiz import QuizRequest

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
      "quizzes": [
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