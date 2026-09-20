"""T5: LLM 추상화 계층 테스트(mock 모드, 실제 키 불필요)."""
from app.llm import schema
from app.llm.mock_provider import MockProvider

TODAY = "2026-09-20"


# ---------------- schema 파싱/정규화 ----------------

def test_parse_valid_json():
    text = '{"type":"ACTION","confidence":0.9,"title":"t","category":"쿠폰",' \
           '"visible_text":"사용기한 2026-09-25","items":[{"kind":"task",' \
           '"action_type":"use","title":"x","date_role":"expiry","date":"2026-09-25",' \
           '"time":null,"end_time":null,"location":"","evidence":"사용기한 2026-09-25"}],' \
           '"place":{"name":null,"area":null},"brand":"스타벅스","note":"n"}'
    data, ok = schema.parse_response(text)
    assert ok is True
    assert data["type"] == "ACTION"
    assert data["confidence"] == 0.9
    assert len(data["items"]) == 1
    assert data["items"][0]["date"] == "2026-09-25"
    assert data["brand"] == "스타벅스"


def test_parse_code_fence_stripped():
    text = "```json\n{\"type\":\"MEMORY\",\"confidence\":0.7,\"title\":\"t\",\"category\":\"맛집\"," \
           "\"visible_text\":\"\",\"items\":[],\"place\":{\"name\":\"x\",\"area\":\"연남동\"}," \
           "\"brand\":null,\"note\":\"\"}\n```"
    data, ok = schema.parse_response(text)
    assert ok is True
    assert data["type"] == "MEMORY"
    assert data["place"]["area"] == "연남동"


def test_parse_failure_falls_back_uncertain():
    data, ok = schema.parse_response("이건 JSON 이 아니다")
    assert ok is False
    assert data["type"] == "UNCERTAIN"
    assert data["items"] == []


def test_invalid_date_item_dropped():
    text = '{"type":"ACTION","confidence":0.8,"title":"t","category":null,"visible_text":"",' \
           '"items":[{"kind":"task","date":"내일","evidence":"내일"},' \
           '{"kind":"event","date":"2026-10-01","evidence":"10-01"}],' \
           '"place":{"name":null,"area":null},"brand":null,"note":""}'
    data, ok = schema.parse_response(text)
    assert ok is True
    # 형식 안 맞는 날짜(내일) item 은 제거, 유효한 1건만
    assert len(data["items"]) == 1
    assert data["items"][0]["date"] == "2026-10-01"


def test_unknown_category_becomes_etc():
    text = '{"type":"MEMORY","confidence":0.5,"title":"t","category":"우주여행",' \
           '"visible_text":"","items":[],"place":{"name":null,"area":null},"brand":null,"note":""}'
    data, ok = schema.parse_response(text)
    assert data["category"] == "기타"


def test_confidence_clamped():
    text = '{"type":"ACTION","confidence":5,"title":"t","category":null,"visible_text":"",' \
           '"items":[],"place":{"name":null,"area":null},"brand":null,"note":""}'
    data, _ = schema.parse_response(text)
    assert data["confidence"] == 1.0


def test_invalid_type_becomes_uncertain():
    text = '{"type":"WEIRD","confidence":0.5,"title":"t","category":null,"visible_text":"",' \
           '"items":[],"place":{"name":null,"area":null},"brand":null,"note":""}'
    data, _ = schema.parse_response(text)
    assert data["type"] == "UNCERTAIN"


# ---------------- MockProvider ----------------

def _analyze(hint):
    p = MockProvider()
    return p.analyze(b"fake", "image/jpeg", None, TODAY, "Asia/Seoul", hint=hint)


def test_mock_coupon_starbucks():
    r = _analyze("starbucks_coupon.jpg")
    assert r.mode == "mock"
    assert r.data["type"] == "ACTION"
    assert r.data["category"] == "쿠폰"
    assert r.data["brand"] == "스타벅스"
    assert r.data["items"][0]["action_type"] == "use"
    assert r.data["items"][0]["date_role"] == "expiry"


def test_mock_food_area():
    r = _analyze("yeonnam_pasta_food.png")
    assert r.data["type"] == "MEMORY"
    assert r.data["category"] == "맛집"
    assert r.data["place"]["area"] == "연남동"


def test_mock_contest_two_items():
    r = _analyze("contest_ideathon.jpg")
    assert r.data["type"] == "ACTION"
    assert len(r.data["items"]) == 2
    roles = {i["date_role"] for i in r.data["items"]}
    assert roles == {"deadline", "event"}


def test_mock_hackathon_single_event_no_deadline():
    r = _analyze("hackathon_poster.jpg")
    assert r.data["type"] == "ACTION"
    assert len(r.data["items"]) == 1
    assert r.data["items"][0]["date_role"] == "event"


def test_mock_seminar_uncertain():
    r = _analyze("seminar_notice.jpg")
    assert r.data["type"] == "UNCERTAIN"
    assert r.data["items"] == []


def test_mock_no_hint_uncertain():
    r = _analyze(None)
    assert r.data["type"] == "UNCERTAIN"
    assert r.data["items"] == []


def test_mock_dates_are_today_relative_and_valid():
    r = _analyze("coupon.jpg")
    # expiry 는 오늘(2026-09-20)+5 = 2026-09-25, 형식 유효
    assert r.data["items"][0]["date"] == "2026-09-25"


# ---------------- provider 선택 ----------------

def test_get_provider_returns_mock_without_key():
    # 테스트 환경엔 LLM_API_KEY 가 없으므로 mock 이어야 한다.
    from app import llm
    from app.config import settings
    if settings.llm_enabled:
        import pytest
        pytest.skip("실제 키가 설정된 환경(live) - mock 선택 검증 생략")
    prov = llm.get_provider()
    assert prov.mode == "mock"
