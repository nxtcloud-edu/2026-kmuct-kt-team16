"""LLM 추상화 계층.

공급자·모델은 환경변수로 교체(멀티모달, JSON 출력).
키가 없으면 mock 공급자로 동작한다(테스트/오프라인).
"""
from __future__ import annotations

from ..config import settings
from .base import AnalysisProvider
from .mock_provider import MockProvider


def get_provider() -> AnalysisProvider:
    """설정에 맞는 분석 공급자 반환. 키 없으면 mock."""
    if not settings.llm_enabled:
        return MockProvider()

    provider = settings.llm_provider.lower()
    if provider == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )
    if provider == "anthropic":
        # 지연 import: anthropic 경로에서만 httpx 사용
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    # 알 수 없는 공급자는 mock 으로 폴백(서버가 죽지 않게)
    return MockProvider()
