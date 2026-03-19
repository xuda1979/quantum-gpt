def parse_assignment(line: str) -> tuple[str, str]:
    if "=" not in line:
        raise ValueError("missing '=' separator")
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        raise ValueError("empty key")
    return key, value


def regression_cases() -> list[dict[str, object]]:
    return [
        {
            "name": "trims surrounding whitespace",
            "input": " answer = 42 ",
            "expected": ("answer", "42"),
        },
        {
            "name": "preserves embedded equals in value",
            "input": "token=abc=def",
            "expected": ("token", "abc=def"),
        },
        {
            "name": "allows empty values",
            "input": "flag=",
            "expected": ("flag", ""),
        },
        {
            "name": "rejects empty keys",
            "input": " = nope",
            "raises": ValueError,
        },
        {
            "name": "rejects missing separator",
            "input": "no assignment here",
            "raises": ValueError,
        },
    ]
