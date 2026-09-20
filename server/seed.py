"""데모 시드 데이터를 서버 DB 에 넣는다. (모든 시드는 seed=true)

사용:
  server\\.venv\\Scripts\\python.exe seed.py           # 시드 추가(기존 seed 는 먼저 삭제)
  server\\.venv\\Scripts\\python.exe seed.py --reset    # 전체 DB 초기화 후 시드

설정의 "시연 데이터 초기화"에서 이 스크립트에 해당하는 API(추후)로 다시 채운다.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta

from app.db import SessionLocal, init_db, engine, Base
from app import models
from app import seed_data


def _ts(offset_ms: int) -> datetime:
    """NOW 기준 offset(ms) 을 UTC datetime 으로."""
    return datetime.now(timezone.utc) + timedelta(milliseconds=offset_ms)


def clear_seed(db) -> None:
    """seed=true 항목만 삭제."""
    db.query(models.Event).filter(models.Event.seed == True).delete()  # noqa: E712
    db.query(models.LibraryItem).filter(models.LibraryItem.seed == True).delete()  # noqa: E712
    db.query(models.ReviewItem).filter(models.ReviewItem.seed == True).delete()  # noqa: E712
    # recent 는 데모용 r-seed-* 만 삭제
    db.query(models.RecentActivity).filter(models.RecentActivity.id.like("r-seed-%")).delete()
    db.commit()


def seed(db) -> dict:
    counts = {"events": 0, "library": 0, "recent": 0}
    for e in seed_data.EVENTS:
        db.add(models.Event(
            id=e["id"], date=e["date"], time=e.get("time"), end_time=e.get("end_time"),
            title=e["title"], location=e.get("location"), category=e.get("category"),
            source=e.get("source"), display_image=e.get("display_image"),
            date_role=e.get("date_role"), action_type=e.get("action_type"),
            evidence=e.get("evidence"), seed=True,
        ))
        counts["events"] += 1

    for l in seed_data.LIBRARY:
        db.add(models.LibraryItem(
            id=l["id"], title=l["title"], category=l.get("category"), note=l.get("note"),
            thumb=l.get("thumb"), display_image=l.get("display_image"),
            place_name=l.get("place_name"), area=l.get("area"), source=l.get("source"),
            geo_type=l.get("geo_type"), lat=l.get("lat"), lng=l.get("lng"),
            radius=l.get("radius"), brand=l.get("brand"),
            branches=json.dumps(l["branches"], ensure_ascii=False) if l.get("branches") else None,
            expiry=l.get("expiry"), geo_enabled=bool(l.get("geo_enabled", False)),
            created_at=_ts(l.get("created_offset", 0)), seed=True,
        ))
        counts["library"] += 1

    for r in seed_data.RECENT:
        db.add(models.RecentActivity(
            id=r["id"], kind=r["kind"], summary=r["summary"], detail=r.get("detail"),
            display_image=r.get("display_image"), kind_ref=r.get("kind_ref"),
            created_at=_ts(r.get("created_offset", 0)),
        ))
        counts["recent"] += 1

    db.commit()
    return counts


def main() -> None:
    reset = "--reset" in sys.argv
    if reset:
        Base.metadata.drop_all(bind=engine)
    init_db()
    db = SessionLocal()
    try:
        if not reset:
            clear_seed(db)
        counts = seed(db)
        print("SEEDED:", counts)
    finally:
        db.close()


if __name__ == "__main__":
    main()
