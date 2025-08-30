# LLM Quiz API (FastAPI + Google Gemini)

LLM Quiz API는 FastAPI와 Google Gemini를 활용해 긴 텍스트를 간결 요약하고, 핵심 개념만 담은 4지선다형 퀴즈 2개를 JSON 형식으로 반환하는 API입니다.

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
 A. .env 파일(프로젝트 루트에 생성):
    API_KEY=발급받은_키값
 B. 현재 터미널 세션에 임시 설정(Windows PowerShell):
    $env:API_KEY="발급받은_키값"
 C. 영구 설정(Windows PowerShell, 새 터미널부터 적용)(권장):
    setx API_KEY "발급받은_키값"

# 4) 서버 실행
python -m uvicorn app:app --reload --port 8000

Swagger UI(권장): http://127.0.0.1:8000/docs
OpenAPI JSON: http://127.0.0.1:8000/openapi.json

```

## 3) 엔드포인트

### POST `/summarize_and_quiz`
- **Request (application/json)**
```json
{
  "text": "요약/퀴즈를 생성할 원문 텍스트를 여기에 입력"
}
```

- **Response 200 (application/json)**
```json
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
```
## 4) 호출 예시
Swagger UI일 때:

1. http://127.0.0.1:8000/docs 접속

2. POST /summarize_and_quiz → Try it out

3. Body에 {"text":"..."}

4. Execute

cURL일 때:

curl -X POST "http://127.0.0.1:8000/summarize_and_quiz" \
  -H "Content-Type: application/json" \
  -d '{"text":"여기에 텍스트"}'

## 5) 트러블슈팅
-API_KEY 미설정(500): .env의 API_KEY= 또는 PowerShell에서 $env:API_KEY="..." / setx API_KEY "...".

-GET으로 호출(405): /summarize_and_quiz는 POST 전용.

-JSON parse failed: 모델 출력이 코드펜스/포맷 이탈 → 재시도 또는 프롬프트·후처리 강화.

-Windows setx 후 인식 안 됨: 새 터미널을 열어 실행.

## 6) 동작 예시

*Swagger UI를 이용한 경우입니다*

<img width="3634" height="1592" alt="스크린샷 2025-08-30 012023" src="https://github.com/user-attachments/assets/08454303-175a-4280-94dd-ddfeed980f1f" />

<img width="3497" height="1831" alt="스크린샷 2025-08-30 012220" src="https://github.com/user-attachments/assets/36c388fe-9aa9-4e8b-b521-6cab4067c1e3" />

<img width="3470" height="1495" alt="스크린샷 2025-08-30 012244" src="https://github.com/user-attachments/assets/4a759046-7ce7-406b-a068-ca39fac8c824" />

<img width="3607" height="1109" alt="스크린샷 2025-08-30 012313" src="https://github.com/user-attachments/assets/33906e83-8548-4c6e-b4c7-e0ef327bca21" />
