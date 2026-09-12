def to_json(error, code_line, lineno, hints):
    return {
        "error_type": type(error).__name__,
        "line": lineno,
        "code": code_line,
        "title": "ബ്രോ, ഈ variable ആരാടാ?",
        "problem": "'y' was used before being defined.",
        "suggestion": "y = <value>",
        "hints": [...]
    }