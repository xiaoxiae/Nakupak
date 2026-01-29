from app.utils import strip_emoji


def test_no_emoji():
    assert strip_emoji("Milk") == "Milk"


def test_leading_emoji():
    assert strip_emoji("🥛 Milk") == "Milk"


def test_multiple_leading_emojis():
    assert strip_emoji("🥛🧈 Butter") == "Butter"


def test_only_emoji():
    assert strip_emoji("🥛🧈") == ""


def test_middle_emoji_not_stripped():
    result = strip_emoji("A 🥛 B")
    assert result == "A 🥛 B"


def test_empty_string():
    assert strip_emoji("") == ""


def test_whitespace_only():
    assert strip_emoji("   ") == ""
