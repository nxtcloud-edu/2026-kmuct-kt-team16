"""RoutingPlan 을 DB 에 반영한다. 중복 판정·이미지 연결·활동기록(되돌리기용)·좌표화 훅.

좌표화(geocode.attach_location)는 T7 에서 구현한다. 지금은 안전한 no-op 훅을 두고,
T7 에서 실제 좌표/geo_enabled 를 채운다.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from . import dedup, models, routing, serializers


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _find_dup_event(db: Session, title: str, date: str) -> models.Event | None:
    for e in db.query(models.Event).filter(models.Event.date == date).all():
        if dedup.is_duplicate(e.title, title):
            return e
    return None


def _find_dup_library(db: Session, title: str, category: str | None) -> models.LibraryItem | None:
    q = db.query(models.LibraryItem)
    if category is not None:
        q = q.filter(models.LibraryItem.category == category)
    for l in q.all():
        if dedup.is_duplicate(l.title, title):
            return l
    return None


# 좌표화 훅: T7 에서 실제 구현으로 교체. 반환: (geo_type, lat, lng, radius, geo_enabled, branches_json)
def _attach_location(item: models.LibraryItem) -> None:
    try:
        from . import geocode  # T7 에서 추가
    except ImportError:
        return
    geocode.attach_location(item)


def apply_plan(
    db: Session,
    plan: "routing.RoutingPlan",
    *,
    image_id: str | None,
    display_image: str | None,
    extracted: dict,
    source_label: str = "Snaptok AI",
) -> dict:
    """plan 을 DB 에 반영하고, 웹에 돌려줄 결과(배지 포함)를 만든다.

    반환 dict:
      {
        "decision": ...,
        "results": [ {kind, status, id, title, badge}... ],  # 항목별 처리 결과
        "created": {"events":[id], "library":[id], "review":[id]},  # 되돌리기 연쇄용
        "recent_id": ...,
      }
    """
    created = {"events": [], "library": [], "review": []}
    results: list[dict] = []

    # --- 확인 필요 ---
    if plan.decision == "review":
        rid = _new_id("rev")
        r = models.ReviewItem(
            id=rid, title=plan.review.title, reason=plan.review.reason,
            category=plan.review.category, image_id=image_id, display_image=display_image,
            extracted=json.dumps(extracted, ensure_ascii=False),
        )
        db.add(r)
        created["review"].append(rid)
        results.append({"kind": "review", "status": "review", "id": rid,
                        "title": plan.review.title, "badge": "확인 필요"})

    # --- 일정 ---
    for pe in plan.events:
        dup = _find_dup_event(db, pe.title, pe.date)
        if dup:
            results.append({"kind": "event", "status": "dup", "id": dup.id,
                            "title": pe.title, "badge": "중복 건너뜀"})
            continue
        eid = _new_id("evt")
        e = models.Event(
            id=eid, date=pe.date, time=pe.time, end_time=pe.end_time,
            title=pe.title, location=pe.location, category=pe.category,
            source=source_label, image_id=image_id, display_image=display_image,
            date_role=pe.date_role, action_type=pe.action_type, evidence=pe.evidence,
        )
        db.add(e)
        db.flush()
        created["events"].append(eid)
        results.append({"kind": "event", "status": "saved", "id": eid,
                        "title": pe.title, "badge": "캘린더 저장됨",
                        "item": serializers.event_to_dict(e)})

    # --- 보관함 ---
    for pl in plan.library:
        dup = _find_dup_library(db, pl.title, pl.category)
        if dup:
            results.append({"kind": "library", "status": "dup", "id": dup.id,
                            "title": pl.title, "badge": "중복 건너뜀"})
            continue
        lid = _new_id("lib")
        l = models.LibraryItem(
            id=lid, title=pl.title, category=pl.category, note=pl.note,
            image_id=image_id, display_image=display_image,
            place_name=pl.place_name, area=pl.area, source=source_label,
            missed=pl.missed, brand=pl.brand, expiry=pl.expiry, geo_type=pl.geo_type,
            missed_date=pl.missed_date, date_role=pl.date_role,
        )
        # 좌표화(T7): specific/area 좌표, brand geoType, geo_enabled 자동 설정
        _attach_location(l)
        db.add(l)
        db.flush()
        created["library"].append(lid)
        if pl.missed:
            badge = "지난 마감"
        elif pl.is_coupon:
            badge = "보관함 쿠폰"
        else:
            badge = "보관함 저장됨"
        results.append({"kind": "library", "status": "saved", "id": lid,
                        "title": pl.title, "badge": badge,
                        "item": serializers.library_to_dict(l)})

    # --- 활동 기록(되돌리기 연쇄용) ---
    recent_id = None
    if created["events"] or created["library"] or created["review"]:
        recent_id = _new_id("rec")
        summary = _summarize(results)
        rec = models.RecentActivity(
            id=recent_id, kind="analyze", summary=summary,
            payload=json.dumps(created, ensure_ascii=False),
            display_image=display_image,
        )
        db.add(rec)

    db.commit()

    return {
        "decision": plan.decision,
        "results": results,
        "created": created,
        "recent_id": recent_id,
    }


def _delete_image_file(image_id: str | None) -> None:
    if not image_id:
        return
    from .images import image_path
    p = image_path(image_id)
    if p is not None:
        try:
            p.unlink()
        except OSError:
            pass


def _image_referenced(db: Session, image_id: str, exclude_event=None, exclude_lib=None, exclude_rev=None) -> bool:
    """다른 항목이 같은 image_id 를 쓰는지(공유 이미지 삭제 방지)."""
    if not image_id:
        return False
    eq = db.query(models.Event).filter(models.Event.image_id == image_id)
    lq = db.query(models.LibraryItem).filter(models.LibraryItem.image_id == image_id)
    rq = db.query(models.ReviewItem).filter(models.ReviewItem.image_id == image_id)
    if exclude_event:
        eq = eq.filter(models.Event.id != exclude_event)
    if exclude_lib:
        lq = lq.filter(models.LibraryItem.id != exclude_lib)
    if exclude_rev:
        rq = rq.filter(models.ReviewItem.id != exclude_rev)
    return bool(eq.first() or lq.first() or rq.first())


def undo_recent(db: Session, recent_id: str) -> dict:
    """활동 기록을 되돌린다: payload 의 event/library/review 를 모두 삭제.

    반환: {"undone": bool, "deleted": {events, library, review}}
    """
    rec = db.get(models.RecentActivity, recent_id)
    if rec is None or rec.undone:
        return {"undone": False, "deleted": {"events": [], "library": [], "review": []}}

    try:
        created = json.loads(rec.payload) if rec.payload else {}
    except (ValueError, TypeError):
        created = {}

    deleted = {"events": [], "library": [], "review": []}
    for eid in created.get("events", []):
        e = db.get(models.Event, eid)
        if e:
            img = e.image_id
            db.delete(e)
            if img and not _image_referenced(db, img, exclude_event=eid):
                _delete_image_file(img)
            deleted["events"].append(eid)
    for lid in created.get("library", []):
        l = db.get(models.LibraryItem, lid)
        if l:
            img = l.image_id
            db.delete(l)
            if img and not _image_referenced(db, img, exclude_lib=lid):
                _delete_image_file(img)
            deleted["library"].append(lid)
    for rid in created.get("review", []):
        r = db.get(models.ReviewItem, rid)
        if r:
            db.delete(r)
            deleted["review"].append(rid)

    rec.undone = True
    db.commit()
    return {"undone": True, "deleted": deleted}


def delete_event(db: Session, event_id: str) -> bool:
    e = db.get(models.Event, event_id)
    if e is None:
        return False
    img = e.image_id
    db.delete(e)
    if img and not _image_referenced(db, img, exclude_event=event_id):
        _delete_image_file(img)
    db.commit()
    return True


def delete_library(db: Session, lib_id: str) -> bool:
    l = db.get(models.LibraryItem, lib_id)
    if l is None:
        return False
    img = l.image_id
    db.delete(l)
    if img and not _image_referenced(db, img, exclude_lib=lib_id):
        _delete_image_file(img)
    db.commit()
    return True


def update_library(db: Session, lib_id: str, changes: dict) -> models.LibraryItem | None:
    """분류·제목·메모 수정, geo_enabled 토글, used(쿠폰 사용) 반영."""
    l = db.get(models.LibraryItem, lib_id)
    if l is None:
        return None
    if "title" in changes and changes["title"] is not None:
        l.title = changes["title"]
    if "category" in changes and changes["category"] is not None:
        l.category = changes["category"]
    if "note" in changes:
        l.note = changes["note"]
    if "geo_enabled" in changes and changes["geo_enabled"] is not None:
        l.geo_enabled = bool(changes["geo_enabled"])
    if "used" in changes and changes["used"] is not None:
        l.used = bool(changes["used"])
    db.commit()
    return l


def set_library_location(db: Session, lib_id: str, lat: float, lng: float) -> models.LibraryItem | None:
    """사용자가 '현재 위치를 이 항목 위치로' 명시 지정. 좌표를 서버에 저장하는 유일한 경로.
    (지오펜스 판단은 브라우저에서 하며, 이 좌표는 사용자가 명시적으로 이 항목에 붙인 것.)"""
    l = db.get(models.LibraryItem, lib_id)
    if l is None:
        return None
    l.lat = float(lat)
    l.lng = float(lng)
    if l.geo_type is None:
        l.geo_type = "specific"
    if l.radius is None:
        l.radius = 150
    l.geo_enabled = True
    db.commit()
    return l


def resolve_review(db: Session, review_id: str, decision: str, category: str | None,
                   now, confidence_action: float, confidence_memory: float) -> dict:
    """확인 필요 항목 처리. extracted(정규화 JSON) 로 재-LLM 없이 저장.

    decision: schedule | memory | delete
    반환: {"ok": bool, "created": {...}, "recent_id": ...}
    """
    r = db.get(models.ReviewItem, review_id)
    if r is None:
        return {"ok": False, "created": None, "recent_id": None}

    image_id = r.image_id
    display_image = r.display_image

    if decision == "delete":
        db.delete(r)
        if image_id and not _image_referenced(db, image_id, exclude_rev=review_id):
            _delete_image_file(image_id)
        db.commit()
        return {"ok": True, "created": {"events": [], "library": [], "review": []}, "recent_id": None}

    try:
        extracted = json.loads(r.extracted) if r.extracted else {}
    except (ValueError, TypeError):
        extracted = {}

    # 사용자가 category 를 지정하면 반영
    if category:
        extracted["category"] = category

    from . import routing
    if decision == "schedule":
        # ACTION 으로 강제 라우팅(신뢰도 무시)
        extracted = dict(extracted)
        extracted["type"] = "ACTION"
        extracted["confidence"] = max(float(extracted.get("confidence") or 0), confidence_action)
        plan = routing.plan_routing(extracted, now, confidence_action, confidence_memory)
        # 유효 항목이 없으면(근거 없는 경우) 최소 하나의 메모리로 폴백하지 않고 그대로 진행
    elif decision == "memory":
        extracted = dict(extracted)
        extracted["type"] = "MEMORY"
        extracted["confidence"] = max(float(extracted.get("confidence") or 0), confidence_memory)
        plan = routing.plan_routing(extracted, now, confidence_action, confidence_memory)
    else:
        return {"ok": False, "created": None, "recent_id": None}

    outcome = apply_plan(
        db, plan, image_id=image_id, display_image=display_image,
        extracted=extracted, source_label="Snaptok AI(사용자 확인)",
    )
    # 원본 review 삭제
    db.delete(r)
    db.commit()

    return {"ok": True, "created": outcome["created"], "recent_id": outcome["recent_id"],
            "results": outcome["results"]}


def _summarize(results: list[dict]) -> str:
    ev = sum(1 for r in results if r["kind"] == "event" and r["status"] == "saved")
    lib = sum(1 for r in results if r["kind"] == "library" and r["status"] == "saved")
    rev = sum(1 for r in results if r["kind"] == "review")
    dup = sum(1 for r in results if r["status"] == "dup")
    parts = []
    if ev:
        parts.append(f"캘린더 {ev}건")
    if lib:
        parts.append(f"보관함 {lib}건")
    if rev:
        parts.append(f"확인 필요 {rev}건")
    if dup:
        parts.append(f"중복 {dup}건")
    return " · ".join(parts) or "처리 결과 없음"
