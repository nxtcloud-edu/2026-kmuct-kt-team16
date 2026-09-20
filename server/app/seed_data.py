"""데모 시드 데이터. Snaptok/app.js 의 시드와 동일하게 유지한다.

posterSVG 는 app.js 와 동일한 SVG data URI 를 생성해 화면이 그대로 보이게 한다.
쿼리스트링 인코딩(encodeURIComponent)도 JS 와 맞춘다.
"""
from __future__ import annotations

from urllib.parse import quote

# app.js 의 esc 와 동일: & < > " ' -> HTML 엔티티
_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def esc(s: str) -> str:
    s = "" if s is None else str(s)
    return "".join(_ESC.get(c, c) for c in s)


def poster_svg(emoji: str, title: str, sub: str = "", tint: str = "#EEE") -> str:
    """app.js posterSVG 와 동일한 data URI 생성."""
    t = esc(title)[:18]
    s = esc(sub or "")[:22]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="620">\n'
        f'    <rect width="480" height="620" fill="{tint}"/>\n'
        '    <rect x="0" y="0" width="480" height="46" fill="rgba(21,27,61,.08)"/>\n'
        '    <text x="20" y="30" font-family="Arial" font-size="18" fill="#151B3D" font-weight="bold">9:41</text>\n'
        f'    <text x="240" y="330" text-anchor="middle" font-size="120">{emoji}</text>\n'
        f'    <text x="240" y="420" text-anchor="middle" font-family="Arial" font-size="26" fill="#151B3D" font-weight="bold">{t}</text>\n'
        f'    <text x="240" y="452" text-anchor="middle" font-family="Arial" font-size="16" fill="#5b5468">{s}</text>\n'
        '  </svg>'
    )
    # JS encodeURIComponent 와 동일한 safe 문자 집합
    return "data:image/svg+xml;charset=utf-8," + quote(svg, safe="!~*'()")


# 시간 오프셋(밀리초) — app.js 의 NOW0 상대값과 동일한 순서를 유지하기 위한 것
H = 3600 * 1000
D = 86400 * 1000


# ---- 이벤트(캘린더 일정) 시드 ----
EVENTS = [
    dict(id="hackathon", date="2026-09-20", time="08:00–21:30", title="AI VIBE CODING 해커톤",
         location="AWS 역삼 센터필드", source="기본 일정", display_image="assets/hackathon.jpg"),
    dict(id="gym-pt", date="2026-09-22", time="19:00", title="헬스장 PT 예약 확인",
         location="월드짐 강남점", source="Snaptok AI",
         display_image=poster_svg("🏋️", "PT 예약 확인", "월드짐 강남점 · 19:00", "#E1F3E6")),
    dict(id="seminar-review", date="2026-09-24", time="시간 미정", title="전공 세미나 안내",
         location="장소 확인 필요", source="Snaptok AI(사용자 확인)",
         display_image=poster_svg("📢", "전공 세미나 안내", "날짜만 확인, 장소 미정", "#F6E4F4")),
    dict(id="ideathon-deadline", date="2026-09-27", time="18:00", title="AI 서비스 아이디어톤 신청 마감",
         location="온라인", source="Snaptok AI",
         display_image=poster_svg("🏆", "아이디어톤 신청마감", "9/27 18:00 · 온라인", "#E3ECFF")),
    dict(id="ideathon-final", date="2026-09-29", time="14:00", title="아이디어톤 본선 발표",
         location="온라인", source="Snaptok AI",
         display_image=poster_svg("🎤", "본선 발표", "9/29 14:00 · 온라인", "#FFE0E0")),
    dict(id="study-group", date="2026-09-21", time="20:00", title="알고리즘 스터디 모임",
         location="학교 도서관 401호", source="Snaptok AI",
         display_image=poster_svg("📚", "스터디 모임", "도서관 401호 · 20:00", "#E1F3E6")),
    dict(id="dentist", date="2026-09-23", time="15:30", title="치과 예약",
         location="서울역삼치과", source="Snaptok AI",
         display_image=poster_svg("🦷", "치과 예약", "서울역삼치과 · 15:30", "#DCEFFB")),
    dict(id="friend-bday", date="2026-09-25", time="19:00", title="재현이 생일 저녁 약속",
         location="성수 오마카세", source="Snaptok AI",
         display_image=poster_svg("🎂", "생일 저녁 약속", "성수 오마카세 · 19:00", "#FFE1EC")),
    dict(id="midterm", date="2026-09-30", time="09:00", title="전공 중간고사",
         location="공학관 302호", source="Snaptok AI",
         display_image=poster_svg("📝", "전공 중간고사", "공학관 302호 · 09:00", "#EDE6FB")),
]


