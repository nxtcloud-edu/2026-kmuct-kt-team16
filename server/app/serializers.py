"""모델 -> 웹 JSON 직렬화. 웹(app.js)이 기대하는 필드명에 맞춘다.

이미지 표시 규칙:
- 업로드 이미지: image_id 가 있으면 image = "/api/images/{image_id}"
- 시드/데모: display_image(SVG data URI 또는 상대경로)를 image 로 그대로 사용
"""
from __future__ import annotations

import json

from . import models


def _json_or_empty(raw: str | None):
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return []


def _image_url(image_id: str | None, display_image: str | None) -> str:
    if image_id:
        return f"/api/images/{image_id}"
    return display_image or ""


def event_to_dict(e: "models.Event") -> dict:
    return {
        "id": e.id,
        "date": e.date,
        "time": e.time,
        "end_time": e.end_time,
        "title": e.title,
        "location": e.location,
        "category": e.category,
        "source": e.source,
        "image": _image_url(e.image_id, e.display_image),
        "date_role": e.date_role,
        "action_type": e.action_type,
        "evidence": e.evidence,
        "sync_status": e.sync_status,
        "seed": e.seed,
    }


def library_to_dict(l: "models.LibraryItem") -> dict:
    d = {
        "id": l.id,
        "title": l.title,
        "category": l.category,
        "place": l.place_name or "",
        "area": l.area,
        "note": l.note,
        "thumb": l.thumb,
        "image": _image_url(l.image_id, l.display_image),
        "source": l.source,
        "missed": l.missed,
        "missed_date": l.missed_date,
        "date_role": l.date_role,
        "used": l.used,
        "geoType": l.geo_type,
        "lat": l.lat,
        "lng": l.lng,
        "radius": l.radius,
        "brand": l.brand,
        "branches": _json_or_empty(l.branches),
        "expiry": l.expiry,
        "geo_enabled": l.geo_enabled,
        "seed": l.seed,
    }
    return d


def review_to_dict(r: "models.ReviewItem") -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "reason": r.reason,
        "category": r.category,
        "image": _image_url(r.image_id, r.display_image),
        "seed": r.seed,
    }


def recent_to_dict(r: "models.RecentActivity") -> dict:
    return {
        "id": r.id,
        "kind": r.kind,
        "label": r.summary,
        "detail": r.detail,
        "image": r.display_image or "",
        "refId": r.kind_ref,
        "undone": r.undone,
        # ts 는 밀리초(웹 timeAgo 호환). created_at 은 UTC.
        "ts": int(r.created_at.timestamp() * 1000) if r.created_at else None,
    }


def geo_target_to_dict(l: "models.LibraryItem", branches: list | None = None) -> dict:
    """geoTargets: geo_enabled 인 library 항목. 웹 지오펜스 엔진이 쓰는 형태."""
    return {
        "id": l.id,
        "title": l.title,
        "category": l.category,
        "geoType": l.geo_type,
        "lat": l.lat,
        "lng": l.lng,
        "radius": l.radius,
        "brand": l.brand,
        "expiry": l.expiry,
        "used": l.used,
        "image": _image_url(l.image_id, l.display_image),
        "branches": branches if branches is not None else _json_or_empty(l.branches),
    }
