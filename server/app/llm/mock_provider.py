"""Mock 분석 공급자.

키가 없거나 테스트/오프라인일 때 사용한다. 실제 이미지 픽셀을 읽지 못하므로,
파일명 힌트(hint)의 키워드로 범용 분류한다. 특정 이미지에 맞춘 하드코딩이 아니라
'스타벅스/쿠폰/파스타/마감' 같은 일반 키워드 규칙이다.

hint 가 없거나 매칭이 없으면 UNCERTAIN 을 반환한다(없는 날짜를 지어내지 않는다).
날짜가 필요한 규칙은 '오늘로부터 N일' 형태로 today 기준 상대 날짜를 만든다
(테스트에서 today 를 고정해 결정적으로 검증 가능).
"""
from __future__ import annotations

from datetime import date, timedelta

from . import schema
from .base import AnalysisProvider, AnalysisResult


def _d(today: str, plus_days: int) -> str:
    y, m, dd = (int(x) for x in today.split("-"))
    return (date(y, m, dd) + timedelta(days=plus_days)).isoformat()


class MockProvider(AnalysisProvider):
    mode = "mock"

    def analyze(
        self,
        image_bytes: bytes,
        content_type: str,
        captured_at: str | None,
        today: str,
        timezone: str,
        hint: str | None = None,
    ) -> AnalysisResult:
        h = (hint or "").lower()

        def result(obj: dict) -> AnalysisResult:
            return AnalysisResult(schema.normalize(obj), raw="[mock]", parsed=True, mode="mock")

        # --- 쿠폰/기프티콘 (use) ---
        if any(k in h for k in ("coupon", "쿠폰", "gifticon", "기프티콘", "sbux", "스타벅스", "starbucks")):
            brand = "스타벅스" if any(k in h for k in ("sbux", "스타벅스", "starbucks")) else None
            expiry = _d(today, 5)  # 오늘+5일 만료(데모용, today 기준 결정적)
            return result({
                "type": "ACTION", "confidence": 0.9,
                "title": (brand or "브랜드") + " 기프티콘",
                "category": "쿠폰",
                "visible_text": f"기프티콘 사용기한 {expiry}",
                "items": [{
                    "kind": "task", "action_type": "use", "title": "기프티콘 사용",
                    "date_role": "expiry", "date": expiry, "time": None, "end_time": None,
                    "location": "", "evidence": f"사용기한 {expiry}",
                }],
                "place": {"name": None, "area": None},
                "brand": brand, "note": "쿠폰 만료 전 사용",
            })

        # --- 맛집 (MEMORY, specific/area) ---
        if any(k in h for k in ("food", "맛집", "pasta", "파스타", "restaurant")):
            area = None
            for a in ("연남", "성수", "역삼", "yeonnam", "seongsu", "yeoksam"):
                if a in h:
                    area = {"yeonnam": "연남동", "seongsu": "성수", "yeoksam": "역삼"}.get(a, a)
                    break
            return result({
                "type": "MEMORY", "confidence": 0.9,
                "title": (area or "") + " 맛집" if area else "맛집",
                "category": "맛집",
                "visible_text": (area or "") + " 파스타 맛집",
                "items": [],
                "place": {"name": (area or "") + " 파스타집" if area else "파스타집", "area": area},
                "brand": None, "note": "방문 시 다시 보기",
            })

        # --- 공모전/포스터 (마감 + 발표일 2건) ---
        if any(k in h for k in ("contest", "공모전", "ideathon", "아이디어톤")):
            deadline = _d(today, 7)
            final = _d(today, 9)
            return result({
                "type": "ACTION", "confidence": 0.85,
                "title": "공모전",
                "category": "공모전",
                "visible_text": f"접수 마감 {deadline}\n본선 발표 {final}",
                "items": [
                    {"kind": "task", "action_type": "submit", "title": "접수 마감",
                     "date_role": "deadline", "date": deadline, "time": "18:00", "end_time": None,
                     "location": "온라인", "evidence": f"접수 마감 {deadline}"},
                    {"kind": "event", "action_type": "attend", "title": "본선 발표",
                     "date_role": "event", "date": final, "time": "14:00", "end_time": None,
                     "location": "온라인", "evidence": f"본선 발표 {final}"},
                ],
                "place": {"name": None, "area": None},
                "brand": None, "note": "공모전 일정",
            })

        # --- 해커톤 포스터 (행사 1건, 마감 없음) ---
        if any(k in h for k in ("hackathon", "해커톤")):
            ev = _d(today, 0)
            return result({
                "type": "ACTION", "confidence": 0.88,
                "title": "해커톤",
                "category": "공모전",
                "visible_text": f"행사 {ev} 08:00-21:30\nAWS 역삼 센터필드",
                "items": [{
                    "kind": "event", "action_type": "attend", "title": "해커톤 참석",
                    "date_role": "event", "date": ev, "time": "08:00", "end_time": "21:30",
                    "location": "AWS 역삼 센터필드", "evidence": f"행사 {ev} 08:00-21:30",
                }],
                "place": {"name": "AWS 역삼 센터필드", "area": "역삼"},
                "brand": None, "note": "행사 당일만, 신청 마감 없음",
            })

        # --- 전시/팝업 (MEMORY, 좌표) ---
        if any(k in h for k in ("expo", "전시", "popup", "팝업", "exhibition")):
            return result({
                "type": "MEMORY", "confidence": 0.85,
                "title": "전시/팝업",
                "category": "전시회",
                "visible_text": "성수 전시/팝업 안내",
                "items": [],
                "place": {"name": None, "area": "성수"},
                "brand": None, "note": "관람 후보",
            })

        # --- 여행지 (MEMORY, 좌표 없음: 해외) ---
        if any(k in h for k in ("trip", "여행", "kyoto", "교토", "travel")):
            return result({
                "type": "MEMORY", "confidence": 0.8,
                "title": "여행지",
                "category": "여행지",
                "visible_text": "여행 후보 스팟",
                "items": [],
                "place": {"name": None, "area": None},
                "brand": None, "note": "여행 후보",
            })

        # --- 패션 (MEMORY) ---
        if any(k in h for k in ("fashion", "패션", "옷", "clothes")):
            return result({
                "type": "MEMORY", "confidence": 0.8,
                "title": "패션 아이템",
                "category": "패션",
                "visible_text": "옷 상품 정보",
                "items": [],
                "place": {"name": None, "area": None},
                "brand": None, "note": "쇼핑 관심",
            })

        # --- 날짜 역할 애매 (UNCERTAIN) ---
        if any(k in h for k in ("seminar", "세미나", "uncertain", "애매")):
            return result({
                "type": "UNCERTAIN", "confidence": 0.4,
                "title": "세미나 안내",
                "category": None,
                "visible_text": "세미나 안내 (날짜 역할 불분명)",
                "items": [],
                "place": {"name": None, "area": None},
                "brand": None, "note": "날짜 역할 불분명",
            })

        # --- 밈/기타 ---
        if any(k in h for k in ("meme", "밈", "etc", "기타")):
            return result({
                "type": "MEMORY", "confidence": 0.6,
                "title": "저장한 이미지",
                "category": "기타",
                "visible_text": "",
                "items": [],
                "place": {"name": None, "area": None},
                "brand": None, "note": "기타",
            })

        # 기본값: 힌트가 없거나 매칭 실패 -> UNCERTAIN (없는 날짜 생성 금지)
        return AnalysisResult(
            schema.uncertain(title="분석 확인 필요", note="mock: 힌트 없음"),
            raw="[mock:default]", parsed=True, mode="mock",
        )
