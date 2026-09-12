# core/test_lab.py — AYYO Test Lab auto-test generator and runner

import ast
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from .analyzer import CodeAnalysis
from .runner import run_code


@dataclass
class GeneratedTest:
    function_name: str
    test_name: str
    code: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestLabResult:
    functions: List[str]
    tests: List[GeneratedTest]
    skipped: List[Dict[str, Any]]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "functions": self.functions,
            "tests": [t.to_dict() for t in self.tests],
            "skipped": self.skipped,
            "summary": self.summary
        }


def _is_complex_node(node: ast.AST) -> bool:
    """Returns True if the AST node contains complex constructs like loops, calls, try/except."""
    for child in ast.walk(node):
        if isinstance(child, (ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)):
            return True
        if isinstance(child, ast.Call):
            # Check if calling print, input, open, append, etc.
            func_name = ""
            if isinstance(child.func, ast.Name):
                func_name = child.func.id
            elif isinstance(child.func, ast.Attribute):
                func_name = child.func.attr
            if func_name in ("print", "input", "open", "exec", "eval", "append", "write", "extend", "remove", "pop"):
                return True
    return False


def _evaluate_ast_expr(expr: ast.AST, env: dict) -> Any:
    """Safely evaluates a simple arithmetic/comparison/string AST expression using Python's eval with limited scope."""
    code_obj = compile(ast.Expression(expr), filename="<eval>", mode="eval")
    return eval(code_obj, {"__builtins__": {}}, env)


def generate_test_lab(analysis: CodeAnalysis) -> TestLabResult:
    """
    Analyzes functions in the user's code AST and generates unittest cases for simple functions
    while conservatively skipping complex ones.
    """
    functions_found: List[str] = []
    generated_tests: List[GeneratedTest] = []
    skipped: List[Dict[str, Any]] = []

    if not analysis.tree:
        return TestLabResult(
            functions=[],
            tests=[],
            skipped=[],
            summary="ബ്രോ, valid Python code തന്നാൽ മാത്രമേ tests ഉണ്ടാക്കാൻ പറ്റൂ."
        )

    # Gather FunctionDef nodes
    func_nodes: List[ast.FunctionDef] = []
    for node in ast.iter_child_nodes(analysis.tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_nodes.append(node)

    for fn in func_nodes:
        fn_name = fn.name
        functions_found.append(fn_name)

        # 1. Complexity check
        is_complex = False
        skip_reason = ""

        if _is_complex_node(fn):
            is_complex = True
            skip_reason = f"⚠️ Function '{fn_name}()' is too complex for auto-tests (uses loops / side-effects). Skipping — needs human-written tests."

        # Extract arguments
        args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]

        # Look for return statement
        return_nodes = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]

        if not is_complex and len(return_nodes) != 1:
            is_complex = True
            skip_reason = f"⚠️ Function '{fn_name}()' has multiple or no return statements. Skipping — needs human-written tests."

        if is_complex:
            skipped.append({
                "function": fn_name,
                "reason": skip_reason
            })
            continue

        ret_expr = return_nodes[0].value
        if ret_expr is None:
            skipped.append({
                "function": fn_name,
                "reason": f"⚠️ Function '{fn_name}()' returns None. Skipping — needs human-written tests."
            })
            continue

        # Try to analyze return expression
        tests_for_fn: List[GeneratedTest] = []

        try:
            # Case A: Binary Arithmetic (+, -, *, /)
            if isinstance(ret_expr, ast.BinOp) and len(args) >= 2:
                param1, param2 = args[0], args[1]
                op = ret_expr.op

                # Test positive
                env_pos = {param1: 2, param2: 3}
                val_pos = _evaluate_ast_expr(ret_expr, env_pos)
                tests_for_fn.append(GeneratedTest(
                    function_name=fn_name,
                    test_name=f"test_{fn_name}_positive",
                    code=f"def test_{fn_name}_positive():\n    assert {fn_name}(2, 3) == {repr(val_pos)}",
                    reason="Positive integer test"
                ))

                # Test negative
                env_neg = {param1: -2, param2: -3}
                val_neg = _evaluate_ast_expr(ret_expr, env_neg)
                tests_for_fn.append(GeneratedTest(
                    function_name=fn_name,
                    test_name=f"test_{fn_name}_negative",
                    code=f"def test_{fn_name}_negative():\n    assert {fn_name}(-2, -3) == {repr(val_neg)}",
                    reason="Negative integer test"
                ))

                # Test zero
                env_zero = {param1: 0, param2: 0}
                if not (isinstance(op, ast.Div) or isinstance(op, ast.FloorDiv) or isinstance(op, ast.Mod)):
                    val_zero = _evaluate_ast_expr(ret_expr, env_zero)
                    tests_for_fn.append(GeneratedTest(
                        function_name=fn_name,
                        test_name=f"test_{fn_name}_zero",
                        code=f"def test_{fn_name}_zero():\n    assert {fn_name}(0, 0) == {repr(val_zero)}",
                        reason="Zero edge case test"
                    ))

            # Case B: String concatenation / formatting
            elif (isinstance(ret_expr, ast.BinOp) and isinstance(ret_expr.op, ast.Add)) or isinstance(ret_expr, ast.JoinedStr):
                if len(args) >= 1:
                    param = args[0]
                    # Test standard string
                    env_str = {param: "World"}
                    val_str = _evaluate_ast_expr(ret_expr, env_str)
                    tests_for_fn.append(GeneratedTest(
                        function_name=fn_name,
                        test_name=f"test_{fn_name}_standard",
                        code=f"def test_{fn_name}_standard():\n    assert {fn_name}('World') == {repr(val_str)}",
                        reason="Standard string input test"
                    ))

                    # Test empty string
                    env_empty = {param: ""}
                    val_empty = _evaluate_ast_expr(ret_expr, env_empty)
                    tests_for_fn.append(GeneratedTest(
                        function_name=fn_name,
                        test_name=f"test_{fn_name}_empty",
                        code=f"def test_{fn_name}_empty():\n    assert {fn_name}('') == {repr(val_empty)}",
                        reason="Empty string edge case test"
                    ))

            # Case C: Comparison operator
            elif isinstance(ret_expr, ast.Compare) and len(args) >= 1:
                param = args[0]
                env_val1 = {param: 5}
                env_val2 = {param: -5}
                val1 = _evaluate_ast_expr(ret_expr, env_val1)
                val2 = _evaluate_ast_expr(ret_expr, env_val2)
                tests_for_fn.append(GeneratedTest(
                    function_name=fn_name,
                    test_name=f"test_{fn_name}_comparison_positive",
                    code=f"def test_{fn_name}_comparison_positive():\n    assert {fn_name}(5) == {repr(val1)}",
                    reason="Positive value comparison test"
                ))
                tests_for_fn.append(GeneratedTest(
                    function_name=fn_name,
                    test_name=f"test_{fn_name}_comparison_negative",
                    code=f"def test_{fn_name}_comparison_negative():\n    assert {fn_name}(-5) == {repr(val2)}",
                    reason="Negative value comparison test"
                ))

            # Generic single param or constant return fallback
            elif isinstance(ret_expr, (ast.Constant, ast.Name)):
                if len(args) == 1:
                    param = args[0]
                    env_val = {param: 10}
                    val = _evaluate_ast_expr(ret_expr, env_val)
                    tests_for_fn.append(GeneratedTest(
                        function_name=fn_name,
                        test_name=f"test_{fn_name}_isolation",
                        code=f"def test_{fn_name}_isolation():\n    assert {fn_name}(10) == {repr(val)}",
                        reason="Parameter isolation test"
                    ))
                elif len(args) == 0:
                    val = _evaluate_ast_expr(ret_expr, {})
                    tests_for_fn.append(GeneratedTest(
                        function_name=fn_name,
                        test_name=f"test_{fn_name}_no_args",
                        code=f"def test_{fn_name}_no_args():\n    assert {fn_name}() == {repr(val)}",
                        reason="No-argument return test"
                    ))

        except Exception:
            # If expression evaluation fails or is ambiguous
            pass

        if tests_for_fn:
            generated_tests.extend(tests_for_fn)
        else:
            skipped.append({
                "function": fn_name,
                "reason": f"⚠️ Function '{fn_name}()' return logic is not deterministically inferable. Skipping — needs human-written tests."
            })

    # Build summary statement
    tested_functions_count = len(set(t.function_name for t in generated_tests))
    total_functions_count = len(functions_found)

    if total_functions_count == 0:
        summary = "ബ്രോ, കോഡിൽ functions ഒന്നും കണ്ടെത്തിയില്ല! Test ഉണ്ടാക്കാൻ def function എഴുതൂ."
    elif tested_functions_count == total_functions_count:
        summary = f"Tests എഴുതുന്നത് നല്ല habit ആണ് ബ്രോ. നിന്നെ pole ulla developers-ന് respect! 🔥 ({tested_functions_count}/{total_functions_count} functions tested)"
    else:
        summary = f"ബ്രോ, {total_functions_count} functions-ൽ {tested_functions_count} എണ്ണത്തിന് നമുക്ക് tests ഉണ്ടാക്കാൻ പറ്റി. ബാക്കി നീ തന്നെ എഴുതിക്കോ! 😂"

    return TestLabResult(
        functions=functions_found,
        tests=generated_tests,
        skipped=skipped,
        summary=summary
    )


