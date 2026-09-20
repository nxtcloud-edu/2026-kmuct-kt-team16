"""T7: 장소 좌표화 (시드 대체 경로) 테스트."""
from app import geocode


def test_brand_no_coords_but_branches_and_enabled():
    r = geocode.resolve_coordinates(
        geo_type=None, place_name=None, area=None, brand="스타벅스", category="쿠폰"
    )
    assert r["geo_type"] == "brand"
    assert r["lat"] is None and r["lng"] is None
    assert len(r["branches"]) == 3  # 시드 매장 3곳
    assert r["geo_enabled"] is True


def test_specific_from_seed():
    r = geocode.resolve_coordinates(
        geo_type=None, place_name="연남동 파스타집", area="연남동", brand=None, category="맛집"
    )
    assert r["geo_type"] == "specific"
    assert r["lat"] == 37.5663 and r["lng"] == 126.9254
    assert r["radius"] == 150
    assert r["geo_enabled"] is True


def test_area_center_from_seed():
    # 가게 이름 없이 동네만 -> area 중심, 반경 700
    r = geocode.resolve_coordinates(
        geo_type=None, place_name=None, area="성수", brand=None, category="전시회"
    )
    assert r["geo_type"] == "area"
    assert r["radius"] == 700
    assert r["geo_enabled"] is True


def test_overseas_no_coords():
    r = geocode.resolve_coordinates(
        geo_type=None, place_name=None, area="교토", brand=None, category="여행지"
    )
    assert r["lat"] is None and r["lng"] is None
    assert r["geo_enabled"] is False


def test_not_found_no_coords():
    r = geocode.resolve_coordinates(
        geo_type=None, place_name="세상에없는가게이름xyz", area=None, brand=None, category="맛집"
    )
    assert r["lat"] is None
    assert r["geo_enabled"] is False


def test_non_geo_category_not_enabled_even_with_coords():
    # 공부 카테고리는 좌표가 붙어도 자동 geo_enabled 대상 아님
    r = geocode.resolve_coordinates(
        geo_type=None, place_name="연남동 파스타집", area="연남동", brand=None, category="공부"
    )
    assert r["geo_type"] == "specific"
    assert r["lat"] == 37.5663
    assert r["geo_enabled"] is False
