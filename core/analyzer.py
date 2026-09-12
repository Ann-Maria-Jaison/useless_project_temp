# core/analyzer.py

import ast
import re
import builtins
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from .errors import ERROR_HANDLERS, AyyoTimeout
from .hints import smart_hints, did_you_mean, format_suggestions
from .runner import run_code


@dataclass
class Issue:
    severity: str          # "ERROR" | "WARNING" | "INFO"
    line: Optional[int]
    col: Optional[int]
    type: str              # e.g. "NameError", "UnusedVariable"
    code: Optional[str]
    title: str             # Malayalam title
    desc: str              # Malayalam description
    tip: str               # Malayalam tip / suggestion
    hints: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CodeAnalysis:
    source: str
    tree: Optional[ast.AST]
    variables: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    loops: List[Dict[str, Any]]
    conditions: List[Dict[str, Any]]
    imports: List[Dict[str, Any]]
    calls: List[Dict[str, Any]]
    issues: List[Issue]
    metrics: Dict[str, Any]
    syntax_error: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("tree", None)  # AST not JSON serializable directly
        return d


# Common stdlib functions/constants used without import
COMMON_STD_IMPORTS = {
    "sqrt": ("math", "from math import sqrt"),
    "ceil": ("math", "from math import ceil"),
    "floor": ("math", "from math import floor"),
    "pow": ("math", "from math import pow"),
    "sin": ("math", "from math import sin"),
    "cos": ("math", "from math import cos"),
    "tan": ("math", "from math import tan"),
    "pi": ("math", "from math import pi"),
    "e": ("math", "from math import e"),
    "radians": ("math", "from math import radians"),
    "degrees": ("math", "from math import degrees"),
    "factorial": ("math", "from math import factorial"),
    "gcd": ("math", "from math import gcd"),

    "argv": ("sys", "import sys"),
    "exit": ("sys", "import sys"),

    "environ": ("os", "import os"),
    "getcwd": ("os", "import os"),
    "listdir": ("os", "import os"),

    "search": ("re", "import re"),
    "match": ("re", "import re"),
    "sub": ("re", "import re"),
    "findall": ("re", "import re"),

    "dumps": ("json", "import json"),
    "loads": ("json", "import json"),

    "randint": ("random", "import random"),
    "choice": ("random", "import random"),
    "shuffle": ("random", "import shuffle"),

    "datetime": ("datetime", "from datetime import datetime"),
    "date": ("datetime", "from datetime import date"),
    "timedelta": ("datetime", "from datetime import timedelta"),

    "sleep": ("time", "import time"),

    "Counter": ("collections", "from collections import Counter"),
    "defaultdict": ("collections", "from collections import defaultdict"),
    "deque": ("collections", "from collections import deque"),
    "namedtuple": ("collections", "from collections import namedtuple"),
}

BUILTIN_REASSIGN_TARGETS = {
    "list", "str", "int", "float", "dict", "set", "tuple",
    "sum", "max", "min", "type", "input", "open", "range",
    "len", "abs", "all", "any"
}

BUILTIN_NAMES = set(dir(builtins))


