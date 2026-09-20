"""분석 결과 -> 저장 계획(plan) 순수 함수. (DB 접근 없음, 테스트 용이)

명세 4.3 라우팅/저장 규칙을 구현한다.
plan 은 store.py 가 실제 DB 에 반영한다.

용어:
- 유효 항목(valid item): date 가 파싱되고, evidence 속 날짜 숫자가 visible_text 에 존재.
- ACTION + confidence>=CONFIDENCE_ACTION + 유효항목 있음 -> 자동 저장(일정/보관함).
- MEMORY + confidence>=CONFIDENCE_MEMORY -> 보관함.
- 그 외 -> 확인 필요(review). 추출 결과 전체 보관.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time

# action_type -> 사람이 읽는 "행동" 라벨 (제목 "{title} · {행동}" 에 사용)
ACTION_LABEL = {
    "apply": "신청",
    "submit": "제출",
    "use": "사용",
    "book": "예약",
    "attend": "참석",
    "pay": "결제",
}

_NUM_RE = re.compile(r"\d+")


def _date_numbers(s: str) -> list[str]:
    """문자열에서 숫자 토큰 추출."""
    return _NUM_RE.findall(s or "")


def evidence_supported(item: dict, visible_text: str) -> bool:
    """근거 검사: evidence 속 날짜 숫자(월/일)가 visible_text 에 존재하는지.

    date(YYYY-MM-DD)의 월·일 숫자 중 하나라도 evidence 와 visible_text 양쪽에서
    확인되면 근거 있음으로 본다. evidence 가 비어 있으면(모델이 근거를 안 준 경우)
    date 의 월/일이 visible_text 에 있으면 통과.
    """
    d = item.get("date")
    if not d:
        return False
    try:
        y, m, dd = (int(x) for x in d.split("-"))
    except (ValueError, AttributeError):
        return False

    vis = visible_text or ""
    vis_nums = set(_date_numbers(vis))

    # 월/일을 여러 표기로 후보화 (예: 9, 09, 25)
    cand = {str(m), f"{m:02d}", str(dd), f"{dd:02d}"}

    # visible_text 에 월 또는 일 숫자가 있어야 근거로 인정
    day_in_vis = str(dd) in vis_nums or f"{dd:02d}" in vis
    month_in_vis = str(m) in vis_nums or f"{m:02d}" in vis
    if not (day_in_vis and month_in_vis):
        # 최소한 '일' 숫자라도 visible_text 에 있어야 함
        if not day_in_vis:
            return False

    ev = item.get("evidence") or ""
    if ev:
        ev_nums = set(_date_numbers(ev))
        # evidence 에 date 의 일 숫자가 있어야 함
        if not (str(dd) in ev_nums or f"{dd:02d}" in ev):
            return False
    return True


def _parse_dt(d: str, t: str | None) -> datetime | None:
    try:
        y, mo, da = (int(x) for x in d.split("-"))
    except (ValueError, AttributeError):
        return None
    hh, mm = 0, 0
    if t:
        mt = re.match(r"^(\d{1,2}):(\d{2})$", t)
        if mt:
            hh, mm = int(mt.group(1)), int(mt.group(2))
    try:
        return datetime(y, mo, da, hh, mm)
    except ValueError:
        return None


def is_past(item: dict, now: datetime) -> bool:
    """기준 시각이 지났는지. date_role/ kind 에 따라 기준 시각 결정.
    - expiry: 만료일 23:59
    - event: end_time 있으면 그 시각, 없으면 해당일 23:59(하루 종일로 관대하게)
    - deadline/task: time 있으면 그 시각, 없으면 해당일 23:59
    """
    d = item.get("date")
    if not d:
        return False
    role = item.get("date_role")
    if role == "expiry":
        ref = _parse_dt(d, "23:59")
    elif role == "event":
        end_t = item.get("end_time") or item.get("time")
        ref = _parse_dt(d, end_t) if end_t else _parse_dt(d, "23:59")
    else:  # deadline / 기타
        t = item.get("time")
        ref = _parse_dt(d, t) if t else _parse_dt(d, "23:59")
    if ref is None:
        return False
    return ref < now


def title_with_action(title: str, action_type: str | None) -> str:
    label = ACTION_LABEL.get(action_type or "")
    base = (title or "").strip()
    if label and not base.endswith("· " + label) and label not in base:
        return f"{base} · {label}"
    return base


@dataclass
class PlannedEvent:
    title: str
    date: str
    time: str | None
    end_time: str | None
    location: str | None
    category: str | None
    date_role: str | None
    action_type: str | None
    evidence: str | None


@dataclass
class PlannedLibrary:
    title: str
    category: str | None
    note: str | None
    place_name: str | None
    area: str | None
    brand: str | None
    expiry: str | None
    geo_type: str | None
    missed: bool = False
    is_coupon: bool = False
    missed_date: str | None = None
    date_role: str | None = None


@dataclass
class PlannedReview:
    title: str
    reason: str
    category: str | None


@dataclass
class RoutingPlan:
    decision: str                      # "action" | "memory" | "review"
    events: list[PlannedEvent] = field(default_factory=list)
    library: list[PlannedLibrary] = field(default_factory=list)
    review: PlannedReview | None = None
    valid_items: list[dict] = field(default_factory=list)


def plan_routing(
    data: dict,
    now: datetime,
    confidence_action: float,
    confidence_memory: float,
) -> RoutingPlan:
    """정규화된 분석 결과(data)로 저장 계획 수립."""
    typ = data.get("type")
    conf = float(data.get("confidence") or 0.0)
    visible = data.get("visible_text") or ""
    items = data.get("items") or []
    title = data.get("title") or "분석 결과"
    category = data.get("category")
    place = data.get("place") or {}
    place_name = place.get("name")
    area = place.get("area")
    brand = data.get("brand")
    note = data.get("note") or ""

    # 유효 항목 필터
    valid = [it for it in items if evidence_supported(it, visible)]

    # ACTION 라우팅
    if typ == "ACTION" and conf >= confidence_action and valid:
        plan = RoutingPlan(decision="action", valid_items=valid)
        for it in valid:
            past = is_past(it, now)
            is_use = it.get("action_type") == "use"
            item_title = title_with_action(it.get("title") or title, it.get("action_type"))

            if past:
                # 지난 기준시각 -> 보관함 missed (원래 날짜/역할 보존)
                plan.library.append(PlannedLibrary(
                    title=item_title, category=category, note=note,
                    place_name=place_name, area=area, brand=brand,
                    expiry=it.get("date") if it.get("date_role") == "expiry" else None,
                    geo_type=None, missed=True,
                    is_coupon=is_use,
                    missed_date=it.get("date"),
                    date_role=it.get("date_role"),
                ))
                continue

            # 일정 저장 (쿠폰도 만료 알림용 일정 생성)
            plan.events.append(PlannedEvent(
                title=item_title, date=it.get("date"), time=it.get("time"),
                end_time=it.get("end_time"), location=it.get("location") or place_name,
                category=category, date_role=it.get("date_role"),
                action_type=it.get("action_type"), evidence=it.get("evidence"),
            ))
            # 쿠폰(use) -> 보관함 쿠폰 항목도 생성
            if is_use:
                plan.library.append(PlannedLibrary(
                    title=title, category="쿠폰", note=note,
                    place_name=place_name, area=area, brand=brand,
                    expiry=it.get("date") if it.get("date_role") == "expiry" else it.get("date"),
                    geo_type="brand" if brand else None,
                    is_coupon=True,
                ))
        return plan

    # MEMORY 라우팅
    if typ == "MEMORY" and conf >= confidence_memory:
        plan = RoutingPlan(decision="memory")
        plan.library.append(PlannedLibrary(
            title=title, category=category or "기타", note=note,
            place_name=place_name, area=area, brand=brand,
            expiry=None, geo_type=None,
        ))
        return plan

    # 그 외 -> 확인 필요
    reason = "확신도 낮음" if typ in ("ACTION", "MEMORY") else "날짜 역할 불분명"
    if typ == "ACTION" and not valid:
        reason = "근거 있는 날짜 없음"
    return RoutingPlan(
        decision="review",
        review=PlannedReview(title=title, reason=reason, category=category),
    )
