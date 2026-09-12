"""
Sandbox layer for AYYO.

Two walls:
  1. Block dangerous modules (os, subprocess, socket, ...).
  2. Block dangerous builtins (open, eval, exec, __import__, input, ...).

We replace `__import__` with a wrapper that checks the top-level
module name against BLOCKED_MODULES before delegating to the real one.
"""

import builtins

# ------------------------------------------------------------------
#  Modules that user code can NEVER import
# ------------------------------------------------------------------
BLOCKED_MODULES = {
    # OS / process
    "os", "sys", "subprocess", "shutil", "pty", "signal",
    "resource", "fcntl", "select", "selectors", "posix", "nt",
    "multiprocessing", "concurrent", "threading",

    # Filesystem
    "pathlib", "glob", "tempfile", "fileinput", "filecmp",

    # Serialization / deserialization (RCE vectors)
    "pickle", "marshal", "shelve", "dbm", "sqlite3",

    # Import system
    "importlib", "imp", "pkgutil", "runpy", "zipimport",

    # Introspection / runtime fiddling
    "gc", "atexit", "builtins", "__builtin__", "inspect",
    "types", "code", "codeop",

    # Network
    "socket", "ssl", "http", "urllib", "urllib2", "urllib3",
    "ftplib", "smtplib", "telnetlib", "socketserver", "asyncio",
    "requests", "httpx", "aiohttp", "websocket", "websockets",

    # Native / FFI
    "ctypes", "cffi",

    # System info
    "platform", "getpass", "pwd", "grp", "crypt",

    # GUI / browser
    "turtle", "tkinter", "webbrowser",
}


# ------------------------------------------------------------------
#  Builtins that user code can NEVER call
# ------------------------------------------------------------------
BLOCKED_BUILTINS = {
    # Code execution
    "eval", "exec", "compile", "__import__",

    # File access (public server: no disk writes/reads)
    "open", "input", "breakpoint",

    # Namespace introspection
    "globals", "locals", "vars",

    # Debugging / exit
    "help", "exit", "quit",
}


# ------------------------------------------------------------------
#  Safe import wrapper
# ------------------------------------------------------------------
def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    top = name.split(".")[0]
    if top in BLOCKED_MODULES:
        raise ImportError(
            f"Module '{top}' is not allowed inside AYYO sandbox."
        )
    return builtins.__import__(name, globals, locals, fromlist, level)


# ------------------------------------------------------------------
#  Build a fresh __builtins__ dict with our overrides
# ------------------------------------------------------------------
def safe_builtins() -> dict:
    safe = {}
    for name, value in builtins.__dict__.items():
        if name in BLOCKED_BUILTINS:
            continue
        safe[name] = value
    safe["__import__"] = safe_import
    return safe