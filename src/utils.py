from __future__ import annotations

FORBIDDEN_WORDS: list[str] = [
    "touch", "taste", "eat", "pick mushroom", "pick berries",
    "chhoona", "khana", "khaana", "chakhna",
]

def contains_forbidden(text: str) -> bool:
    """Return True if any forbidden word appears in the lowered text."""
    lowered = text.lower()
    for word in FORBIDDEN_WORDS:
        if word in lowered:
            return True
    return False


def validate_hunt(hunt: dict, expected_items: int) -> None:
    """Validate a hunt dict; raise ValueError on any rule violation."""
    if not isinstance(hunt, dict):
        raise ValueError("hunt must be a dict")

    required_keys = {"title", "intro", "items", "bonus_challenge", "parent_note"}
    missing = required_keys - set(hunt.keys())
    if missing:
        raise ValueError(f"hunt is missing required keys: {missing}")

    items = hunt["items"]
    if not isinstance(items, list):
        raise ValueError("items must be a list")

    if len(items) != expected_items:
        raise ValueError(
            f"items length is {len(items)}, expected {expected_items}"
        )

    allowed_types = {"spot", "sound", "smell", "count", "texture", "collect_safe"}

    for i, item in enumerate(items):
        missing_keys = {"id", "emoji", "text_en", "text_hi", "hint", "type"} - set(item.keys())
        if missing_keys:
            raise ValueError(
                f"item {i} is missing required keys: {missing_keys}"
            )
        item_type = item["type"]
        if item_type not in allowed_types:
            raise ValueError(
                f"item {i} has invalid type '{item_type}'; "
                f"must be one of {allowed_types}"
            )
        for field in ("text_en", "text_hi", "hint"):
            if contains_forbidden(item[field]):
                raise ValueError(
                    f"item {i}'s {field} contains a forbidden word"
                )
        # emoji field just must exist — emoji content not checked
        if "emoji" not in item:
            raise ValueError(f"item {i} is missing 'emoji'")


def safe_filename(text: str) -> str:
    """Return a filesystem-safe version of text: lowercase, replace spaces
    with underscore, strip characters that are not [a-z0-9_-]."""
    import re

    text = text.lower()
    text = text.replace(" ", "_")
    text = re.sub(r"[^a-z0-9_-]", "", text)
    return text
