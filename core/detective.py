# core/detective.py

from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from .analyzer import CodeAnalysis


@dataclass
class DetectiveResult:
    counts: Dict[str, int]
    suspicious_activities: List[Dict[str, Any]]
    verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def inspect_code(analysis: CodeAnalysis) -> DetectiveResult:
    """
    Consumes CodeAnalysis and performs an AST code audit report with explicit ERROR / WARNING / INFO labels.
    """
    counts = {
        "Variables": analysis.metrics.get("variable_count", 0),
        "Functions": analysis.metrics.get("function_count", 0),
        "Classes": analysis.metrics.get("class_count", 0),
        "Imports": analysis.metrics.get("import_count", 0),
        "Loops": analysis.metrics.get("loop_count", 0),
        "Conditions": analysis.metrics.get("condition_count", 0),
        "Calls": analysis.metrics.get("call_count", 0),
    }

    suspicious = []

    # Map issues from analysis
    for issue in analysis.issues:
        suspicious.append({
            "severity": issue.severity,
            "kind": issue.type,
            "line": issue.line,
            "message": f"{issue.title} {issue.desc}".strip()
        })

    # Deep Nesting Check
    max_depth = analysis.metrics.get("max_nesting_depth", 0)
    if max_depth > 4:
        suspicious.append({
            "severity": "WARNING",
            "kind": "DeepNesting",
            "line": None,
            "message": f"Nesting level {max_depth} വളരെ കൂടുതലാണ്. Code readability കുറയും."
        })

    # Deduplicate suspicious list
    seen = set()
    unique_suspicious = []
    for item in suspicious:
        key = (item["severity"], item["kind"], item.get("line"), item["message"])
        if key not in seen:
            seen.add(key)
            unique_suspicious.append(item)

    # Detective Verdict
    errors_cnt = sum(1 for s in unique_suspicious if s["severity"] == "ERROR")
    warnings_cnt = sum(1 for s in unique_suspicious if s["severity"] == "WARNING")

    if errors_cnt > 0:
        verdict = f"🧾 Verdict: 'Scene മാറിയിട്ടുണ്ട് ബ്രോ! {errors_cnt} critical error(s) ഉണ്ട്. ആദ്യം അത് ശരിയാക്കൂ!'"
    elif warnings_cnt > 0:
        verdict = f"🧾 Verdict: 'Code working ആയിരിക്കാം ബ്രോ... പക്ഷേ {warnings_cnt} suspicious activity ശ്രദ്ധിക്കാനുണ്ട്!' 😂"
    else:
        verdict = "🧾 Verdict: 'Clean record ബ്രo! കുറ്റവും കുറവും ഒന്നും കണ്ടെത്താനായില്ല!' 🎉"

    return DetectiveResult(
        counts=counts,
        suspicious_activities=unique_suspicious,
        verdict=verdict
    )