def analyze_code_full(code: str) -> CodeAnalysis:
    """
    Shared analysis engine. Parses AST, extracts structures, calculates complexity metrics,
    and returns a comprehensive CodeAnalysis dataclass object.
    """
    source_lines = code.splitlines() if isinstance(code, str) else []
    line_count = len(source_lines)
    comment_lines = sum(1 for line in source_lines if line.strip().startswith("#"))
    blank_lines = sum(1 for line in source_lines if not line.strip())
    code_lines = line_count - comment_lines - blank_lines

    empty_metrics = {
        "line_count": line_count,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
        "max_nesting_depth": 0,
        "function_count": 0,
        "class_count": 0,
        "loop_count": 0,
        "condition_count": 0,
        "variable_count": 0,
        "import_count": 0,
        "call_count": 0,
    }

    if not isinstance(code, str) or not code.strip():
        return CodeAnalysis(
            source=code or "",
            tree=None,
            variables=[],
            functions=[],
            classes=[],
            loops=[],
            conditions=[],
            imports=[],
            calls=[],
            issues=[],
            metrics=empty_metrics,
            syntax_error=None
        )

    # 1. AST Parsing & Syntax Error Check
    try:
        tree = ast.parse(code, filename="<ayyo>")
        syntax_err = None
    except SyntaxError as se:
        syn_issue_dict = _build_syntax_issue(se, source_lines)
        syn_issue = Issue(
            severity=syn_issue_dict["severity"],
            line=syn_issue_dict["line"],
            col=syn_issue_dict["col"],
            type=syn_issue_dict["type"],
            code=syn_issue_dict["code"],
            title=syn_issue_dict["title"],
            desc=syn_issue_dict["desc"],
            tip=syn_issue_dict["tip"],
            hints=syn_issue_dict["hints"]
        )
        return CodeAnalysis(
            source=code,
            tree=None,
            variables=[],
            functions=[],
            classes=[],
            loops=[],
            conditions=[],
            imports=[],
            calls=[],
            issues=[syn_issue],
            metrics=empty_metrics,
            syntax_error=syn_issue_dict
        )

    # 2. AST Visitor & Structure Extraction
    visitor = AyyoASTVisitor(source_lines)
    try:
        visitor.visit(tree)
    except Exception:
        pass

    # Calculate max nesting depth
    max_depth = _compute_max_nesting_depth(tree)

    metrics = {
        "line_count": line_count,
        "code_lines": max(0, code_lines),
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
        "max_nesting_depth": max_depth,
        "function_count": len(visitor.functions),
        "class_count": len(visitor.classes),
        "loop_count": len(visitor.loops),
        "condition_count": len(visitor.conditions),
        "variable_count": len(visitor.variables),
        "import_count": len(visitor.imports),
        "call_count": len(visitor.calls),
    }

    # 3. Dry-run in Sandbox (if no static blocking errors found)
    issues = list(visitor.issues)
    has_blocking_errors = any(i.severity == "ERROR" for i in issues)
    if not has_blocking_errors:
        try:
            res = run_code(code, timeout=1)
            if not res.get("ok") and res.get("error"):
                err = res["error"]
                err_line = err.get("line")
                err_type = err.get("type")
                already_caught = any(
                    i.line == err_line and (i.type == err_type or i.type == "MissingImport")
                    for i in issues
                )
                if not already_caught:
                    issues.append(Issue(
                        severity="ERROR",
                        line=err_line or 1,
                        col=1,
                        type=err_type or "RuntimeError",
                        code=err.get("code"),
                        title=err.get("title") or "Runtime Error",
                        desc=err.get("desc") or "",
                        tip=err.get("tip") or "",
                        hints=err.get("hints") or []
                    ))
        except Exception:
            pass

    # Sort issues by line number then column
    issues.sort(key=lambda x: (x.line or 1, x.col or 1))

    return CodeAnalysis(
        source=code,
        tree=tree,
        variables=visitor.variables,
        functions=visitor.functions,
        classes=visitor.classes,
        loops=visitor.loops,
        conditions=visitor.conditions,
        imports=visitor.imports,
        calls=visitor.calls,
        issues=issues,
        metrics=metrics,
        syntax_error=syntax_err
    )


def analyze_code(code: str) -> List[Dict[str, Any]]:
    """
    Backward-compatible wrapper. Returns a list of issue dicts.
    """
    analysis = analyze_code_full(code)
    return [i.to_dict() for i in analysis.issues]


