"""OpenAI 호환 게이트웨이 분석 공급자 (해커톤 주최측 게이트웨이).

openai 패키지의 OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY) 로
chat.completions 를 호출한다. 이미지는 image_url 에 base64 data URL 로 넣고,
기존과 동일한 프롬프트로 동일한 JSON 을 받는다. 코드펜스 제거 후 파싱.
키는 settings(LLM_API_KEY)에서만 온다.
"""
from __future__ import annotations

import base64

from openai import OpenAI

from . import prompt, schema
from .base import AnalysisProvider, AnalysisResult

_MEDIA = {
    "image/jpeg": "image/jpeg", "image/jpg": "image/jpeg",
    "image/png": "image/png", "image/webp": "image/webp", "image/gif": "image/gif",
}


def _media_type(content_type: str) -> str:
    ct = (content_type or "").lower().split(";")[0].strip()
    return _MEDIA.get(ct, "image/jpeg")


class OpenAIProvider(AnalysisProvider):
    mode = "live"

    def __init__(self, api_key: str, model: str, base_url: str):
        self._model = model
        # base_url 이 비면 openai 기본 엔드포인트. 게이트웨이는 base_url 지정.
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)

    def _call(self, image_data_url: str, system: str, user: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                },
            ],
        )
        return (resp.choices[0].message.content or "").strip()

    def analyze(
        self,
        image_bytes: bytes,
        content_type: str,
        captured_at: str | None,
        today: str,
        timezone: str,
        hint: str | None = None,
    ) -> AnalysisResult:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        data_url = f"data:{_media_type(content_type)};base64,{b64}"
        system = prompt.build_system_prompt()
        user = prompt.build_user_prompt(captured_at, today, timezone)

        raw = self._call(data_url, system, user)
        result, ok = schema.parse_response(raw)
        if ok:
            return AnalysisResult(result, raw=raw, parsed=True, mode="live")
        # 파싱 실패 -> 1회 재시도(더 강하게 JSON 만)
        retry_user = user + "\n반드시 유효한 JSON 오브젝트 하나만 출력하라. 다른 텍스트 금지."
        raw2 = self._call(data_url, system, retry_user)
        result2, ok2 = schema.parse_response(raw2)
        return AnalysisResult(result2, raw=raw2, parsed=ok2, mode="live")
