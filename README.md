# LLM Quiz API (FastAPI + Google Gemini)

긴 텍스트를 간결 요약하고, 핵심 개념만 담은 4지선다형 퀴즈 2개를 JSON으로 반환하는 API입니다.

## 주요 기능
- 입력 텍스트 요약 (3문장 내외)
- 4지선다 퀴즈 2개 자동 생성
- JSON 스키마 검증 (선지 개수, 정답 인덱스 등)
- `.env` 자동 탐색 및 로딩

## 요구 사항
- Python 3.10+
- Google AI Studio API Key
- 

## 설치
```bash
git clone <your-repo-url>
cd llm-quiz-api

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# .env 파일에 API_KEY=발급받은_키 입력

## 터미널에서 실행

작업 디렉터리를 app.py가 있는 폴더로 이동한 뒤:

python -m uvicorn app:app --reload --port 8000

Swagger UI: http://127.0.0.1:8000/docs

OpenAPI JSON: http://127.0.0.1:8000/openapi.json

--env-file .env 사용 시, 현재 폴더에 .env가 실제 존재해야 합니다. 절대경로도 가능: --env-file "C:/.../QuizAPI/.env"

## PyCharm에서 실행

Python 구성:

Script path: .../QuizAPI/app.py

Working directory: .../QuizAPI

Env vars: API_KEY=발급키

모듈 실행(uvicorn) 구성:

Module name: uvicorn

Parameters: app:app --reload --port 8000

Working directory: .../QuizAPI

Env vars: API_KEY=발급키

## 검증/에러 처리

입력값 검증: text가 비어 있으면 400 (text is empty)

환경변수 검증: API_KEY 미설정 시 500 (Missing API_KEY ...)

LLM 출력 파싱 실패 시 500 (JSON parse failed: ...)

스키마 검증 실패 시 502 (Model returned invalid schema)

퀴즈 검증 실패 시 422

choices 길이 4가 아님

answer_index가 정수가 아니거나 0..3 범위를 벗어남

그 외 예기치 못한 오류: 502 (Upstream model error)

브라우저 주소창으로 GET /summarize_and_quiz 요청 시 빈 화면/405가 정상입니다. (POST 전용)