def _build_syntax_issue(se: SyntaxError, source_lines: List[str]) -> Dict[str, Any]:
    lineno = se.lineno or 1
    col = se.offset or 1
    code_line = (se.text or "").rstrip()
    if not code_line and 0 < lineno <= len(source_lines):
        code_line = source_lines[lineno - 1]

    msg = str(se.msg or se)
    title = "ബ്രോ... syntax ഒന്ന് ശരിയാക്ക്."
    desc = msg
    tip = "Brackets, quotes, colons എല്ലാം ശരിയാണോ എന്ന് നോക്കൂ."
    hints = []

    if "return" in msg.lower() and "outside" in msg.lower():
        title = "Return function-ന് പുറത്ത് ഉപയോഗിക്കാൻ പറ്റില്ല ബ്രോ."
        tip = "Return statement ഒരു function-നുള്ളിൽ മാത്രമേ ഉപയോഗിക്കാൻ പറ്റൂ."
        hints.append("Suggested fix:\n   def my_func():\n       return ...")
    elif "break" in msg.lower() and "outside" in msg.lower():
        title = "Break loop-ന് പുറത്ത് പാടില്ല ബ്രോ."
        tip = "Break statement for അല്ലെങ്കിൽ while loop-നുള്ളിൽ മാത്രം ഉപയോഗിക്കൂ."
    elif "continue" in msg.lower() and "outside" in msg.lower():
        title = "Continue loop-ന് പുറത്ത് പാടില്ല ബ്രോ."
        tip = "Continue statement for അല്ലെങ്കിൽ while loop-നുള്ളിൽ മാത്രം ഉപയോഗിക്കൂ."
    elif isinstance(se, IndentationError):
        title = "Indentation ശരിയല്ല ബ്രോ."
        tip = "Spaces-ഉം tabs-ഉം മിക്സ് ചെയ്യാതെ ഒരേ indentation ഉപയോഗിക്കൂ."
    elif code_line and re.search(r"\b(if|while|elif)\b.*=", code_line) and not re.search(r"==|<=|>=|!=", code_line):
        title = "If/While condition-ൽ '=' അല്ല, '==' വേണം ബ്രോ."
        tip = "Assignment (=) അല്ല, comparison (==) ആണ് ഉപയോഗിക്കേണ്ടത്."
        hints.append("Did you mean:\n   if x == 5:")

    return {
        "severity": "ERROR",
        "line": lineno,
        "col": col,
        "type": type(se).__name__,
        "code": code_line,
        "title": title,
        "desc": desc,
        "tip": tip,
        "hints": hints
    }


def _compute_max_nesting_depth(node: ast.AST, current_depth: int = 0) -> int:
    max_d = current_depth
    nesting_nodes = (ast.For, ast.While, ast.If, ast.With, ast.Try, ast.FunctionDef, ast.ClassDef)

    for child in ast.iter_child_nodes(node):
        if isinstance(child, nesting_nodes):
            max_d = max(max_d, _compute_max_nesting_depth(child, current_depth + 1))
        else:
            max_d = max(max_d, _compute_max_nesting_depth(child, current_depth))
    return max_d


