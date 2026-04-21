import sys

# Tracks the last seen line number so errors can reference it
_last_line = None

# Will hold the collected steps during a single run_code call
_steps = []


def _is_internal(key: str) -> bool:
    """Filter out Python internals and builtins from variable snapshots."""
    return key.startswith("__") and key.endswith("__")


def _safe_repr(value) -> str:
    """
    Convert a variable value to a JSON-safe string representation.
    Prevents crashes from non-serialisable objects (e.g. functions, modules).
    """
    try:
        # Only allow basic types through as-is; everything else becomes a string
        if isinstance(value, (int, float, bool, str, list, dict, tuple, type(None))):
            return value
        return repr(value)
    except Exception:
        return "<unrepresentable>"


def _trace(frame, event, arg):
    """
    sys.settrace callback. Called by Python on every line event inside exec().
    We only care about 'line' events — one fires each time a new line is about
    to execute.
    """
    global _last_line

    if event != "line":
        return _trace  # keep tracing, just ignore non-line events

    _last_line = frame.f_lineno

    # Snapshot local variables, filtering internals and sanitising values
    variables = {
        key: _safe_repr(val)
        for key, val in frame.f_locals.items()
        if not _is_internal(key)
    }

    _steps.append({
        "line": frame.f_lineno,
        "variables": variables,
    })

    return _trace


def run_code(code: str) -> list:
    """
    Execute `code` under the tracer and return a list of step dictionaries.

    Each successful step:  {"line": int, "variables": dict}
    An error step:         {"line": int | None, "error": str}
    """
    global _steps, _last_line
    _steps = []
    _last_line = None

    # Minimal globals — just enough for exec to work without leaking builtins
    # into variable snapshots.  We give exec a real __builtins__ so that
    # built-in functions (print, len, range …) still work inside the user code.
    exec_globals = {"__builtins__": __builtins__}
    exec_locals = {}

    sys.settrace(_trace)
    try:
        exec(compile(code, "<string>", "exec"), exec_globals, exec_locals)
    except Exception as exc:
        _steps.append({
            "line": _last_line,   # may be None if error happened before any line
            "error": str(exc),
        })
    finally:
        sys.settrace(None)

    return _steps