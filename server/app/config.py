"""서버 설정. .env 를 읽어 환경변수를 로드한다.
API 키는 코드에 두지 않으며, server/.env 에서만 읽는다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# server/ 디렉터리 기준 경로
SERVER_DIR = Path(__file__).resolve().parent.parent          # .../server
REPO_ROOT = SERVER_DIR.parent                                # .../snaptok_v2
WEB_DIR = REPO_ROOT / "Snaptok"                              # 정적 웹(/app)
DATA_DIR = SERVER_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "snaptok.db"
PLACES_SEED_PATH = DATA_DIR / "places_seed.json"

# .env 로드 (server/.env)
load_dotenv(SERVER_DIR / ".env")


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _get_float(name: str, default: float) -> float:
    raw = _get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # LLM
    llm_provider: str
    llm_model: str
    llm_api_key: str
    # 카카오
    kakao_rest_api_key: str
    # 구글 캘린더
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str
    google_calendar_id: str
    calendar_sync: str  # off | google
    # 임계값
    confidence_action: float
    confidence_memory: float
    # LLM 게이트웨이(OpenAI 호환) base_url
    llm_base_url: str
    # 시간대 / 시연 날짜
    default_timezone: str
    demo_today: str  # "" 이면 실제 오늘

    @property
    def llm_enabled(self) -> bool:
        """실제 LLM 호출 가능 여부. 키가 없으면 mock 모드."""
        return bool(self.llm_api_key)

    @property
    def calendar_sync_enabled(self) -> bool:
        return self.calendar_sync.lower() == "google"


def load_settings() -> Settings:
    return Settings(
        llm_provider=_get("LLM_PROVIDER", "anthropic"),
        llm_model=_get("LLM_MODEL", "claude-sonnet-5"),
        llm_api_key=_get("LLM_API_KEY"),
        llm_base_url=_get("LLM_BASE_URL"),
        kakao_rest_api_key=_get("KAKAO_REST_API_KEY"),
        google_client_id=_get("GOOGLE_CLIENT_ID"),
        google_client_secret=_get("GOOGLE_CLIENT_SECRET"),
        google_refresh_token=_get("GOOGLE_REFRESH_TOKEN"),
        google_calendar_id=_get("GOOGLE_CALENDAR_ID"),
        calendar_sync=_get("CALENDAR_SYNC", "off") or "off",
        confidence_action=_get_float("CONFIDENCE_ACTION", 0.7),
        confidence_memory=_get_float("CONFIDENCE_MEMORY", 0.55),
        default_timezone=_get("DEFAULT_TIMEZONE", "Asia/Seoul"),
        demo_today=_get("DEMO_TODAY"),
    )


settings = load_settings()