def run_test_lab_tests(user_code: str, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Combines user code + generated tests into one runner script and executes it in sandbox.
    Returns structured pass/fail results per test.
    """
    if not tests:
        return {"ok": True, "results": [], "summary": "No tests to run."}

    test_codes = [t.get("code", "") for t in tests if t.get("code")]
    test_names = [t.get("test_name", "") for t in tests if t.get("test_name")]

    runner_script = user_code + "\n\n# --- AYYO TEST LAB RUNNER ---\n"
    runner_script += "\n".join(test_codes) + "\n\n"
    runner_script += "_tests_to_run = [" + ", ".join(test_names) + "]\n"
    runner_script += """
for _tf in _tests_to_run:
    _tn = _tf.__name__
    try:
        _tf()
        print(f"AYYO_TEST|PASSED|{_tn}|OK")
    except AssertionError as _e:
        print(f"AYYO_TEST|FAILED|{_tn}|AssertionError: {_e}")
    except Exception as _e:
        print(f"AYYO_TEST|FAILED|{_tn}|{type(_e).__name__}: {_e}")
"""

    res = run_code(runner_script, timeout=5)
    output = res.get("output", "")

    test_results = []
    passed_count = 0
    failed_count = 0

    for line in output.splitlines():
        if line.startswith("AYYO_TEST|"):
            parts = line.split("|", 3)
            if len(parts) >= 4:
                status = parts[1]
                tname = parts[2]
                detail = parts[3]
                is_pass = status == "PASSED"
                if is_pass:
                    passed_count += 1
                else:
                    failed_count += 1

                test_results.append({
                    "test_name": tname,
                    "status": status,
                    "passed": is_pass,
                    "detail": detail
                })

    return {
        "ok": res.get("ok", False),
        "results": test_results,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "total_count": len(test_results),
        "raw_output": output
    }