# ---- 보관함 시드 ----
LIBRARY = [
    dict(id="seed-food-seongsu", title="성수 생면 파스타", category="맛집", place_name="성수",
         note="성수 방문 시 다시 보여주기", thumb="🍝",
         display_image=poster_svg("🍝", "성수 생면 파스타", "성수 방문 시 다시 보여주기", "#FFE3D6"),
         source="스크린샷", created_offset=-5 * H,
         geo_type="specific", lat=37.5446, lng=127.0559, radius=150, area="성수", geo_enabled=True),
    dict(id="seed-food-yeonnam", title="연남동 파스타집", category="맛집", place_name="연남동",
         note="연남동 갈 때 들르기", thumb="🍝",
         display_image=poster_svg("🍝", "연남동 파스타집", "연남동 갈 때 들르기", "#FFE3D6"),
         source="스크린샷", created_offset=-6 * H,
         geo_type="specific", lat=37.5663, lng=126.9254, radius=150, area="연남동", geo_enabled=True),
    dict(id="seed-food-yeoksam", title="역삼 생면 파스타", category="맛집", place_name="역삼",
         note="회사 근처 점심 후보", thumb="🍝",
         display_image=poster_svg("🍝", "역삼 생면 파스타", "회사 근처 점심 후보", "#FFE3D6"),
         source="스크린샷", created_offset=-7 * H,
         geo_type="specific", lat=37.5015, lng=127.0380, radius=150, area="역삼", geo_enabled=True),
    dict(id="seed-coupon-oliveyoung", title="올리브영 세일 15% 쿠폰", category="쿠폰", place_name="",
         note="코드 WELCOME15 · 사용기한 9/23", thumb="🎟️",
         display_image=poster_svg("🎟️", "올리브영 15% 쿠폰", "코드 WELCOME15", "#FFEBD0"),
         source="카카오톡 공유", created_offset=-1 * D, expiry="2026-09-23"),
    dict(id="seed-trip-huinyeoul", title="흰여울문화마을", category="여행지", place_name="부산 영도",
         note="부산 여행 후보", thumb="🌊",
         display_image=poster_svg("🌊", "흰여울문화마을", "부산 영도 · 여행 후보", "#DCEFFB"),
         source="스크린샷", created_offset=-1 * D - 3 * H),
    dict(id="seed-expo-media", title="서울 미디어아트 전시", category="전시회", place_name="성수",
         note="주말 관람 후보", thumb="🖼️",
         display_image=poster_svg("🖼️", "미디어아트 전시", "성수 · 주말 관람 후보", "#F6E4F4"),
         source="스크린샷", created_offset=-2 * D,
         geo_type="specific", lat=37.5446, lng=127.0559, radius=700, area="성수", geo_enabled=True),
    dict(id="seed-fashion-jacket", title="가을 바람막이 후드집업", category="패션", place_name="무신사",
         note="쇼핑 관심 상품", thumb="🧥",
         display_image=poster_svg("🧥", "가을 바람막이", "무신사 · 쇼핑 관심 상품", "#EDE6FB"),
         source="스크린샷", created_offset=-2 * D - 4 * H),
    dict(id="seed-birthday-roommate", title="룸메이트 생일 선물 후보", category="생일", place_name="",
         note="다이슨 드라이기 사고 싶어함", thumb="🎁",
         display_image=poster_svg("🎁", "생일 선물 후보", "다이슨 드라이기", "#FFE1EC"),
         source="카카오톡 공유", created_offset=-3 * D),
    dict(id="seed-movie-interstellar", title="인터스텔라 재개봉", category="영화", place_name="",
         note="친구랑 같이 보러 가기로 함", thumb="🎬",
         display_image=poster_svg("🎬", "인터스텔라 재개봉", "친구랑 보러 가기로 함", "#E3E0FA"),
         source="스크린샷", created_offset=-3 * D - 6 * H),
    dict(id="seed-concert-day6", title="데이식스 전국투어 티켓 오픈 안내", category="콘서트", place_name="",
         note="티켓팅 날짜 다시 확인 필요", thumb="🎤",
         display_image=poster_svg("🎤", "데이식스 투어", "티켓팅 날짜 확인 필요", "#FFE0E0"),
         source="스크린샷", created_offset=-4 * D),
    dict(id="seed-study-algo", title="알고리즘 스터디 정리노트", category="공부", place_name="",
         note="동적계획법 파트 정리", thumb="📚",
         display_image=poster_svg("📚", "알고리즘 정리노트", "동적계획법 파트", "#E1F3E6"),
         source="사진첩", created_offset=-4 * D - 5 * H),
    dict(id="seed-trip-kyoto", title="교토 벚꽃 여행 후보 스팟", category="여행지", place_name="교토",
         note="내년 4월 여행 후보 · 저장만", thumb="✈️",
         display_image=poster_svg("✈️", "교토 벚꽃 여행", "내년 4월 여행 후보", "#DCEFFB"),
         source="스크린샷", created_offset=-5 * D),
]


# ---- 활동 기록 시드 ----
RECENT = [
    dict(id="r-seed-1", kind="event", kind_ref="ideathon-deadline",
         summary="캘린더 등록 · AI 서비스 아이디어톤 신청 마감", detail="9/27 18:00", created_offset=-2 * H,
         display_image=poster_svg("🏆", "아이디어톤 신청마감", "9/27 18:00", "#E3ECFF")),
    dict(id="r-seed-2", kind="library", kind_ref="seed-coupon-oliveyoung",
         summary="보관함 저장 · 올리브영 세일 15% 쿠폰", detail="쿠폰 · 사용기한 9/23", created_offset=-1 * D,
         display_image=poster_svg("🎟️", "올리브영 15%", "사용기한 9/23", "#FFEBD0")),
    dict(id="r-seed-3", kind="event", kind_ref="seminar-review",
         summary="캘린더 등록 · 전공 세미나 안내", detail="날짜만 확실해 사용자 확인 후 등록", created_offset=-1 * D - 2 * H,
         display_image=poster_svg("📢", "전공 세미나", "사용자 확인 후 등록", "#F6E4F4")),
    dict(id="r-seed-4", kind="library", kind_ref="seed-food-seongsu",
         summary="보관함 저장 · 성수 생면 파스타", detail="맛집 · 성수", created_offset=-5 * H,
         display_image=poster_svg("🍝", "성수 파스타", "성수", "#FFE3D6")),
    dict(id="r-seed-5", kind="library", kind_ref="seed-concert-day6",
         summary="보관함 저장 · 데이식스 콘서트", detail="확신도 낮아 확인 필요로 표시", created_offset=-4 * D,
         display_image=poster_svg("🎤", "데이식스 투어", "확인 필요", "#FFE0E0")),
]
