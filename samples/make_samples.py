"""시연 샘플 3장 생성(Pillow, malgun.ttf). 파일명에 mock 분류 키워드 포함."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = r"C:\Windows\Fonts\malgun.ttf"


def font(sz):
    return ImageFont.truetype(FONT, sz)


def make(name, tint, lines):
    img = Image.new("RGB", (720, 960), tint)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 720, 70], fill=(21, 27, 61))
    d.text((28, 22), "Snaptok Sample", font=font(26), fill=(255, 255, 255))
    y = 160
    for text, sz, color in lines:
        d.text((40, y), text, font=font(sz), fill=color)
        y += sz + 26
    img.save(OUT / name, quality=90)
    print("wrote", name)


# 1) 연남동 파스타 맛집 (파일명: yeonnam_pasta_food)
make("yeonnam_pasta_food.jpg", (255, 240, 225), [
    ("연남동 파스타집", 52, (30, 30, 40)),
    ("연남동 골목 안 작은 파스타 맛집", 30, (90, 84, 104)),
    ("생면 파스타 · 와인", 28, (90, 84, 104)),
    ("연남동 갈 때 꼭 들르기", 26, (140, 60, 60)),
])

# 2) 스타벅스 기프티콘 (파일명: starbucks_coupon), 사용기한 2026-09-25
make("starbucks_coupon.jpg", (255, 235, 208), [
    ("스타벅스 아메리카노", 48, (30, 30, 40)),
    ("기프티콘 · Gifticon", 30, (90, 84, 104)),
    ("사용기한 2026-09-25", 34, (180, 40, 40)),
    ("전국 스타벅스 매장", 26, (90, 84, 104)),
])

# 3) 공모전 포스터 (파일명: contest_ideathon), 접수 마감 + 본선 발표
make("contest_ideathon.jpg", (227, 236, 255), [
    ("AI 서비스 아이디어톤", 46, (30, 30, 40)),
    ("공모전 · Contest", 30, (90, 84, 104)),
    ("접수 마감 2026-09-27 18:00", 30, (180, 40, 40)),
    ("본선 발표 2026-09-29 14:00", 30, (40, 60, 160)),
    ("온라인 접수", 26, (90, 84, 104)),
])
