# LLM Quiz API (FastAPI + Google Gemini)

긴 텍스트를 간결 요약하고, 핵심 개념만 담은 4지선다형 퀴즈 2개를 JSON으로 반환하는 API입니다.

## 주요 기능
- 입력 텍스트 요약 (3문장 내외)
- 4지선다 퀴즈 2개 자동 생성
- JSON 스키마 검증 (선지 개수, 정답 인덱스 등)
- `.env` 자동 탐색 및 로딩

## 1) 요구 사항
- Python 3.10+
- Google AI Studio **API Key** (Gemini)
- `requirements.txt` 설치

---

## 2) 설치 & 실행 (Quick Start)

```bash
# 1) 가상환경
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

# 2) 의존성
pip install -r requirements.txt

# 3) API 키 설정 (아래 중 택1)
#   A. .env 파일(프로젝트 루트에 생성):
#      API_KEY=발급받은_키값
#   B. 현재 터미널 세션에 임시 설정(Windows PowerShell):
#      $env:API_KEY="발급받은_키값"
#   C. 영구 설정(Windows PowerShell, 새 터미널부터 적용):
#      setx API_KEY "발급받은_키값"

# 4) 서버 실행
python -m uvicorn app:app --reload --port 8000

Swagger UI(권장): http://127.0.0.1:8000/docs
OpenAPI JSON: http://127.0.0.1:8000/openapi.json

참고: 주소창으로 /summarize_and_quiz를 열면 GET 요청이라 405/빈 화면이 정상

## 3) 엔드포인트

### POST `/summarize_and_quiz`
- **Request (application/json)**
```json
{
  "text": "요약/퀴즈를 생성할 원문 텍스트를 여기에 입력"
}

### Response 200 (application/json)

{
  "summary": "핵심 3문장 요약",
  "quizzes": [
    {
      "question": "문항 내용",
      "choices": ["A", "B", "C", "D"],
      "answer_index": 0
    },
    {
      "question": "두 번째 문항",
      "choices": ["A", "B", "C", "D"],
      "answer_index": 2
    }
  ]
}
