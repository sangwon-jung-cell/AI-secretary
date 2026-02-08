import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime  # 날짜 계산을 위해 추가

# 현재 파일(ai_service.py)의 부모 폴더(backend)의 부모 폴더(AI-SECRETARY)에 있는 .env 찾기
load_dotenv() # .env 파일을 읽어서 시스템 환경변수에 등록함

# os.getenv("이름")을 통해 .env에 적은 이름을 찾아 가져옵니다.
api_key = os.getenv("GEMINI_API_KEY") # 또는 GOOGLE_API_KEY (.env 파일과 맞추세요)

genai.configure(api_key=api_key)

# Gemini 설정

model = genai.GenerativeModel('models/gemini-2.5-flash') # 가볍고 빠른 모델

def analyze_memo_with_ai(content: str):
    # 1. 오늘 날짜 구하기
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    weekday_str = now.strftime("%A") # 요일 정보도 주면 더 똑똑해집니다.

    # 2. 프롬프트에 '오늘 날짜' 정보 추가
    prompt = f"""
    당신은 비서 로봇입니다. 사용자의 메모에서 '할 일(task)', '날짜(date)', '시간(time)'을 추출하세요.
    - 날짜 형식: YYYY-MM-DD (연도가 없으면 2026년으로 가정)
    - "내일", "모레", "다음 주" 등은 오늘 날짜({today_str})를 기준으로 계산하세요.
    - 시간 형식: HH:MM
    - 정보가 없으면 null로 표시하세요.
    - 반드시 JSON 형식으로만 응답하세요.

    메모 내용: "{content}"
    """

    # Gemini 호출
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    # 결과 파싱
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"JSON 파싱 에러: {e}")
        return {{"task": "분석 실패", "date": None, "time": None}}