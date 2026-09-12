# core/cleaner.py

import re
import ast
import io
import tokenize
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from .analyzer import CodeAnalysis


@dataclass
class CleanerResult:
    original: str
    cleaned: str
    changes_made: List[str]
    manglish_comment: str
    is_modified: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def clean_code(analysis: CodeAnalysis) -> CleanerResult:
    """
    Consumes CodeAnalysis and applies provably safe formatting transforms without altering code semantics.
    """
    original = analysis.source
    if not original.strip():
        return CleanerResult(
            original=original,
            cleaned=original,
            changes_made=[],
            manglish_comment="Code ഒന്നും ഇല്ലാത്തത് കൊണ്ട് clean ചെയ്യാൻ പറ്റില്ല ബ്രോ!",
            is_modified=False
        )

    # If syntax error exists, return original untouched with safety explanation
    if analysis.syntax_error or any(i.severity == "ERROR" and i.type == "SyntaxError" for i in analysis.issues):
        return CleanerResult(
            original=original,
            cleaned=original,
            changes_made=["Syntax error ഉള്ളത് കൊണ്ട് safery മുൻനിർത്തി reformatter ഓടിച്ചില്ല."],
            manglish_comment="“Syntax error ആദ്യം ശരിയാക്ക് ബ്രോ, എന്നിട്ട് clean ആക്കാം!” 🛑",
            is_modified=False
        )

    changes = []
    lines = original.splitlines()

    # Step 1: Trim trailing whitespace
    trimmed_lines = [line.rstrip() for line in lines]
    if any(l1 != l2 for l1, l2 in zip(lines, trimmed_lines)):
        changes.append("Lines-ന്റെ അവസാനിയിലെ ആവശ്യമില്ലാത്ത spaces നീക്കം ചെയ്തു (Trimmed trailing spaces).")

    # Step 2: Normalize multiple consecutive blank lines to max 1
    collapsed_lines = []
    blank_count = 0
    for line in trimmed_lines:
        if not line:
            blank_count += 1
            if blank_count <= 2:
                collapsed_lines.append(line)
        else:
            blank_count = 0
            collapsed_lines.append(line)

    if len(collapsed_lines) != len(trimmed_lines):
        changes.append("അധികമുള്ള blank lines ക്രമീകരിച്ചു (Collapsed multiple blank lines).")

    # Step 3: Spacing & Redundant Parens normalization line-by-line
    formatted_lines = []
    for line in collapsed_lines:
        new_line = line
        # Redundant parens in if/while (e.g., `if (x < y):` -> `if x < y:`)
        new_line = re.sub(r"\b(if|while|elif)\s*\(([^()]+)\):", r"\1 \2:", new_line)
        
        # Spacing after commas (if not inside string)
        if "," in new_line and not ('"' in new_line or "'" in new_line):
            new_line = re.sub(r",([^\s])", r", \1", new_line)

        # Spacing around binary operators like =, ==, +, -, *, /, <, > (simple non-string heuristic)
        if not ('"' in new_line or "'" in new_line or "#" in new_line):
            new_line = re.sub(r"\s*==\s*", " == ", new_line)
            new_line = re.sub(r"\s*(?<![=!<>+\-*/])=\s*([^=])", r" = \1", new_line)
            new_line = re.sub(r"\s*<\s*", " < ", new_line)
            new_line = re.sub(r"\s*>\s*", " > ", new_line)

        formatted_lines.append(new_line)

    if formatted_lines != collapsed_lines:
        changes.append("Operators-നും commas-നും ചുറ്റുമുള്ള spacing ശരിയാക്കി.")

    cleaned_result = "\n".join(formatted_lines)
    is_modified = (cleaned_result.strip() != original.strip())

    if is_modified:
        comment = "“ബ്രോ... code working ആയിരുന്നു. പക്ഷേ കണ്ടിട്ട് എനിക്ക് headache ആയിരുന്നു.” 😂"
    else:
        comment = "“Code പക്കാ clean ആണ് ബ്രോ! മാറ്റങ്ങൾ ഒന്നും വേണ്ടിവന്നില്ല!” ✨"

    return CleanerResult(
        original=original,
        cleaned=cleaned_result,
        changes_made=changes if changes else ["Code structure clean ആയി നിലനിർത്തി."],
        manglish_comment=comment,
        is_modified=is_modified
    )
