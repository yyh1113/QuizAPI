import os, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv, find_dotenv, dotenv_values
import google.generativeai as genai
import logging

# uvicorn 콘솔에 찍히는 로그 채널을 활용
logger = logging.getLogger("uvicorn.error")

def _load_env():
    """
    .env 파일을 다양한 경로 후보에서 탐색/로딩하고,
    실제로 API_KEY가 잡혔는지 로깅까지 해주는 유틸 함수.
    - 1차: 현재 작업 디렉토리(CWD) 기준
    - 2차: 현재 파일(app.py)의 폴더 기준
    - 3차: 상위 폴더들을 거슬러 올라가며 루트 추정(최대 3단계)
    """
    # CWD 기준 탐색 (.env가 현재 실행 디렉토리에 있으면 최우선)
    path1 = find_dotenv(filename=".env", usecwd=True)

    # 소스 파일 위치 기준 탐색 (uvicorn이 다른 CWD에서 앱을 띄울 때 대비)
    path2 = str(Path(__file__).resolve().parent / ".env")

    # 상위 폴더들까지 후보로 추가 (모노레포/다층 폴더 구조 대비)
    here = Path(__file__).resolve()
    candidates = {path1, path2}
    for up in range(1, 4):
        candidates.add(str(here.parents[up-1] / ".env"))

    loaded = False
    tried = []  # 어디 어디를 시도했는지 기록

    # 후보 경로들을 순회하며 최초로 발견되는 .env를 로딩
    for p in [c for c in candidates if c]:
        tried.append(p)
        if Path(p).is_file():
            load_dotenv(dotenv_path=p, override=True)  # 같은 키가 있으면 .env 값으로 덮어씀
            loaded = True
            logger.info(f"[dotenv] loaded from: {p}")
            break

    # 어떤 후보에서도 발견 못한 경우 경고 로그
    if not loaded:
        logger.warning(f"[dotenv] .env not found. tried: {tried}")

    # 디버깅: API_KEY가 실제로 로드되었는지(앞 6글자만) 출력
    api = os.getenv("API_KEY")
    logger.info(f"[dotenv] API_KEY exists?: {bool(api)} value_prefix: {api[:6]+'...' if api else None}")

    # dotenv_values로 파싱 자체가 되는지(키 목록만) 추가 확인
    for p in tried:
        if Path(p).is_file():
            vals = dotenv_values(p)
            logger.info(f"[dotenv] dotenv_values keys: {list(vals.keys())}")
            break

# 서버 시작 시점에 .env 로딩 시도
_load_env()

# 환경변수에 API_KEY가 있는지 표준 출력으로 한 번 더 확인
print("API_KEY exists?:", bool(os.getenv("API_KEY")))

# Google Generative AI(Gemini) SDK 초기화: 환경변수 API_KEY 사용
genai.configure(api_key=os.getenv("API_KEY"))

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="LLM Quiz API")

# ----- 요청/응답 모델 및 예외 정의 -----

class InBody(BaseModel):
    """ 클라이언트가 보내는 JSON 바디 스키마: 텍스트 한 덩어리 """
    text: str

class QuizChoiceError(Exception):
    """ 4지선다 검증용으로 쓸 수 있는 커스텀 예외 (현재는 사용하지 않지만 확장 대비) """
    pass

# 시스템 프롬프트: 모델에게 역할/출력 포맷을 엄격히 지시
SYSTEM_MESSAGE = """당신은 대학 강의 내용을 정리하고 요약하여 객관식 퀴즈를 만드는 전문가다.
아래 텍스트를 요약하여 정리하고, 핵심 개념만 담은 4지선다형 퀴즈 2개를 만들어라.
단, 불필요한 예시/잡담은 금지하고,
난이도는 초-중급으로 맞추고,
반드시 JSON 스키마에 맞춰라.
JSON 스키마:
{
  "summary": "string",
  "quizzes": [
    { "question": "string", "choices": ["A","B","C","D"], "answer_index": 0 }
  ]
}
출력은 JSON만 반환하라.
"""

# ----- 엔드포인트 구현 -----

@app.post("/summarize_and_quiz")
def summarize_and_quiz(body: InBody):
    """
    입력 텍스트를 요약하고, 4지선다형 퀴즈 2개를 생성해 JSON으로 반환.
    - 입력 검증
    - API_KEY 존재 검증
    - Gemini 호출 및 원시 응답 로깅
    - 코드블록(```json ...) 제거
    - JSON 파싱/스키마/값 검증
    """
    # 1) 입력 검증: 공백만 있으면 400
    if not body.text.strip():
        raise HTTPException(400, "text is empty")

    # 2) 환경변수에 API_KEY가 아직도 없으면 500
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(
            500,
            "Missing API_KEY (확인순서: 1) 실행 경로의 .env 존재 2) 파일명이 정확히 '.env' 3) 'API_KEY=...' 형식 4) uvicorn --env-file 사용)"
        )

    try:
        # 3) 모델 인스턴스 준비 및 프롬프트 구성
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"{SYSTEM_MESSAGE}\n입력 텍스트:\n\"\"\"\n{body.text}\n\"\"\"\n"

        # 4) 모델 호출
        resp = model.generate_content(prompt)

        # 5) SDK 객체에서 텍스트만 추출 (없으면 빈 문자열)
        raw = (getattr(resp, "text", None) or "").strip()

        # 6) 원문 로그: 문제 발생 시 디버깅을 돕기 위해 앞 1000자만 기록
        logger.info(f"[LLM RAW START]\n{raw[:1000]}\n[LLM RAW END]")

        # 7) 모델이 ```json ... ``` 같은 코드블록으로 감쌌을 경우 제거
        if raw.startswith("```"):
            raw = raw.strip("`")               # 백틱 제거
            raw = raw.split("\n", 1)[-1]       # 첫 줄(펜스 언어 표시) 제거
            if raw.strip().startswith("json"): # ```json으로 시작하는 경우 한 줄 더 제거
                raw = raw.split("\n", 1)[-1]

        # 8) JSON 디코딩 시도
        try:
            data = json.loads(raw)
        except Exception as pe:
            logger.exception("JSON parse failed")
            # 모델이 포맷을 어긴 경우 등을 500으로 명확히 반환
            raise HTTPException(500, f"JSON parse failed: {pe}")

        # 9) 최상위 스키마 검증
        if "summary" not in data or "quizzes" not in data:
            raise HTTPException(502, "Model returned invalid schema")

        # 10) 각 퀴즈 항목에 대해 4지선다/정답 인덱스 검증
        for q in data["quizzes"]:
            choices = q.get("choices", [])
            if len(choices) != 4:
                raise HTTPException(422, "Each quiz must have 4 choices")
            ai = q.get("answer_index", None)
            if type(ai) is not int or not (0 <= ai < 4):
                raise HTTPException(422, "answer_index must be 0..3")

        # 11) 모든 검증 통과 → 그대로 응답
        return data

    # FastAPI HTTPException은 그대로 상위로 전달
    except HTTPException:
        raise
    # 그 외 예기치 못한 에러는 502(업스트림/모델 오류)로 통일
    except Exception as e:
        logger.exception("Upstream/model error")
        raise HTTPException(502, f"Upstream model error: {e!r}")