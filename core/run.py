# routes/run.py

from flask import Blueprint, request, jsonify

from core.runner import run_code, DEFAULT_TIMEOUT

bp = Blueprint("run", __name__)

MAX_CODE_BYTES = 20_000
MAX_TIMEOUT = 10


@bp.route("/run", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}

    code = data.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "empty code"}), 400

    if len(code) > MAX_CODE_BYTES:
        return jsonify({
            "error": f"code too large (max {MAX_CODE_BYTES} bytes)"
        }), 413

    # clamp timeout to server policy
    try:
        timeout = int(data.get("timeout", DEFAULT_TIMEOUT))
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT
    timeout = max(1, min(timeout, MAX_TIMEOUT))

    result = run_code(code, timeout=timeout)
    return jsonify(result)