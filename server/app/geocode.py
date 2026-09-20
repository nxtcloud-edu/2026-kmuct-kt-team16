"""장소 좌표화(위치 저장). 명세 4.4.

보관함 항목이 저장될 때 서버가 좌표를 붙인다.
- brand: 좌표 없이 geo_type=brand, 매장 좌표는 시드(brand_stores) 또는 웹이 현재위치 기준으로 찾음(5.4).
- specific: place.name(+area) 로 검색 -> lat/lng, 반경 150m.
- area: 가게명 없이 동네만 -> 동네 중심 좌표, 반경 700m.
- 카카오 키 없거나 실패 -> places_seed.json 으로 대체. 그래도 없으면 좌표 없이 geo_enabled=false.
- 좌표 붙은 항목 중 카테고리가 맛집/여행지/전시회/패션/콘서트/쿠폰이면 geo_enabled=true.
- 해외 장소(국내 검색 결과 없음)는 좌표 없이 둔다.

카카오 REST 검색(T14, P1)은 kakao_search() 훅으로 분리. 지금은 시드 대체만 동작.
"""
from __future__ import annotations

import json

from .config import PLACES_SEED_PATH, settings

RADIUS_SPECIFIC = 150
RADIUS_AREA = 700

# 좌표가 붙으면 기본으로 지오펜스를 켜는 카테고리
GEO_CATEGORIES = {"맛집", "여행지", "전시회", "패션", "콘서트", "쿠폰"}

# 해외로 간주할 지역 키워드(국내 검색 결과가 없을 때만 판단 보조)
_OVERSEAS_HINTS = ("교토", "도쿄", "오사카", "kyoto", "tokyo", "osaka", "paris", "파리", "뉴욕", "new york")


def _load_seed() -> dict:
    try:
        return json.loads(PLACES_SEED_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"places": [], "brand_stores": {}}


def _seed_lookup(name: str | None, area: str | None, want_kind: str | None = None) -> dict | None:
    """places_seed.json 에서 이름/지역으로 매칭. want_kind 로 specific/area 제한 가능."""
    seed = _load_seed()
    hay = " ".join(x for x in (name, area) if x).strip().lower()
    if not hay:
        return None
    best = None
    for p in seed.get("places", []):
        if want_kind and p.get("kind") != want_kind:
            continue
        for kw in p.get("keywords", []):
            if kw.lower() in hay or hay in kw.lower():
                # 더 구체적인(specific) 매칭 우선
                if best is None or (p.get("kind") == "specific" and best.get("kind") != "specific"):
                    best = p
    return best


def _brand_stores(brand: str) -> list[dict]:
    seed = _load_seed()
    return seed.get("brand_stores", {}).get(brand, [])


def kakao_search(query: str) -> dict | None:
    """카카오 키워드 검색(T14, P1 에서 구현). 좌표 dict 또는 None.

    반환 예: {"lat": 37.5, "lng": 127.0, "name": "...", "single": True}
    지금은 키가 없거나 미구현이므로 None(시드 대체 경로로).
    """
    if not settings.kakao_rest_api_key:
        return None
    # T14 에서 실제 카카오 REST 호출 구현. 미구현 상태에서는 None.
    return None


def _is_overseas(name: str | None, area: str | None) -> bool:
    hay = " ".join(x for x in (name, area) if x).lower()
    return any(h in hay for h in _OVERSEAS_HINTS)


def resolve_coordinates(
    geo_type: str | None,
    place_name: str | None,
    area: str | None,
    brand: str | None,
    category: str | None,
) -> dict:
    """좌표화 결과를 dict 로 반환(순수 함수, 테스트 용이).

    반환: {geo_type, lat, lng, radius, branches(list), geo_enabled}
    """
    result = {
        "geo_type": geo_type,
        "lat": None,
        "lng": None,
        "radius": None,
        "branches": [],
        "geo_enabled": False,
    }

    # 1) 브랜드 쿠폰
    if brand:
        result["geo_type"] = "brand"
        result["branches"] = _brand_stores(brand)
        # 브랜드는 좌표 없이도 감시 대상(매장은 웹이 현재위치 기준으로 찾음)
        result["geo_enabled"] = category in GEO_CATEGORIES or True  # 쿠폰 brand 는 기본 on
        return result

    # 2) 해외 장소 -> 좌표 없이
    if _is_overseas(place_name, area):
        result["geo_enabled"] = False
        return result

    # 3) specific: 가게 이름이 있으면 검색(카카오 -> 시드)
    if place_name:
        hit = kakao_search(f"{place_name} {area or ''}".strip())
        if hit is None:
            hit = _seed_lookup(place_name, area, want_kind="specific") or _seed_lookup(place_name, area)
        if hit:
            result["geo_type"] = "specific"
            result["lat"] = hit["lat"]
            result["lng"] = hit["lng"]
            result["radius"] = RADIUS_SPECIFIC
            result["geo_enabled"] = category in GEO_CATEGORIES
            return result

    # 4) area: 동네만 있으면 동네 중심
    if area:
        hit = kakao_search(area)
        if hit is None:
            hit = _seed_lookup(None, area, want_kind="area") or _seed_lookup(None, area)
        if hit:
            result["geo_type"] = "area"
            result["lat"] = hit["lat"]
            result["lng"] = hit["lng"]
            result["radius"] = RADIUS_AREA
            result["geo_enabled"] = category in GEO_CATEGORIES
            return result

    # 5) 못 찾음 -> 좌표 없이, geo 꺼짐
    result["geo_enabled"] = False
    return result


def attach_location(item) -> None:
    """LibraryItem 에 좌표/geo 필드를 채운다(store._attach_location 에서 호출)."""
    res = resolve_coordinates(
        geo_type=item.geo_type,
        place_name=item.place_name,
        area=item.area,
        brand=item.brand,
        category=item.category,
    )
    item.geo_type = res["geo_type"]
    item.lat = res["lat"]
    item.lng = res["lng"]
    item.radius = res["radius"]
    if res["branches"]:
        item.branches = json.dumps(res["branches"], ensure_ascii=False)
    item.geo_enabled = res["geo_enabled"]
