"""데이터 모델. 데이터의 원본은 서버 DB다.

명세 참고:
- events: 일정 (자동 등록된 ACTION 항목의 유효 항목들)
- library: 보관함 (MEMORY / 쿠폰 / missed ACTION). 지오펜스 대상 필드 포함.
- review: 확인 필요 큐. 추출 결과 전체(extracted)를 보관해 재분석 없이 처리.
- recent: 활동 기록 + 되돌리기 연쇄(관련 event/library id 를 payload 에 보관)
- processed_request: request_id 멱등 처리(같은 요청이면 이전 결과 재사용)

지오펜스 실행 상태(_status/_dist/_dwellStart)는 DB 에 저장하지 않는다(브라우저 메모리 전용).
사용자 위치 좌표도 서버에 저장하지 않는다.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Event(Base):
    """캘린더 일정."""
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(String, nullable=False)          # YYYY-MM-DD
    time: Mapped[str | None] = mapped_column(String, nullable=True)     # HH:MM 또는 표시문구
    end_time: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    image_id: Mapped[str | None] = mapped_column(String, nullable=True)  # 업로드 이미지 -> /api/images/{id}
    # 시드/데모 표시용 이미지 문자열(SVG data URI 또는 상대경로). 업로드분은 None(image_id 사용).
    display_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 날짜 역할/근거 (약한 날짜 처리 개선)
    date_role: Mapped[str | None] = mapped_column(String, nullable=True)  # deadline|event|expiry|ticket_open
    action_type: Mapped[str | None] = mapped_column(String, nullable=True)  # apply|submit|use|book|attend|pay
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 구글 캘린더 동기화(P1)
    gcal_event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    sync_status: Mapped[str | None] = mapped_column(String, nullable=True)  # synced|failed|None
    # 메타
    seed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class LibraryItem(Base):
    """보관함 항목(기억형/쿠폰/지난 마감 등)."""
    __tablename__ = "library"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)   # 맛집/여행지/쿠폰 ...
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_id: Mapped[str | None] = mapped_column(String, nullable=True)
    display_image: Mapped[str | None] = mapped_column(Text, nullable=True)  # 시드/데모 표시용
    thumb: Mapped[str | None] = mapped_column(String, nullable=True)         # 이모지 썸네일(데모)
    place_name: Mapped[str | None] = mapped_column(String, nullable=True)
    area: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    # 상태
    missed: Mapped[bool] = mapped_column(Boolean, default=False)          # 지난 마감으로 저장된 ACTION
    missed_date: Mapped[str | None] = mapped_column(String, nullable=True)  # 지난 마감/행사의 원래 날짜 YYYY-MM-DD
    date_role: Mapped[str | None] = mapped_column(String, nullable=True)    # deadline|event|expiry (표시용)
    used: Mapped[bool] = mapped_column(Boolean, default=False)            # 쿠폰 사용 완료
    # --- 지오펜스 / 위치 저장 ---
    geo_type: Mapped[str | None] = mapped_column(String, nullable=True)   # brand|specific|area
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    radius: Mapped[int | None] = mapped_column(Integer, nullable=True)    # m
    brand: Mapped[str | None] = mapped_column(String, nullable=True)      # 체인 브랜드명
    branches: Mapped[str | None] = mapped_column(Text, nullable=True)     # brand 매장 좌표 목록 JSON(시드용)
    expiry: Mapped[str | None] = mapped_column(String, nullable=True)     # 쿠폰 만료 YYYY-MM-DD
    geo_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    # 메타
    seed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class ReviewItem(Base):
    """확인 필요 큐. extracted 에 LLM 추출 원본 JSON 을 보관해 재호출 없이 처리."""
    __tablename__ = "review"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)     # UNCERTAIN 사유/분석실패 등
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    image_id: Mapped[str | None] = mapped_column(String, nullable=True)
    display_image: Mapped[str | None] = mapped_column(Text, nullable=True)  # 시드/데모 표시용
    extracted: Mapped[str | None] = mapped_column(Text, nullable=True)    # LLM 결과 JSON 문자열
    seed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class RecentActivity(Base):
    """활동 기록 + 되돌리기 연쇄 정보."""
    __tablename__ = "recent"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)   # analyze|resolve|manual ...
    summary: Mapped[str] = mapped_column(String, nullable=False)
    # 이 활동으로 생성된 항목들(되돌리기 시 연쇄 삭제 대상) JSON:
    #   {"events":[id...], "library":[id...], "review":[id...]}
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[str | None] = mapped_column(String, nullable=True)       # 부가 설명(데모)
    display_image: Mapped[str | None] = mapped_column(Text, nullable=True)  # 시드/데모 표시용
    kind_ref: Mapped[str | None] = mapped_column(String, nullable=True)     # 데모 refId(event/library)
    undone: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class ProcessedRequest(Base):
    """request_id 멱등. 같은 request_id 재요청 시 저장해 둔 결과(result JSON)를 반환."""
    __tablename__ = "processed_request"

    request_id: Mapped[str] = mapped_column(String, primary_key=True)
    result: Mapped[str] = mapped_column(Text, nullable=False)   # /api/analyze 응답 JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
