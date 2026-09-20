"""Snaptok FastAPI 진입점.

T3 범위: 앱 뼈대, DB 초기화, /app 정적 제공, /api/images/{id}, /api/health.
/api/state, /api/analyze 등 나머지 엔드포인트는 후속 작업(T4~)에서 추가한다.
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import date, datetime

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models, routing, serializers, store
from .config import WEB_DIR, settings
from .db import get_session, init_db
from .images import content_type_for, image_path, save_image_bytes
from .llm import get_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Snaptok Server", version="0.1.0", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "llm_mode": "live" if settings.llm_enabled else "mock",
        "calendar_sync": settings.calendar_sync,
        "demo_today": settings.demo_today or None,
    }


@app.get("/api/state")
def get_state(db: Session = Depends(get_session)):
    """초기 로드: events, library, review, recent, geoTargets.

    - events: 날짜 오름차순
    - library: 최신 저장 순(created_at desc)
    - review: 최신 순
    - recent: 최신 순(최대 60)
    - geoTargets: geo_enabled 이고 사용하지 않은(used=false) 지오펜스 감시 대상
    """
    events = db.query(models.Event).order_by(models.Event.date.asc()).all()
    library = (
        db.query(models.LibraryItem)
        .order_by(models.LibraryItem.created_at.desc())
        .all()
    )
    review = (
        db.query(models.ReviewItem)
        .order_by(models.ReviewItem.created_at.desc())
        .all()
    )
    recent = (
        db.query(models.RecentActivity)
        .filter(models.RecentActivity.undone == False)  # noqa: E712
        .order_by(models.RecentActivity.created_at.desc())
        .limit(60)
        .all()
    )
    geo_targets = [
        l for l in library
        if l.geo_enabled and not l.used and (l.geo_type == "brand" or (l.lat is not None and l.lng is not None))
    ]

    return {
        "events": [serializers.event_to_dict(e) for e in events],
        "library": [serializers.library_to_dict(l) for l in library],
        "review": [serializers.review_to_dict(r) for r in review],
        "recent": [serializers.recent_to_dict(r) for r in recent],
        "geoTargets": [serializers.geo_target_to_dict(l) for l in geo_targets],
        "config": {
            "demo_today": settings.demo_today or None,
            "default_timezone": settings.default_timezone,
            "calendar_sync": settings.calendar_sync,
        },
    }


def _resolve_today_now() -> tuple[str, datetime]:
    """오늘 날짜 문자열과 라우팅 기준 now(naive local) 반환.

    DEMO_TODAY 가 있으면 그 날짜를 '오늘'로 쓰고, now 는 그 날짜의 현재 시각(벽시계 시분)을 붙인다.
    (지난 날짜 판정이 그 날의 흐름을 반영하도록.)
    """
    wall = datetime.now()
    if settings.demo_today:
        try:
            y, m, d = (int(x) for x in settings.demo_today.split("-"))
            today = f"{y:04d}-{m:02d}-{d:02d}"
            now = datetime(y, m, d, wall.hour, wall.minute, wall.second)
            return today, now
        except (ValueError, AttributeError):
            pass
    return wall.date().isoformat(), wall


@app.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...),
    captured_at: str | None = Form(None),
    request_id: str | None = Form(None),
    db: Session = Depends(get_session),
):
    """이미지 분석 후 즉시 저장하고 결과 반환.

    - request_id 가 이미 처리된 값이면 이전 결과를 그대로 반환(멱등).
    - 분석 실패(LLM 호출 오류)면 '분석 실패' 항목으로 확인 필요에 저장.
    """
    # 멱등 처리
    if request_id:
        prev = db.get(models.ProcessedRequest, request_id)
        if prev:
            return json.loads(prev.result)

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty image")

    content_type = image.content_type or "image/jpeg"
    filename = image.filename or ""
    image_id = save_image_bytes(raw, content_type, filename)

    today, now = _resolve_today_now()
    provider = get_provider()

    try:
        analysis = provider.analyze(
            raw, content_type, captured_at, today, settings.default_timezone, hint=filename
        )
        data = analysis.data
        analysis_failed = False
    except Exception:  # noqa: BLE001  네트워크/HTTP 등 -> 분석 실패로 확인 필요에
        data = None
        analysis_failed = True

    if analysis_failed or data is None:
        # 분석 실패 -> 확인 필요
        plan = routing.RoutingPlan(
            decision="review",
            review=routing.PlannedReview(title="분석 실패", reason="분석 오류", category=None),
        )
        extracted = {"error": "analyze_failed"}
    else:
        plan = routing.plan_routing(
            data, now, settings.confidence_action, settings.confidence_memory
        )
        extracted = data

    outcome = store.apply_plan(
        db, plan, image_id=image_id, display_image=None, extracted=extracted,
    )

    # 요약 배너 문구
    summary = store._summarize(outcome["results"])

    result = {
        "request_id": request_id,
        "decision": outcome["decision"],
        "results": outcome["results"],
        "summary": summary,
        "recent_id": outcome["recent_id"],
        "image": f"/api/images/{image_id}",
        "llm_mode": analysis.mode if not analysis_failed and data is not None else "mock",
    }

    # 멱등 저장
    if request_id:
        db.add(models.ProcessedRequest(request_id=request_id, result=json.dumps(result, ensure_ascii=False)))
        db.commit()

    return result


@app.get("/api/images/{image_id}")
def get_image(image_id: str):
    p = image_path(image_id)
    if p is None:
        raise HTTPException(status_code=404, detail="image not found")
    return FileResponse(p, media_type=content_type_for(image_id))


# ---------------- 수정 / 되돌리기 / 확인필요 처리 ----------------

class LibraryPatch(BaseModel):
    title: str | None = None
    category: str | None = None
    note: str | None = None
    geo_enabled: bool | None = None
    used: bool | None = None


class LocationBody(BaseModel):
    lat: float
    lng: float


class ResolveBody(BaseModel):
    decision: str                    # schedule | memory | delete
    category: str | None = None


@app.patch("/api/library/{lib_id}")
def patch_library(lib_id: str, body: LibraryPatch, db: Session = Depends(get_session)):
    l = store.update_library(db, lib_id, body.model_dump(exclude_unset=True))
    if l is None:
        raise HTTPException(status_code=404, detail="library item not found")
    return serializers.library_to_dict(l)


@app.post("/api/library/{lib_id}/location")
def set_location(lib_id: str, body: LocationBody, db: Session = Depends(get_session)):
    """사용자가 '현재 위치를 이 항목 위치로' 명시 지정할 때만 호출."""
    l = store.set_library_location(db, lib_id, body.lat, body.lng)
    if l is None:
        raise HTTPException(status_code=404, detail="library item not found")
    return serializers.library_to_dict(l)


@app.delete("/api/library/{lib_id}")
def del_library(lib_id: str, db: Session = Depends(get_session)):
    if not store.delete_library(db, lib_id):
        raise HTTPException(status_code=404, detail="library item not found")
    return {"ok": True}


@app.delete("/api/events/{event_id}")
def del_event(event_id: str, db: Session = Depends(get_session)):
    if not store.delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="event not found")
    return {"ok": True}


@app.post("/api/review/{review_id}/resolve")
def resolve_review(review_id: str, body: ResolveBody, db: Session = Depends(get_session)):
    if body.decision not in ("schedule", "memory", "delete"):
        raise HTTPException(status_code=400, detail="invalid decision")
    _, now = _resolve_today_now()
    out = store.resolve_review(
        db, review_id, body.decision, body.category, now,
        settings.confidence_action, settings.confidence_memory,
    )
    if not out["ok"]:
        raise HTTPException(status_code=404, detail="review item not found")
    return out


@app.post("/api/recent/{recent_id}/undo")
def undo(recent_id: str, db: Session = Depends(get_session)):
    out = store.undo_recent(db, recent_id)
    if not out["undone"]:
        raise HTTPException(status_code=404, detail="recent activity not found or already undone")
    return out


# 루트 접속 시 /app 으로 안내
@app.get("/")
def root():
    return {"message": "Snaptok server. Web app is served at /app"}


# 정적 웹(Snaptok/) 을 /app 으로 제공. html=True 로 index.html 자동 서빙.
# API 라우트 뒤에 마운트해야 /api/* 가 가려지지 않는다.
if WEB_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(WEB_DIR), html=True), name="app")
