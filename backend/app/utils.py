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
