"""이미지 파일 저장/조회 유틸. base64 대신 파일로 저장한다."""
from __future__ import annotations

import uuid
from pathlib import Path

from .config import IMAGES_DIR

# 지원 확장자 -> content-type
_EXT_CT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def _ext_for(content_type: str, filename: str | None) -> str:
    ct = (content_type or "").lower()
    if "png" in ct:
        return ".png"
    if "webp" in ct:
        return ".webp"
    if "gif" in ct:
        return ".gif"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    if filename:
        suffix = Path(filename).suffix.lower()
        if suffix in _EXT_CT:
            return suffix
    return ".jpg"


def save_image_bytes(data: bytes, content_type: str = "", filename: str | None = None) -> str:
    """이미지 바이트를 저장하고 image_id(확장자 포함 파일명) 반환."""
    ext = _ext_for(content_type, filename)
    image_id = f"{uuid.uuid4().hex}{ext}"
    (IMAGES_DIR / image_id).write_bytes(data)
    return image_id


def image_path(image_id: str) -> Path | None:
    """image_id 로 파일 경로 반환. 경로 이탈(../) 방지."""
    if not image_id:
        return None
    # 파일명만 허용 (디렉터리 구분자 차단)
    if "/" in image_id or "\\" in image_id or ".." in image_id:
        return None
    p = (IMAGES_DIR / image_id).resolve()
    try:
        p.relative_to(IMAGES_DIR.resolve())
    except ValueError:
        return None
    return p if p.exists() else None


def content_type_for(image_id: str) -> str:
    return _EXT_CT.get(Path(image_id).suffix.lower(), "application/octet-stream")
