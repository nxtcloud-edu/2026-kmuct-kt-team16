"""LLM 원시 응답(JSON 텍스트)을 정규화된 dict 로 파싱·검증한다.

파싱 실패/형식 오류 시 UNCERTAIN 결과로 폴백한다.
근거(evidence) 속 날짜가 visible_text 에 존재하는지는 라우팅(T6)에서 검사하므로
여기서는 형식 정규화만 담당한다.
"""
from __future__ import annotations

import json
import re
from typing import Any

from .prompt import CATEGORIES

VALID_TYPES = {"ACTION", "MEMORY", "UNCERTAIN"}
VALID_KINDS = {"task", "event"}
VALID_ACTION_TYPES = {"apply", "submit", "use", "book", "attend", "pay"}
VALID_DATE_ROLES = {"deadline", "event", "expiry", "ticket_open"}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")


def uncertain(title: str = "분석 확인 필요", note: str = "", visible_text: str = "") -> dict:
    return {
        "type": "UNCERTAIN",
        "confidence": 0.0,
        "title": title,
        "category": None,
        "visible_text": visible_text,
        "items": [],
        "place": {"name": None, "area": None},
        "brand": None,
        "note": note,
    }


def _strip_code_fence(text: str) -> str:
    """```json ... ``` 같은 코드펜스 제거하고 첫 JSON 오브젝트만 취한다."""
    t = text.strip()
    if t.startswith("```"):
        # 첫 줄(```json) 과 마지막 ``` 제거
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    # 첫 '{' 부터 마지막 '}' 까지
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start : end + 1]
    return t


def try_load(text: str) -> dict | None:
    """텍스트에서 JSON 오브젝트를 로드. 실패 시 None."""
    if not text:
        return None
    candidate = _strip_code_fence(text)
    try:
        obj = json.loads(candidate)
        return obj if isinstance(obj, dict) else None
    except (ValueError, TypeError):
        return None


def _coerce_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _coerce_confidence(v: Any) -> float:
    try:
        f = float(v)
    except (ValueError, TypeError):
        return 0.0
    return max(0.0, min(1.0, f))


def _norm_item(raw: Any) -> dict | None:
    if not isinstance(raw, dict):
        return None
    date = _coerce_str(raw.get("date"))
    # 날짜가 YYYY-MM-DD 형식이 아니면 그 item 은 무효(라우팅에서 유효항목 검사)
    if not date or not _DATE_RE.match(date):
        return None
    kind = _coerce_str(raw.get("kind"))
    if kind not in VALID_KINDS:
        # 기본: date_role 로 유추, 그래도 없으면 event
        kind = "task" if _coerce_str(raw.get("date_role")) in ("deadline", "expiry") else "event"
    action_type = _coerce_str(raw.get("action_type"))
    if action_type not in VALID_ACTION_TYPES:
        action_type = None
    date_role = _coerce_str(raw.get("date_role"))
    if date_role not in VALID_DATE_ROLES:
        date_role = None
    time = _coerce_str(raw.get("time"))
    if time and not _TIME_RE.match(time):
        time = None
    end_time = _coerce_str(raw.get("end_time"))
    if end_time and not _TIME_RE.match(end_time):
        end_time = None
    return {
        "kind": kind,
        "action_type": action_type,
        "title": _coerce_str(raw.get("title")) or "",
        "date_role": date_role,
        "date": date,
        "time": time,
        "end_time": end_time,
        "location": _coerce_str(raw.get("location")) or "",
        "evidence": _coerce_str(raw.get("evidence")) or "",
    }


def normalize(obj: dict | None) -> dict:
    """원시 dict 를 스키마에 맞게 정규화. 실패 요소는 안전한 기본값으로."""
    if not isinstance(obj, dict):
        return uncertain(note="응답 형식 오류")

    typ = _coerce_str(obj.get("type"))
    typ = typ.upper() if typ else None
    if typ not in VALID_TYPES:
        typ = "UNCERTAIN"

    category = _coerce_str(obj.get("category"))
    if category is not None and category not in CATEGORIES:
        # 알 수 없는 카테고리는 기타로
        category = "기타"

    items_raw = obj.get("items")
    items: list[dict] = []
    if isinstance(items_raw, list):
        for it in items_raw:
            ni = _norm_item(it)
            if ni:
                items.append(ni)

    place_raw = obj.get("place") if isinstance(obj.get("place"), dict) else {}
    place = {
        "name": _coerce_str(place_raw.get("name")),
        "area": _coerce_str(place_raw.get("area")),
    }

    return {
        "type": typ,
        "confidence": _coerce_confidence(obj.get("confidence")),
        "title": _coerce_str(obj.get("title")) or "분석 결과",
        "category": category,
        "visible_text": _coerce_str(obj.get("visible_text")) or "",
        "items": items,
        "place": place,
        "brand": _coerce_str(obj.get("brand")),
        "note": _coerce_str(obj.get("note")) or "",
    }


def parse_response(text: str) -> tuple[dict, bool]:
    """LLM 텍스트 응답을 파싱. (정규화 결과, 파싱성공여부) 반환.
    파싱 실패면 (UNCERTAIN, False)."""
    obj = try_load(text)
    if obj is None:
        return uncertain(note="JSON 파싱 실패"), False
    return normalize(obj), True
