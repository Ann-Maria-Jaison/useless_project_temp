# core/hints.py

import re
import difflib
import builtins
import sys
from .errors import AyyoTimeout


def did_you_mean(word, candidates, n=3, cutoff=0.55):
    if not word:
        return []
    filtered = [c for c in candidates
                if isinstance(c, str)
                and not c.startswith("__")
                and c != word]
    return difflib.get_close_matches(word, filtered, n=n, cutoff=cutoff)


def format_suggestions(matches):
    if not matches:
        return None
    return matches[0] if len(matches) == 1 else ", ".join(matches)


def guess_dict_from_line(code_line, namespace):
    if not code_line:
        return None
    m = re.search(r"(\w+)\s*\[", code_line)
    if not m:
        return None
    obj = namespace.get(m.group(1))
    if obj is None:
        return None
    try:
        if hasattr(obj, "keys"):
            return [str(k) for k in obj.keys()]
    except Exception:
        pass
    return None


def smart_hints(e, code_line, namespace):
    hints = []

    if isinstance(e, AyyoTimeout):
        hints.append("Problem:\n   Code execution time limit (timeout) കഴിഞ്ഞു.")
        hints.append("Likely cause:\n   Infinite loop അല്ലെങ്കിൽ വളരെ slow computation.")
        hints.append("Suggestions:\n   - while condition ശരിയാണോ?\n   - break statement ഉണ്ടോ?\n   - Loop counter update ചെയ്യുന്നുണ്ടോ?")

    if isinstance(e, NameError):
        name = getattr(e, "name", None)
        if not name:
            m = re.search(r"name '([^']+)' is not defined", str(e))
            name = m.group(1) if m else None
        if name:
            hints.append(f"Problem:\n   '{name}' was used before being defined.")
            candidates = list(namespace.keys()) + dir(builtins)
            suggestion = format_suggestions(did_you_mean(name, candidates))
            if suggestion:
                hints.append(f"Did you mean:\n   {suggestion}")
            else:
                hints.append(f"Suggested fix:\n   {name} = <value>")

    elif isinstance(e, AttributeError):
        name = getattr(e, "name", None)
        obj = getattr(e, "obj", None)
        if name is None:
            m = re.search(r"has no attribute '([^']+)'", str(e))
            name = m.group(1) if m else None
        if obj is not None and name:
            hints.append(f"Problem:\n   '{type(obj).__name__}' object-ന് '{name}' എന്ന attribute ഇല്ല.")
            try:
                suggestion = format_suggestions(did_you_mean(name, dir(obj)))
                if suggestion:
                    hints.append(f"Did you mean:\n   {suggestion}")
            except Exception:
                pass
        elif name:
            hints.append(f"Problem:\n   '{name}' എന്ന attribute കിട്ടിയില്ല.")

    elif isinstance(e, KeyError):
        key = e.args[0] if e.args else None
        if key is not None:
            hints.append(f"Problem:\n   '{key}' എന്ന key dictionary-ൽ ഇല്ല.")
            keys = guess_dict_from_line(code_line, namespace)
            if keys:
                suggestion = format_suggestions(did_you_mean(str(key), keys))
                if suggestion:
                    hints.append(f"Did you mean:\n   {suggestion}")
                else:
                    shown = ", ".join(keys[:8])
                    extra = "..." if len(keys) > 8 else ""
                    hints.append(f"Available keys:\n   {shown}{extra}")

    elif isinstance(e, ModuleNotFoundError):
        name = getattr(e, "name", None)
        if name:
            hints.append(f"Problem:\n   '{name}' module install ചെയ്തിട്ടില്ല.")
            stdlib = list(getattr(sys, "stdlib_module_names", []))
            suggestion = format_suggestions(did_you_mean(name, stdlib))
            if suggestion:
                hints.append(f"Did you mean:\n   {suggestion}")
            hints.append(f"Suggested fix:\n   pip install {name}")

    elif isinstance(e, ImportError):
        # likely from our sandbox blocking a module
        if "not allowed inside AYYO sandbox" in str(e):
            hints.append("Problem:\n   Sandbox blocked this import.")
            hints.append("Reason:\n   AYYO runs on a shared server — dangerous modules are blocked.")
            hints.append("Try:\n   Avoid os / sys / subprocess / socket for now.")

    elif isinstance(e, IndexError) and code_line:
        hints.append(f"Problem:\n   List index out of range -> {code_line.strip()}")

    elif isinstance(e, ZeroDivisionError) and code_line:
        hints.append(f"Problem:\n   Zero-division here -> {code_line.strip()}")

    elif isinstance(e, ValueError):
        m = re.search(r"invalid literal for int\(\) with base 10: '([^']*)'", str(e))
        if m:
            hints.append(f"Problem:\n   '{m.group(1)}' ഒരു number അല്ല.")

    return hints
