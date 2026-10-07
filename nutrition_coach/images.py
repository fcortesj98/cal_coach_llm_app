"""Validation and Base64 encoding of uploaded meal photos."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO

from PIL import Image, UnidentifiedImageError

# Formats the vision model accepts as data URLs.
_MIME_BY_FORMAT = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}


class InvalidImageError(ValueError):
    """Raised when an upload is empty or not a supported image."""


@dataclass(frozen=True)
class EncodedImage:
    base64_data: str
    mime_type: str

    @property
    def data_url(self) -> str:
        return f"data:{self.mime_type};base64,{self.base64_data}"


def encode_upload(stream: BinaryIO) -> EncodedImage:
    """Read an uploaded file, check it is a real image, and Base64-encode it."""
    raw = stream.read()
    if not raw:
        raise InvalidImageError("The uploaded file is empty.")

    try:
        with Image.open(BytesIO(raw)) as img:
            img.verify()
            image_format = img.format
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("The uploaded file is not a valid image.") from exc

    mime_type = _MIME_BY_FORMAT.get(image_format or "")
    if mime_type is None:
        supported = ", ".join(sorted(_MIME_BY_FORMAT))
        raise InvalidImageError(f"Unsupported image format. Use one of: {supported}.")

    return EncodedImage(base64.b64encode(raw).decode("utf-8"), mime_type)
