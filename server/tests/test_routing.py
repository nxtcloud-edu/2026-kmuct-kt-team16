"""T6: 라우팅 순수 함수 테스트 (DB 없이)."""
from datetime import datetime

from app import routing
from app.llm import schema

TODAY = "2026-09-20"
NOW = datetime(2026, 9, 20, 12, 0, 0)
CA, CM = 0.7, 0.55


def _norm(obj):
    return schema.normalize(obj)


# ---------- evidence 근거 검사 ----------

def test_evidence_supported_true():
    item = {"date": "2026-09-25", "date_role": "expiry", "evidence": "사용기한 9/25"}
    assert routing.evidence_supported(item, "스타벅스 아메리카노 사용기한 9/25") is True


def test_evidence_not_in_visible_text():
    # visible_text 에 9/25 근거 없음 -> 근거 미달
    item = {"date": "2026-09-25", "date_role": "expiry", "evidence": "사용기한 9/25"}
    assert routing.evidence_supported(item, "스타벅스 아메리카노 기프티콘") is False


def test_evidence_fabricated_date_rejected():
    # 모델이 없는 날짜를 지어낸 경우: visible_text 에 그 날짜 없음
    item = {"date": "2026-12-31", "date_role": "deadline", "evidence": "12/31 마감"}
    assert routing.evidence_supported(item, "행사 안내 (날짜 없음)") is False


# ---------- ACTION 라우팅 ----------

def test_action_saves_event():
    data = _norm({
        "type": "ACTION", "confidence": 0.9, "title": "아이디어톤",
        "category": "공모전", "visible_text": "신청 마감 9/27 18:00",
        "items": [{"kind": "task", "action_type": "submit", "title": "신청 마감",
                   "date_role": "deadline", "date": "2026-09-27", "time": "18:00",
                   "evidence": "신청 마감 9/27"}],
        "place": {"name": None, "area": None}, "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "action"
    assert len(plan.events) == 1
    assert "제출" in plan.events[0].title  # "{title} · {행동}"


def test_action_two_items():
    data = _norm({
        "type": "ACTION", "confidence": 0.9, "title": "공모전",
        "category": "공모전", "visible_text": "접수 마감 9/27\n본선 발표 9/29",
        "items": [
            {"kind": "task", "action_type": "submit", "date_role": "deadline",
             "date": "2026-09-27", "evidence": "접수 마감 9/27"},
            {"kind": "event", "action_type": "attend", "date_role": "event",
             "date": "2026-09-29", "evidence": "본선 발표 9/29"},
        ],
        "place": {"name": None, "area": None}, "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert len(plan.events) == 2


def test_action_low_confidence_goes_review():
    data = _norm({
        "type": "ACTION", "confidence": 0.5, "title": "x", "category": None,
        "visible_text": "마감 9/27", "items": [{"kind": "task", "date_role": "deadline",
        "date": "2026-09-27", "evidence": "마감 9/27"}],
        "place": {"name": None, "area": None}, "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "review"


def test_action_no_valid_item_goes_review():
    # 근거 없는 날짜만 -> 유효항목 0 -> review
    data = _norm({
        "type": "ACTION", "confidence": 0.9, "title": "x", "category": None,
        "visible_text": "행사 안내", "items": [{"kind": "event", "date_role": "event",
        "date": "2026-12-31", "evidence": "12/31"}],
        "place": {"name": None, "area": None}, "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "review"
    assert plan.review.reason == "근거 있는 날짜 없음"


# ---------- 지난 날짜 -> 보관함 missed ----------

def test_past_deadline_goes_library_missed():
    data = _norm({
        "type": "ACTION", "confidence": 0.9, "title": "지난 마감", "category": "공모전",
        "visible_text": "마감 9/10", "items": [{"kind": "task", "action_type": "submit",
        "date_role": "deadline", "date": "2026-09-10", "evidence": "마감 9/10"}],
        "place": {"name": None, "area": None}, "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "action"
    assert len(plan.events) == 0
    assert len(plan.library) == 1
    assert plan.library[0].missed is True


# ---------- 쿠폰 이중 저장 ----------

def test_coupon_double_save():
    data = _norm({
        "type": "ACTION", "confidence": 0.9, "title": "스타벅스 기프티콘", "category": "쿠폰",
        "visible_text": "사용기한 9/25", "items": [{"kind": "task", "action_type": "use",
        "date_role": "expiry", "date": "2026-09-25", "evidence": "사용기한 9/25"}],
        "place": {"name": None, "area": None}, "brand": "스타벅스", "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "action"
    assert len(plan.events) == 1                 # 만료 알림용 일정
    assert len(plan.library) == 1                # 보관함 쿠폰
    assert plan.library[0].category == "쿠폰"
    assert plan.library[0].brand == "스타벅스"
    assert plan.library[0].geo_type == "brand"
    assert plan.library[0].expiry == "2026-09-25"


# ---------- MEMORY ----------

def test_memory_saves_library():
    data = _norm({
        "type": "MEMORY", "confidence": 0.9, "title": "연남동 파스타집", "category": "맛집",
        "visible_text": "연남동 맛집", "items": [],
        "place": {"name": "연남동 파스타집", "area": "연남동"}, "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "memory"
    assert len(plan.library) == 1
    assert plan.library[0].area == "연남동"


def test_memory_low_confidence_goes_review():
    data = _norm({
        "type": "MEMORY", "confidence": 0.4, "title": "x", "category": "맛집",
        "visible_text": "", "items": [], "place": {"name": None, "area": None},
        "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "review"


# ---------- UNCERTAIN ----------

def test_uncertain_goes_review():
    data = _norm({
        "type": "UNCERTAIN", "confidence": 0.4, "title": "세미나", "category": None,
        "visible_text": "", "items": [], "place": {"name": None, "area": None},
        "brand": None, "note": "",
    })
    plan = routing.plan_routing(data, NOW, CA, CM)
    assert plan.decision == "review"
