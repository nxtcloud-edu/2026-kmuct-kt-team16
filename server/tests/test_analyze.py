"""T6: /api/analyze 엔드포인트 테스트 (mock 공급자, DB 연동)."""
import io


def _img(name):
    # 최소 JPEG 헤더 바이트(내용은 mock 이 파일명 힌트로 분류하므로 무관)
    return (name, io.BytesIO(b"\xff\xd8\xff\xe0fake-jpeg-bytes"), "image/jpeg")


def _post(client, name, request_id=None):
    files = {"image": _img(name)}
    data = {}
    if request_id:
        data["request_id"] = request_id
    return client.post("/api/analyze", files=files, data=data)


def test_analyze_coupon_double_save(client):
    r = _post(client, "starbucks_coupon.jpg")
    assert r.status_code == 200
    j = r.json()
    assert j["decision"] == "action"
    kinds = [(x["kind"], x["status"]) for x in j["results"]]
    # 일정 저장 + 보관함 쿠폰 저장
    assert ("event", "saved") in kinds
    assert ("library", "saved") in kinds
    badges = [x["badge"] for x in j["results"]]
    assert "보관함 쿠폰" in badges

    # state 로 실제 저장 확인
    s = client.get("/api/state").json()
    assert len(s["events"]) >= 1
    assert any(l["category"] == "쿠폰" for l in s["library"])


def test_analyze_memory_food(client):
    r = _post(client, "yeonnam_pasta_food.jpg")
    j = r.json()
    assert j["decision"] == "memory"
    s = client.get("/api/state").json()
    assert any(l["category"] == "맛집" for l in s["library"])


def test_analyze_contest_two_events(client):
    r = _post(client, "contest_ideathon.jpg")
    j = r.json()
    assert j["decision"] == "action"
    saved_events = [x for x in j["results"] if x["kind"] == "event" and x["status"] == "saved"]
    assert len(saved_events) == 2


def test_analyze_seminar_review(client):
    r = _post(client, "seminar_notice.jpg")
    j = r.json()
    assert j["decision"] == "review"
    s = client.get("/api/state").json()
    assert len(s["review"]) == 1


def test_analyze_duplicate_skipped(client):
    r1 = _post(client, "contest_ideathon.jpg")
    assert r1.json()["decision"] == "action"
    # 같은 내용 다시 -> 중복 건너뜀
    r2 = _post(client, "contest_ideathon.jpg")
    j2 = r2.json()
    dups = [x for x in j2["results"] if x["status"] == "dup"]
    assert len(dups) == 2  # 두 일정 모두 중복

    s = client.get("/api/state").json()
    # 이벤트가 2개만 유지(중복으로 안 늘어남)
    assert len(s["events"]) == 2


def test_analyze_idempotent_request_id(client):
    rid = "req-123"
    r1 = _post(client, "starbucks_coupon.jpg", request_id=rid)
    j1 = r1.json()
    # 같은 request_id 재요청 -> 동일 결과, 새 항목 안 생김
    r2 = _post(client, "starbucks_coupon.jpg", request_id=rid)
    j2 = r2.json()
    assert j1["results"] == j2["results"]

    s = client.get("/api/state").json()
    # 쿠폰 1개, 일정 1개만 (중복 저장 안 됨)
    assert sum(1 for l in s["library"] if l["category"] == "쿠폰") == 1


def test_analyze_summary_banner(client):
    r = _post(client, "starbucks_coupon.jpg")
    j = r.json()
    assert "캘린더" in j["summary"] or "보관함" in j["summary"]


def test_analyze_empty_image_400(client):
    import io as _io
    files = {"image": ("empty.jpg", _io.BytesIO(b""), "image/jpeg")}
    r = client.post("/api/analyze", files=files)
    assert r.status_code == 400


def test_analyze_food_gets_coords_and_geotarget(client):
    # 연남동 맛집 -> 좌표 붙고 geo_enabled -> geoTargets 에 등장 (T7 통합)
    _post(client, "yeonnam_pasta_food.jpg")
    s = client.get("/api/state").json()
    lib = [l for l in s["library"] if l["category"] == "맛집"]
    assert lib, "맛집 항목이 저장되어야 함"
    item = lib[0]
    assert item["lat"] == 37.5663 and item["lng"] == 126.9254
    assert item["geo_enabled"] is True
    # geoTargets 에 포함
    assert any(t["id"] == item["id"] for t in s["geoTargets"])


def test_analyze_coupon_brand_geotarget(client):
    # 스타벅스 쿠폰 -> 보관함 쿠폰 brand geoType, branches, geoTargets 등장
    _post(client, "starbucks_coupon.jpg")
    s = client.get("/api/state").json()
    coupon = [l for l in s["library"] if l["category"] == "쿠폰"]
    assert coupon
    item = coupon[0]
    assert item["geoType"] == "brand"
    assert item["brand"] == "스타벅스"
    assert len(item["branches"]) == 3
    assert any(t["id"] == item["id"] for t in s["geoTargets"])
