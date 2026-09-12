# core/runner.py

import io
import sys
import signal
import threading
import contextlib

from .sandbox import safe_builtins
from .errors import ERROR_HANDLERS, AyyoTimeout
from .hints import smart_hints

AYYO_FILENAME = "<ayyo>"
DEFAULT_TIMEOUT = 5
MAX_OUTPUT = 10_000      # chars — protects against print-spam


def _alarm_handler(signum, frame):
    raise AyyoTimeout("Code ran for too long.")


# ------------------------------------------------------------------
#  Output capture — truncates to MAX_OUTPUT characters
# ------------------------------------------------------------------
class _LimitedBuffer(io.StringIO):
    def __init__(self, limit):
        super().__init__()
        self._limit = limit
        self._truncated = False

    def write(self, s):
        if self.tell() + len(s) > self._limit:
            remaining = self._limit - self.tell()
            if remaining > 0:
                super().write(s[:remaining])
            self._truncated = True
            return len(s)
        return super().write(s)

    @property
    def truncated(self):
        return self._truncated


# ------------------------------------------------------------------
#  Main entry point
# ------------------------------------------------------------------
def run_code(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Execute user code in a sandbox.

    Returns a JSON-serializable dict:
    {
      "ok": bool,
      "output": str,
      "truncated": bool,
      "error": None | {
          "type": "NameError",
          "line": 2,
          "code": "print(y)",
          "title": "...",
          "desc":  "...",
          "tip":   "...",
          "hints": [...]
      }
    }
    """
    source_lines = code.splitlines()

    # 1. compile (SyntaxError caught here, before sandbox)
    try:
        compiled = compile(code, AYYO_FILENAME, "exec")
    except SyntaxError as se:
        return _syntax_error_result(se)

    # 2. namespace with sandboxed builtins
    user_ns = {"__builtins__": safe_builtins(), "__name__": "__ayyo__"}

    stdout_buf = _LimitedBuffer(MAX_OUTPUT)
    stderr_buf = _LimitedBuffer(MAX_OUTPUT)

    # 3. run with timeout
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            _execute_with_timeout(compiled, user_ns, timeout)
    except Exception as e:
        output = stdout_buf.getvalue()
        err = _build_error(e, source_lines, user_ns)
        return {
            "ok": False,
            "output": output,
            "truncated": stdout_buf.truncated,
            "error": err,
        }

    return {
        "ok": True,
        "output": stdout_buf.getvalue(),
        "truncated": stdout_buf.truncated,
        "error": None,
    }


# ------------------------------------------------------------------
#  Timeout handling — Unix signal, thread fallback for Windows
# ------------------------------------------------------------------
def _execute_with_timeout(compiled, user_ns, seconds):
    # Unix fast path
    if hasattr(signal, "SIGALRM") and threading.current_thread() is threading.main_thread():
        old = signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(seconds)
        try:
            exec(compiled, user_ns)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)
        return

    # Portable fallback — daemon thread
    done = {"flag": False, "err": None}

    def target():
        try:
            exec(compiled, user_ns)
        except Exception as ex:
            done["err"] = ex
        finally:
            done["flag"] = True

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(seconds)

    if not done["flag"]:
        raise AyyoTimeout("Code ran for too long.")
    if done["err"] is not None:
        raise done["err"]


# ------------------------------------------------------------------
#  Error → JSON dict
# ------------------------------------------------------------------
def _syntax_error_result(se: SyntaxError) -> dict:
    return {
        "ok": False,
        "output": "",
        "truncated": False,
        "error": {
            "type": type(se).__name__,
            "line": se.lineno,
            "code": (se.text or "").rstrip(),
            "offset": se.offset,
            "title": "Syntax error",
            "desc": se.msg,
            "tip": "Brackets, quotes, colons എല്ലാം ശരിയാണോ എന്ന് നോക്കൂ.",
            "hints": [],
        },
    }


def _get_user_frame(e):
    tb = e.__traceback__
    last = None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == AYYO_FILENAME:
            last = tb
        tb = tb.tb_next
    return last


def _build_error(e, source_lines, namespace) -> dict:
    # Friendly title/desc/tip from the table
    title, desc, tip = (
        "എന്തോ വലിയ പ്രശ്നം സംഭവിച്ചു ബ്രോ.",
        f"{type(e).__name__}: {e}",
        "Code ഒന്ന് ശരിയായി നോക്കൂ.",
    )
    for exc_type, (t, d, p) in ERROR_HANDLERS:
        if isinstance(e, exc_type):
            title, desc, tip = t, d, p
            break

    # Line + code
    lineno = None
    code_line = None
    if not isinstance(e, AyyoTimeout):
        frame = _get_user_frame(e)
        if frame:
            lineno = frame.tb_lineno
            if 0 < lineno <= len(source_lines):
                code_line = source_lines[lineno - 1]

    hints = smart_hints(e, code_line, namespace)

    return {
        "type": type(e).__name__,
        "line": lineno,
        "code": code_line.rstrip() if code_line else None,
        "title": title,
        "desc": desc,
        "tip": tip,
        "hints": hints,
    }