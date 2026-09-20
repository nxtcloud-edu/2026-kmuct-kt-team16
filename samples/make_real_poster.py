"""실제 포스터 재현: 연도 명시 + 기간 + 결과 발표. (파일명에 분류 힌트 없음: 실제 LLM 판독)"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = r"C:\Windows\Fonts\malgun.ttf"

def f(sz): return ImageFont.truetype(FONT, sz)

img = Image.new("RGB", (1000, 1400), (18, 22, 55))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 1000, 140], fill=(255, 91, 84))
d.text((60, 44), "2025 대학생 아이디어 공모전", font=f(46), fill=(255, 255, 255))
lines = [
    ("주제: 지속가능한 캠퍼스", 34, (230, 230, 240), 260),
    ("접수 기간", 30, (255, 200, 120), 380),
    ("2025.7.4(금) ~ 2025.8.31(일)", 40, (255, 255, 255), 430),
    ("결과 발표", 30, (255, 200, 120), 560),
    ("2025.9월 중순 (개별 통보)", 36, (255, 255, 255), 610),
    ("시상: 대상 500만원 외", 30, (210, 210, 225), 740),
    ("주최: 총학생회 · 후원: OO재단", 26, (180, 180, 200), 820),
    ("접수: 홈페이지 온라인 제출", 26, (180, 180, 200), 880),
]
for text, sz, color, y in lines:
    d.text((60, y), text, font=f(sz), fill=color)
img.save(OUT / "real_contest_poster.png")
print("wrote real_contest_poster.png")
