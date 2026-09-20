"""분석 공급자 인터페이스."""
from __future__ import annotations

from typing import Protocol


class AnalysisResult:
    """분석 결과 컨테이너.

    - data: 정규화된 dict(schema.normalize 결과)
    - raw: LLM 원시 텍스트(디버그용, mock 은 생성 텍스트)
    - parsed: JSON 파싱 성공 여부
    - mode: "live" | "mock"
    """

    def __init__(self, data: dict, raw: str = "", parsed: bool = True, mode: str = "live"):
        self.data = data
        self.raw = raw
        self.parsed = parsed
        self.mode = mode


class AnalysisProvider(Protocol):
    mode: str  # "live" | "mock"

    def analyze(
        self,
        image_bytes: bytes,
        content_type: str,
        captured_at: str | None,
        today: str,
        timezone: str,
        hint: str | None = None,
    ) -> AnalysisResult:
        """이미지를 분석해 AnalysisResult 반환.

        hint: 파일명 등 부가 힌트(선택). live 공급자는 무시하거나 참고만,
        mock 공급자는 오프라인 분류에 활용한다. LLM 출력을 특정 이미지에
        하드코딩하는 용도가 아니다(파일명 키워드 기반의 범용 규칙).
        """
        ...
