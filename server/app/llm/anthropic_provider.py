"""Anthropic Claude 멀티모달 분석 공급자.

Anthropic Messages API (POST /v1/messages) 를 httpx 로 직접 호출한다.
- 이미지: content block {type:image, source:{type:base64, media_type, data}}
- JSON 출력: 시스템 프롬프트로 강제 + 파싱 실패 시 1회 재시도(명세 4.2), 그래도 실패면 UNCERTAIN.
API 키는 config(settings.llm_api_key)에서만 온다. 코드/로그에 키를 남기지 않는다.
"""
from __future__ import annotations

import base64

import httpx

from . import prompt, schema
from .base import AnalysisProvider, AnalysisResult

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"
_TIMEOUT = 60.0

# Anthropic 이 지원하는 media_type 로 정규화
_MEDIA = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
    "image/webp": "image/webp",
    "image/gif": "image/gif",
}


def _media_type(content_type: str) -> str:
    ct = (content_type or "").lower().split(";")[0].strip()
    return _MEDIA.get(ct, "image/jpeg")


class AnthropicProvider(AnalysisProvider):
    mode = "live"

    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model

    def _call(self, image_b64: str, media_type: str, system: str, user: str) -> str:
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        }
        body = {
            "model": self._model,
            "max_tokens": 1024,
            "system": system,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": user},
                    ],
                }
            ],
        }
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(_API_URL, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
        # content: [{type:text, text:...}]
        parts = data.get("content", [])
        texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
        return "\n".join(texts).strip()

    def analyze(
        self,
        image_bytes: bytes,
        content_type: str,
        captured_at: str | None,
        today: str,
        timezone: str,
        hint: str | None = None,
    ) -> AnalysisResult:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        media_type = _media_type(content_type)
        system = prompt.build_system_prompt()
        user = prompt.build_user_prompt(captured_at, today, timezone)

        # 1차 시도
        try:
            raw = self._call(image_b64, media_type, system, user)
        except (httpx.HTTPError, ValueError, KeyError):
            # 네트워크/HTTP 오류는 상위(analyze route)에서 "분석 실패"로 처리하도록 예외 전파
            raise

        result, ok = schema.parse_response(raw)
        if ok:
            return AnalysisResult(result, raw=raw, parsed=True, mode="live")

        # 파싱 실패 -> 1회 재시도(더 강하게 JSON 만 요청)
        retry_user = user + "\n반드시 유효한 JSON 오브젝트 하나만 출력하라. 다른 텍스트 금지."
        try:
            raw2 = self._call(image_b64, media_type, system, retry_user)
        except (httpx.HTTPError, ValueError, KeyError):
            return AnalysisResult(schema.uncertain(note="LLM 호출 실패"), raw=raw, parsed=False, mode="live")

        result2, ok2 = schema.parse_response(raw2)
        return AnalysisResult(result2, raw=raw2, parsed=ok2, mode="live")
