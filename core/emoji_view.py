# core/emoji_view.py — Line-by-line regex code-to-emoji translator

import re
from typing import List, Dict, Any


def classify_line_to_emoji(line: str) -> str:
    """
    Classifies a single line of Python code to its corresponding emoji icon using conservative regex matching.
    Defaults to ⬜ for unknown / unclassified lines.
    """
    s = line.strip()
    if not s:
        return "⬜"

    if re.match(r"^#", s):
        return "💬"
    if re.match(r"^(from|import)\b", s):
        return "📦"
    if re.match(r"^(async\s+)?def\b", s):
        return "🎁"
    if re.match(r"^return\b", s):
        return "🔚"
    if re.match(r"^raise\b", s):
        return "🚨"
    if re.match(r"^print\s*\(", s):
        return "🔢"
    if re.match(r"^input\s*\(", s):
        return "📥"
    if re.match(r"^(async\s+)?for\b", s):
        return "🔁"
    if re.match(r"^while\b", s):
        return "🔄"
    if re.match(r"^(if|elif|else)\b", s):
        return "🔀"
    if re.match(r"^(try|except|finally)\b", s):
        return "🛡️"
    if re.match(r"^break\b", s):
        return "🚪"
    if re.match(r"^continue\b", s):
        return "⏭️"
    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*\s*(\+|-|\*|/|//|%|\*\*|&|\||\^|<<|>>)?=", s):
        return "📝"

    # Conservative default
    return "⬜"


def code_to_emoji(code: str) -> List[Dict[str, Any]]:
    """
    Translates full Python code into line-by-line emoji representations.
    Returns a list of dicts: [{"line": line_number, "code": line_str, "emoji": emoji_icon}]
    """
    if not isinstance(code, str):
        return []

    lines = code.splitlines()
    translated = []

    for i, line in enumerate(lines, start=1):
        emoji = classify_line_to_emoji(line)
        translated.append({
            "line": i,
            "code": line,
            "emoji": emoji
        })

    return translated
