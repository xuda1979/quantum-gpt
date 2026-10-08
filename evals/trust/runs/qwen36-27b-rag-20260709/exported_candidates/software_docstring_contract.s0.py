def normalize_identifier(raw: str) -> str:
    """Return a lowercase snake_case identifier built from a human label.

    Rules:
    - Trim leading/trailing whitespace.
    - Convert internal runs of whitespace or hyphens to a single underscore.
    - Remove any characters that are not ASCII letters, digits, underscores, spaces, or hyphens.
    - Collapse repeated underscores.
    """
    cleaned = []
    for char in raw.strip().lower():
        if char.isascii() and (char.isalnum() or char in {"_", " ", "-"}):
            cleaned.append(char)

    text = "".join(cleaned).replace("-", "_").replace(" ", "_")
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")
