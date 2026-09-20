"""중복 판정용 바이그램 유사도. 데모(app.js)의 로직을 서버로 옮긴 것.

- normTitle: 소문자화 + 공백/특수문자 제거
- bigrams: 연속 2글자 집합
- similarity: Dice 계수 (2*교집합 / (|A|+|B|))
- 임계값 0.55
"""
from __future__ import annotations

import re

_STRIP = re.compile(r"[\s\u3000·,\.\-\_/()!?~]+")
THRESHOLD = 0.55


def norm_title(s: str | None) -> str:
    return _STRIP.sub("", str(s or "").lower())


def bigrams(s: str) -> set[str]:
    return {s[i : i + 2] for i in range(len(s) - 1)}


def similarity(a: str | None, b: str | None) -> float:
    na, nb = norm_title(a), norm_title(b)
    A, B = bigrams(na), bigrams(nb)
    if not A or not B:
        return 1.0 if na == nb else 0.0
    inter = len(A & B)
    return (2 * inter) / (len(A) + len(B))


def is_duplicate(a: str | None, b: str | None) -> bool:
    return similarity(a, b) >= THRESHOLD
