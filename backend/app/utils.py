import re
import unicodedata

_EMOJI_RE = re.compile(
    r'^[\U0001F300-\U0001FAFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0000200D\s]+',
)


def strip_emoji(s: str) -> str:
    return _EMOJI_RE.sub('', s)


def sort_key(s: str) -> str:
    s = strip_emoji(s).lower()
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')


# Raster image types we accept for uploads; SVG is excluded since it can carry scripts.
_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def image_extension(content_type: str | None) -> str | None:
    """Safe file extension for an image content type, or None if not an allowed image."""
    if not content_type:
        return None
    mime = content_type.split(";")[0].strip().lower()
    return _IMAGE_EXTENSIONS.get(mime)