class AyyoASTVisitor(ast.NodeVisitor):
    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.issues: List[Issue] = []

        self.defined_names: set = set(BUILTIN_NAMES)
        self.used_names: Dict[str, List[ast.Name]] = {}
        self.assigned_names: Dict[str, ast.Name] = {}
        self.imported_names: Dict[str, ast.AST] = {}
        self.inferred_types: Dict[str, str] = {}

        self.variables: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[Dict[str, Any]] = []
        self.loops: List[Dict[str, Any]] = []
        self.conditions: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []
        self.calls: List[Dict[str, Any]] = []

    def _get_line(self, lineno: int) -> str:
        if 0 < lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1]
        return ""

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.asname or alias.name
            self.defined_names.add(name)
            self.imported_names[name] = node
            self.imports.append({
                "module": alias.name,
                "name": name,
                "alias": alias.asname,
                "line": node.lineno,
                "is_used": False
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        for alias in node.names:
            name = alias.asname or alias.name
            self.defined_names.add(name)
            self.imported_names[name] = node
            self.imports.append({
                "module": mod,
                "name": name,
                "alias": alias.asname,
                "line": node.lineno,
                "is_used": False
            })
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.defined_names.add(node.name)
        args_list = [a.arg for a in node.args.args]
        docstring = ast.get_docstring(node) or ""

        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "col": node.col_offset + 1,
            "args": args_list,
            "returns": bool(node.returns),
            "is_called": False,
            "docstring": docstring,
            "body_len": len(node.body)
        })

        # Empty function check
        if len(node.body) == 1 and isinstance(node.body[0], (ast.Pass, ast.Expr)) and isinstance(getattr(node.body[0], 'value', None), ast.Constant):
            code_line = self._get_line(node.lineno)
            self.issues.append(Issue(
                severity="INFO",
                line=node.lineno,
                col=node.col_offset + 1,
                type="EmptyFunction",
                code=code_line,
                title=f"Function '{node.name}' ശൂന്യമാണ് ബ്രോ.",
                desc=f"Function '{node.name}' body-ൽ അർത്ഥവത്തായ കോഡ് ഒന്നും കാണുന്നില്ല.",
                tip="Code അല്ലെങ്കിൽ pass ചേർക്കൂ.",
                hints=[]
            ))

        # Check for mutable default args
        for arg in node.args.defaults + node.args.kw_defaults:
            if arg and isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                code_line = self._get_line(arg.lineno)
                self.issues.append(Issue(
                    severity="WARNING",
                    line=arg.lineno,
                    col=arg.col_offset + 1,
                    type="MutableDefaultArgument",
                    code=code_line,
                    title="Function default argument-ൽ mutable list/dict ഉപയോഗിക്കരുത്.",
                    desc=f"Function '{node.name}' default value ആയി list/dict/set ഉപയോഗിച്ചിട്ടുണ്ട്.",
                    tip="Default value None ആക്കി function-നുള്ളിൽ initialize ചെയ്യൂ (if x is None: x = []).",
                    hints=[f"Suggested fix:\n   def {node.name}(..., x=None):\n       if x is None: x = []"]
                ))

        for arg in node.args.args + node.args.kwonlyargs:
            self.defined_names.add(arg.arg)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.defined_names.add(node.name)
        bases_list = [b.id for b in node.bases if isinstance(b, ast.Name)]
        self.classes.append({
            "name": node.name,
            "line": node.lineno,
            "col": node.col_offset + 1,
            "bases": bases_list,
            "methods_count": sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        })
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        target_name = node.target.id if isinstance(node.target, ast.Name) else "item"
        iter_name = node.iter.id if isinstance(node.iter, ast.Name) else "iterable"
        self.loops.append({
            "kind": "for",
            "line": node.lineno,
            "col": node.col_offset + 1,
            "target": target_name,
            "iter_expr": iter_name
        })
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.loops.append({
            "kind": "while",
            "line": node.lineno,
            "col": node.col_offset + 1,
            "target": None,
            "iter_expr": "condition"
        })
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        code_line = self._get_line(node.lineno)
        self.conditions.append({
            "line": node.lineno,
            "col": node.col_offset + 1,
            "test_code": code_line.strip()
        })
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        val_type = None
        val_repr = None
        if isinstance(node.value, ast.Constant):
            val_type = type(node.value.value).__name__
            val_repr = repr(node.value.value)
        elif isinstance(node.value, ast.List):
            val_type = "list"
            val_repr = "list"
        elif isinstance(node.value, ast.Dict):
            val_type = "dict"
            val_repr = "dict"

        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                self.defined_names.add(name)
                self.assigned_names[name] = target
                if val_type:
                    self.inferred_types[name] = val_type

                self.variables.append({
                    "name": name,
                    "line": node.lineno,
                    "col": target.col_offset + 1,
                    "value_repr": val_repr or "expression",
                    "is_used": False
                })

                # Rule: Reassignment of builtins
                if name in BUILTIN_REASSIGN_TARGETS:
                    code_line = self._get_line(node.lineno)
                    self.issues.append(Issue(
                        severity="WARNING",
                        line=node.lineno,
                        col=target.col_offset + 1,
                        type="ShadowedBuiltin",
                        code=code_line,
                        title=f"Builtin name '{name}' overwrite ചെയ്തു ബ്രോ.",
                        desc=f"Python builtin function/type '{name}' variable name ആയി ഉപയോഗിക്കരുത്.",
                        tip=f"Variable name മാറ്റൂ (ഉദാഹരണത്തിന് {name}_val).",
                        hints=[f"Suggested fix:\n   {name}_val = ..."]
                    ))

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            self.defined_names.add(node.id)
            if node.id not in self.assigned_names:
                self.assigned_names[node.id] = node
        elif isinstance(node.ctx, ast.Load):
            self.used_names.setdefault(node.id, []).append(node)
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        for handler in node.handlers:
            if handler.type is None:
                code_line = self._get_line(handler.lineno)
                self.issues.append(Issue(
                    severity="WARNING",
                    line=handler.lineno,
                    col=handler.col_offset + 1,
                    type="BareExcept",
                    code=code_line,
                    title="Bare 'except:' ഉപയോഗിക്കരുത് ബ്രോ.",
                    desc="എല്ലാ errors-ഉം catch ചെയ്യുന്നത് dangerous ആണ്.",
                    tip="'except Exception:' അല്ലെങ്കിൽ specific error name ഉപയോഗിക്കൂ.",
                    hints=["Suggested fix:\n   except Exception as e:"]
                ))
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                code_line = self._get_line(handler.lineno)
                self.issues.append(Issue(
                    severity="WARNING",
                    line=handler.lineno,
                    col=handler.col_offset + 1,
                    type="SilentException",
                    code=code_line,
                    title="Error കണ്ട് കാണാതെ പോകരുത് ബ്രോ.",
                    desc="Exception catch ചെയ്ത് 'pass' കൊടുക്കുന്നത് bugs മറച്ചുവെക്കും.",
                    tip="At least error print ചെയ്യുകയോ log ചെയ്യുകയോ ചെയ്യൂ.",
                    hints=[]
                ))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name:
            self.calls.append({
                "func_name": func_name,
                "line": node.lineno,
                "col": node.col_offset + 1,
                "args_count": len(node.args) + len(node.keywords)
            })

            # Check calling non-callable variable
            if func_name in self.inferred_types and self.inferred_types[func_name] in ("int", "float", "str", "list", "dict"):
                tname = self.inferred_types[func_name]
                code_line = self._get_line(node.lineno)
                self.issues.append(Issue(
                    severity="ERROR",
                    line=node.lineno,
                    col=node.col_offset + 1,
                    type="TypeError",
                    code=code_line,
                    title=f"'{func_name}' call ചെയ്യാൻ പറ്റില്ല ബ്രോ.",
                    desc=f"'{func_name}' ഒരു {tname} ആണ്, function അല്ല.",
                    tip="Function-ന്റെ പേരിലാണോ variable ഉണ്ടാക്കിയത് എന്ന് നോക്കൂ.",
                    hints=[]
                ))

        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict):
        seen_keys = set()
        for k in node.keys:
            if k is not None:
                key_val = None
                if isinstance(k, ast.Constant):
                    key_val = repr(k.value)
                elif isinstance(k, ast.Name):
                    key_val = k.id

                if key_val is not None:
                    if key_val in seen_keys:
                        code_line = self._get_line(k.lineno)
                        self.issues.append(Issue(
                            severity="WARNING",
                            line=k.lineno,
                            col=k.col_offset + 1,
                            type="DuplicateDictKey",
                            code=code_line,
                            title=f"Dictionary-ൽ {key_val} രണ്ട് തവണ വന്നിട്ടുണ്ട്.",
                            desc="Duplicate key കൊടുത്താൽ രണ്ടാമത്തെ value ആദ്യത്തേതിനെ overwrite ചെയ്യും.",
                            tip="Duplicate key ഒഴിവാക്കൂ.",
                            hints=[]
                        ))
                    else:
                        seen_keys.add(key_val)
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr):
        has_placeholder = any(isinstance(val, ast.FormattedValue) for val in node.values)
        if not has_placeholder:
            code_line = self._get_line(node.lineno)
            self.issues.append(Issue(
                severity="WARNING",
                line=node.lineno,
                col=node.col_offset + 1,
                type="FStringWithoutPlaceholders",
                code=code_line,
                title="f-string-ൽ variables ഒന്നുമില്ല ബ്രോ.",
                desc="Placeholders ({}) ഇല്ലാത്ത f-string ആവശ്യമില്ല.",
                tip="സാധാരണ string ('...') ഉപയോഗിക്കാം.",
                hints=[]
            ))
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        if len(node.comparators) == 1:
            left = node.left
            right = node.comparators[0]
            left_is_str = isinstance(left, ast.Constant) and isinstance(left.value, str)
            right_is_num = isinstance(right, ast.Constant) and isinstance(right.value, (int, float))
            left_is_num = isinstance(left, ast.Constant) and isinstance(left.value, (int, float))
            right_is_str = isinstance(right, ast.Constant) and isinstance(right.value, str)

            if (left_is_str and right_is_num) or (left_is_num and right_is_str):
                code_line = self._get_line(node.lineno)
                self.issues.append(Issue(
                    severity="WARNING",
                    line=node.lineno,
                    col=node.col_offset + 1,
                    type="TypeError",
                    code=code_line,
                    title="String-ഉം Number-ഉം compare ചെയ്യാൻ നോക്കിയല്ലേ.",
                    desc="String-ഉം number-ഉം തമ്മിൽ compare ചെയ്യുന്നത് unexpected results തരും.",
                    tip="Type cast ചെയ്യൂ (int(...) അല്ലെങ്കിൽ str(...)).",
                    hints=[]
                ))
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module):
        self.generic_visit(node)

        # Mark imported names as used
        for imp in self.imports:
            if imp["name"] in self.used_names:
                imp["is_used"] = True

        # Mark variables as used
        for var in self.variables:
            if var["name"] in self.used_names:
                var["is_used"] = True

        # Mark functions as called
        called_names = {c["func_name"] for c in self.calls}
        for fn in self.functions:
            if fn["name"] in called_names:
                fn["is_called"] = True

        # Check Undefined Names
        for name, nodes in self.used_names.items():
            if name not in self.defined_names:
                first_node = nodes[0]
                code_line = self._get_line(first_node.lineno)

                if name in COMMON_STD_IMPORTS:
                    mod, fix_stmt = COMMON_STD_IMPORTS[name]
                    self.issues.append(Issue(
                        severity="WARNING",
                        line=first_node.lineno,
                        col=first_node.col_offset + 1,
                        type="MissingImport",
                        code=code_line,
                        title=f"'{name}' import ചെയ്തിട്ടില്ല ബ്രോ.",
                        desc=f"'{name}' ഉപയോഗിക്കുന്നതിന് മുൻപ് module import ചെയ്യണം.",
                        tip=f"Code-ന്റെ മുകളിൽ '{fix_stmt}' ചേർക്കൂ.",
                        hints=[f"Suggested fix:\n   {fix_stmt}"]
                    ))
                else:
                    candidates = list(self.defined_names) + list(COMMON_STD_IMPORTS.keys())
                    matches = did_you_mean(name, candidates)
                    suggestion = format_suggestions(matches)

                    hints = []
                    if suggestion:
                        hints.append(f"Did you mean:\n   {suggestion}")
                    else:
                        hints.append(f"Suggested fix:\n   {name} = <value>")

                    self.issues.append(Issue(
                        severity="ERROR",
                        line=first_node.lineno,
                        col=first_node.col_offset + 1,
                        type="NameError",
                        code=code_line,
                        title="ബ്രോ, ഈ variable ആരാടാ?",
                        desc=f"'{name}' was used before being defined.",
                        tip="Variable name ശരിയാണോ എന്ന് check ചെയ്യൂ.",
                        hints=hints
                    ))

        # Check Unused Variables
        for name, node in self.assigned_names.items():
            if not name.startswith("_") and name not in self.used_names and name not in BUILTIN_NAMES:
                code_line = self._get_line(node.lineno)
                self.issues.append(Issue(
                    severity="WARNING",
                    line=node.lineno,
                    col=node.col_offset + 1,
                    type="UnusedVariable",
                    code=code_line,
                    title=f"'{name}' വച്ചൊണ്ട് ഒരു കാര്യവുമില്ല ബ്രോ.",
                    desc=f"Variable '{name}' assign ചെയ്തു, പക്ഷെ എവിടെയും ഉപയോഗിച്ചില്ല.",
                    tip="ആവശ്യമില്ലെങ്കിൽ ഈ variable ഒഴിവാക്കാം.",
                    hints=[]
                ))

        # Check Unused Imports
        for name, node in self.imported_names.items():
            if name not in self.used_names:
                lineno = getattr(node, "lineno", 1)
                col = getattr(node, "col_offset", 0) + 1
                code_line = self._get_line(lineno)
                self.issues.append(Issue(
                    severity="WARNING",
                    line=lineno,
                    col=col,
                    type="UnusedImport",
                    code=code_line,
                    title=f"'{name}' വെറുതെ import ചെയ്തതാണ്.",
                    desc=f"Module '{name}' import ചെയ്തു, പക്ഷെ ഉപയോഗിച്ചില്ല.",
                    tip="Unused imports ഒഴിവാക്കുന്നത് code clean ആക്കും.",
                    hints=[]
                ))

        # Check Functions defined but never called
        for fn in self.functions:
            if not fn["is_called"] and not fn["name"].startswith("_"):
                code_line = self._get_line(fn["line"])
                self.issues.append(Issue(
                    severity="WARNING",
                    line=fn["line"],
                    col=fn["col"],
                    type="UncalledFunction",
                    code=code_line,
                    title=f"Function '{fn['name']}()' ഉണ്ടാക്കി, പക്ഷെ എവിടെയും വിളിച്ചില്ല.",
                    desc=f"Function '{fn['name']}' define ചെയ്തിട്ടുണ്ട്, പക്ഷെ call ചെയ്തിട്ടില്ല.",
                    tip=f"Code-ൽ {fn['name']}() എന്ന് ചേർത്ത് വിളിച്ച് നോക്കൂ.",
                    hints=[f"Suggested fix:\n   {fn['name']}()"]
                ))
