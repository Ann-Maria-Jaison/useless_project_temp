# core/explainer.py

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import ast

from .analyzer import CodeAnalysis
from .runner import run_code


@dataclass
class ExplainResult:
    summary: str
    variables_summary: List[str]
    functions_summary: List[str]
    loops_summary: List[str]
    conditions_summary: List[str]
    operations_summary: List[str]
    predictable_output: Optional[str]
    manglish_take: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def explain_code(analysis: CodeAnalysis) -> ExplainResult:
    """
    Consumes CodeAnalysis and generates beginner-friendly Malayalam/Manglish explanations.
    """
    if not analysis.source.strip():
        return ExplainResult(
            summary="Code ഒന്നും തന്നില്ലല്ലോ ബ്രോ. Editor-ൽ കുറച്ചു Python code എഴുതൂ!",
            variables_summary=[],
            functions_summary=[],
            loops_summary=[],
            conditions_summary=[],
            operations_summary=[],
            predictable_output=None,
            manglish_take="“Empty code ആണ്... ഇവിടെ ഒന്നും ചെയ്യാനില്ല!” 😂"
        )

    # 1. Variables Summary
    var_sums = []
    for var in analysis.variables:
        name = var["name"]
        val = var["value_repr"]
        var_sums.append(f"Variable '{name}' ഉണ്ടാക്കി (value: {val}).")

    # 2. Functions Summary
    func_sums = []
    for fn in analysis.functions:
        name = fn["name"]
        args = ", ".join(fn["args"]) if fn["args"] else "args ഒന്നും ഇല്ല"
        func_sums.append(f"Function '{name}({args})' ഉണ്ടാക്കി (purpose: reusable logic).")

    # 3. Loops Summary
    loop_sums = []
    for lp in analysis.loops:
        if lp["kind"] == "for":
            loop_sums.append(f"For loop ഉപയോഗിച്ച് '{lp['iter_expr']}' üzerinden ഓരോ item എടുത്തു repeat ചെയ്യുന്നു.")
        else:
            loop_sums.append("While loop ഉപയോഗിച്ച് condition true ആകുന്നതുവരെ repeat ചെയ്യുന്നു.")

    # 4. Conditions Summary
    cond_sums = []
    for cd in analysis.conditions:
        cond_sums.append(f"If condition '{cd['test_code']}' check ചെയ്യുന്നു.")

    # 5. Operations Summary
    op_sums = []
    if any(c["func_name"] == "print" for c in analysis.calls):
        op_sums.append("Output screen-ൽ വിവരങ്ങൾ കാണിക്കാൻ print() ഉപയോഗിച്ചു.")
    if any(c["func_name"] in ("len", "range", "sum", "min", "max", "abs") for c in analysis.calls):
        op_sums.append("Built-in python functions (len/range/sum/math) ഉപയോഗിച്ച് calculations ചെയ്തു.")

    # 6. Overall Behavior Summary
    summary_parts = []
    if analysis.variables:
        summary_parts.append(f"ആദ്യം {len(analysis.variables)} variable(s) assign ചെയ്തു.")
    if analysis.functions:
        summary_parts.append(f"{len(analysis.functions)} function(s) define ചെയ്തു.")
    if analysis.loops:
        summary_parts.append(f"പിന്നെ {len(analysis.loops)} loop(s) ഉപയോഗിച്ച് repeat ചെയ്തു.")
    if analysis.conditions:
        summary_parts.append("Condition check നടത്തി logic control ചെയ്തു.")
    if any(c["func_name"] == "print" for c in analysis.calls):
        summary_parts.append("അവസാനം result print ചെയ്തു.")

    if not summary_parts:
        summary = "ഈ code basic python statements execute ചെയ്യുന്നു."
    else:
        summary = "ബ്രോ, " + " ".join(summary_parts)

    # 7. Predictable Output (only when statically predictable or safe deterministic execution)
    predictable_output = None
    if not any(i.severity == "ERROR" for i in analysis.issues):
        try:
            res = run_code(analysis.source, timeout=1)
            if res.get("ok") and res.get("output"):
                predictable_output = res["output"].strip()
        except Exception:
            predictable_output = None

    # 8. Manglish Take Joke
    if len(analysis.loops) > 0 and len(analysis.functions) > 0:
        take = "“Functions-ഉം loops-ഉം വച്ചുള്ള ഒന്നാന്തരം code structure ബ്രോ!” 😂"
    elif len(analysis.loops) > 0:
        take = "“ഓരോ item-നും ആവർത്തിച്ച് വിട്ടുപിടിക്കാതെ നോക്കുന്നുണ്ട്!” 😂"
    elif len(analysis.conditions) > 0:
        take = "“Condition ശരിയാണോ എന്ന് പരീക്ഷിച്ചു കൊണ്ടിരിക്കുകയാണ്!” 😂"
    elif predictable_output:
        take = "“Simple ആയി പറഞ്ഞാൽ: വള്ളി പുള്ളി തെറ്റാതെ കൃത്യമായി ഓടുന്നു!” 😂"
    else:
        take = "“Code ഓടുന്നുണ്ട്... എന്തായാലും നമുക്ക് നോക്കാം!” 😂"

    return ExplainResult(
        summary=summary,
        variables_summary=var_sums,
        functions_summary=func_sums,
        loops_summary=loop_sums,
        conditions_summary=cond_sums,
        operations_summary=op_sums,
        predictable_output=predictable_output,
        manglish_take=take
    )
