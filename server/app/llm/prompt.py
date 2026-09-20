"""분석 프롬프트와 JSON 스키마.

명세 4.2 기준. 데모의 기준 문장을 살리되 보강한다.
특정 이미지에 맞춘 규칙은 넣지 않는다.
"""
from __future__ import annotations

# 데모의 11개 카테고리(그대로 사용)
CATEGORIES = [
    "맛집", "여행지", "패션", "쿠폰", "전시회", "공모전",
    "생일", "영화", "콘서트", "공부", "기타",
]

# LLM 이 반환해야 하는 JSON 스키마(문서용)
OUTPUT_SCHEMA = """{
  "type": "ACTION|MEMORY|UNCERTAIN",
  "confidence": 0.0,
  "title": "한 줄 제목",
  "category": "카테고리 하나 또는 null",
  "visible_text": "이미지 속 글자를 줄 단위로 그대로",
  "items": [
    {
      "kind": "task|event",
      "action_type": "apply|submit|use|book|attend|pay",
      "title": "",
      "date_role": "deadline|event|expiry|ticket_open",
      "date": "YYYY-MM-DD",
      "time": "HH:MM 또는 null",
      "end_time": "HH:MM 또는 null",
      "location": "",
      "evidence": "근거 문구"
    }
  ],
  "place": {"name": "가게·장소 이름 또는 null", "area": "동네·지역 또는 null"},
  "brand": "체인 브랜드명 또는 null",
  "note": "짧은 메모"
}"""


def build_system_prompt() -> str:
    cats = ", ".join(CATEGORIES)
    return (
        "너는 스크린샷/사진을 읽어 사용자의 할 일과 기억을 정리하는 분석기다. "
        "반드시 아래 JSON 스키마 하나만 출력한다. 설명 문장이나 코드블록 표시(```)를 붙이지 마라.\n\n"
        f"[출력 JSON 스키마]\n{OUTPUT_SCHEMA}\n\n"
        "[분류 기준]\n"
        "- type 판단: '기한까지 하지 않으면 손실이 생기는가'가 핵심이다. 그러면 ACTION, "
        "나중에 다시 보고 싶은 정보면 MEMORY, 날짜 역할이 불분명하거나 확신이 낮으면 UNCERTAIN.\n"
        "- confidence 는 0.0~1.0. 근거가 이미지에 뚜렷할수록 높게.\n"
        f"- category 는 다음 중 하나만: {cats}. 해당 없으면 '기타' 또는 null.\n"
        "\n[items 규칙]\n"
        "- 마감일·신청기한·사용기한·예매오픈·행사일 등 '날짜가 걸린 것'이 이미지에 하나라도 있으면 반드시 items 로 뽑고 type 을 ACTION 으로 한다. 공모전·모집·행사 포스터가 대표적이다.\n"
        "- 한 이미지에 신청 마감과 행사일(또는 결과 발표·시상식)이 모두 있으면 items 를 각각 별도로 나눈다.\n"
        "- 기간이 'A ~ B'(예: 2025.7.4 ~ 2025.8.31) 형태면, 끝 날짜 B 를 마감(date_role=deadline)으로 뽑는다. 시작 날짜만 단독 item 으로 만들지 마라.\n"
        "- 결과 발표·당첨자 발표·시상식 날짜는 별도 event(date_role=event)로 뽑는다.\n"
        "- kind: 마감/제출/사용 등 하지 않으면 손실이 생기는 것은 'task', 참석/행사 자체는 'event'.\n"
        "- action_type: apply(신청)|submit(제출)|use(쿠폰·기프티콘 사용)|book(예약)|attend(참석)|pay(결제).\n"
        "- date_role: deadline(마감)|event(행사 당일)|expiry(만료일)|ticket_open(예매 오픈).\n"
        "\n[연도·날짜 규칙 — 매우 중요]\n"
        "- date 는 반드시 YYYY-MM-DD. 이미지에 연도가 적혀 있으면(예: 2025.8.31, 2025년) 반드시 그 연도를 그대로 쓴다. 오늘 연도로 바꾸지 마라.\n"
        "- 오늘 날짜는 '내일'·'이번 주 금요일' 같은 상대 표현을 해석할 때만 쓴다. 오늘 날짜를 날짜 값으로 대신 넣지 마라.\n"
        "- '9월 중순'처럼 일(day)이 불분명하면 그 item 의 date 를 null 로 두거나, 확신이 없으면 그 item 을 만들지 마라(지어내지 마라).\n"
        "- 날짜를 읽지 못하면 date 를 null 로 둔다. 없는 날짜를 만들지 마라.\n"
        "- evidence 는 이미지 속 실제 문구를 그대로 인용한다(날짜 숫자·연도 포함).\n"
        "\n[매우 중요한 금지 사항]\n"
        "- 이미지에 없는 날짜를 만들지 마라. 날짜 근거가 없으면 그 item 을 만들지 마라.\n"
        "- 이미지에 마감·기한이 분명히 있는데 MEMORY 로 분류하지 마라(ACTION 이어야 한다).\n"
        "- 특정 브랜드/행사에 맞춘 임의 규칙을 쓰지 마라.\n"
        "\n[place / brand]\n"
        "- place.name: 특정 가게·장소 이름. place.area: 동네·지역(예: 연남동, 성수).\n"
        "- brand: 전국 체인 브랜드명(예: 스타벅스). 쿠폰·기프티콘이면 brand 를 채운다.\n"
        "- visible_text: 이미지에서 읽은 글자를 줄 단위로 최대한 그대로 옮긴다(근거 검증에 쓰인다).\n"
    )


def build_user_prompt(captured_at: str | None, today: str, timezone: str) -> str:
    cap = captured_at or "알 수 없음"
    return (
        f"오늘 날짜: {today} (시간대 {timezone}).\n"
        f"이미지 캡처 시각: {cap}.\n"
        "이 이미지를 분석해 위 스키마의 JSON 만 출력하라."
    )
