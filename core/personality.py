# core/personality.py

from dataclasses import dataclass, asdict
from typing import Dict, Any

from .analyzer import CodeAnalysis


@dataclass
class PersonalityResult:
    scores: Dict[str, int]        # {Logic, Chaos, Organization, Overthinking, Simplicity}
    developer_type: str
    manglish_comment: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def analyze_personality(analysis: CodeAnalysis) -> PersonalityResult:
    """
    Computes a hilarious code personality profile based strictly on AST metrics.
    
    Formula Rules:
    - Logic: derived from condition count + function call ratio.
    - Chaos: derived from nesting depth, warnings, errors, and bare excepts.
    - Organization: derived from function count, class count, and comment lines.
    - Overthinking: derived from function count vs low line count ratio + nesting depth.
    - Simplicity: inverse of nesting depth, conditions, and extra abstractions.
    """
    m = analysis.metrics
    issues = analysis.issues

    cond_cnt = m.get("condition_count", 0)
    func_cnt = m.get("function_count", 0)
    class_cnt = m.get("class_count", 0)
    loop_cnt = m.get("loop_count", 0)
    nesting_depth = m.get("max_nesting_depth", 0)
    code_lines = m.get("code_lines", 0)
    comment_lines = m.get("comment_lines", 0)
    call_cnt = m.get("call_count", 0)

    err_cnt = sum(1 for i in issues if i.severity == "ERROR")
    warn_cnt = sum(1 for i in issues if i.severity == "WARNING")

    # 1. Logic Score (0-100)
    # Formula: Base 30 + (conditions * 15) + (calls * 5)
    logic = min(100, max(10, 30 + (cond_cnt * 15) + (call_cnt * 5)))

    # 2. Chaos Score (0-100)
    # Formula: (nesting_depth * 15) + (warnings * 12) + (errors * 25)
    chaos = min(100, max(5, (nesting_depth * 15) + (warn_cnt * 12) + (err_cnt * 25)))

    # 3. Organization Score (0-100)
    # Formula: (functions * 20) + (classes * 25) + (comment_lines * 15)
    organization = min(100, max(10, (func_cnt * 20) + (class_cnt * 25) + (comment_lines * 15)))
    if func_cnt == 0 and class_cnt == 0 and code_lines > 5:
        organization = max(15, organization - 20)

    # 4. Overthinking Score (0-100)
    # Formula: (functions * 25) + (nesting_depth * 15) - (code_lines * 2)
    overthinking = min(100, max(5, (func_cnt * 25) + (nesting_depth * 15) - (max(0, code_lines - 10) * 2)))

    # 5. Simplicity Score (0-100)
    # Formula: 100 - (nesting_depth * 15) - (func_cnt * 10) - (cond_cnt * 8)
    simplicity = min(100, max(5, 100 - (nesting_depth * 15) - (func_cnt * 10) - (cond_cnt * 8)))

    scores = {
        "Logic": int(logic),
        "Chaos": int(chaos),
        "Organization": int(organization),
        "Overthinking": int(overthinking),
        "Simplicity": int(simplicity)
    }

    # Determine Developer Type
    if overthinking > 70:
        dev_type = "🧙 THE OVERTHINKING PYTHON WIZARD"
        comment = f"“ബ്രോ, {code_lines} line code-ന് {func_cnt} functions എന്തിനാ?” 😂"
    elif chaos > 60:
        dev_type = "💥 THE CHAOTIC MAD SCIENTIST"
        comment = "“Code എങ്ങനെ ഒക്കെ ഒപ്പിക്കുന്നുണ്ട്... പക്ഷെ റിസ്ക് കൂടുതലാണ് ബ്രോ!” 😂"
    elif organization > 65 and simplicity > 50:
        dev_type = "🚀 THE EFFICIENT CODE NINJA"
        comment = "“പക്കാ clean & clean! ആവശ്യത്തിന് മാത്രം abstractions!” 🎉"
    elif simplicity > 75:
        dev_type = "🐣 THE NOVICE EXPLORER"
        comment = "“Short & sweet! ആരുടെയും തലവേദനയില്ലാത്ത കോഡ്!” 😊"
    else:
        dev_type = "💻 THE PRAGMATIC PYTHON DEVELOPER"
        comment = "“കാര്യങ്ങൾ നടക്കുന്നുണ്ട് ബ്രോ! Keep coding!” 👍"

    return PersonalityResult(
        scores=scores,
        developer_type=dev_type,
        manglish_comment=comment
    )
