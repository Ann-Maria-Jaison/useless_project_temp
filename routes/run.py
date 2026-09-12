# routes/run.py

import io
from flask import Blueprint, request, jsonify, send_file

from core.runner import run_code, DEFAULT_TIMEOUT
from core.analyzer import analyze_code, analyze_code_full
from core.explainer import explain_code
from core.detective import inspect_code
from core.cleaner import clean_code
from core.personality import analyze_personality
from core.test_lab import generate_test_lab, run_test_lab_tests
from core.voice import speak_text, get_available_voices
from core.emoji_view import code_to_emoji
from core.emoji_palette import get_emoji_palette, get_quick_programs

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


@bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"issues": []})

    try:
        issues = analyze_code(code)
    except Exception:
        issues = []

    return jsonify({"issues": issues})


@bp.route("/dry-run", methods=["POST"])
def dry_run():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or not code.strip() or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": None})

    try:
        res = run_code(code, timeout=1)
        if not res.get("ok"):
            return jsonify({"error": res.get("error")})
    except Exception:
        pass

    return jsonify({"error": None})


@bp.route("/explain", methods=["POST"])
def explain():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": "invalid code"}), 400

    analysis = analyze_code_full(code)
    res = explain_code(analysis)
    return jsonify(res.to_dict())


@bp.route("/detective", methods=["POST"])
def detective():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": "invalid code"}), 400

    analysis = analyze_code_full(code)
    res = inspect_code(analysis)
    return jsonify(res.to_dict())


@bp.route("/cleaner", methods=["POST"])
def cleaner():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": "invalid code"}), 400

    analysis = analyze_code_full(code)
    res = clean_code(analysis)
    return jsonify(res.to_dict())


@bp.route("/personality", methods=["POST"])
def personality():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": "invalid code"}), 400

    analysis = analyze_code_full(code)
    res = analyze_personality(analysis)
    return jsonify(res.to_dict())


@bp.route("/test-lab", methods=["POST"])
def test_lab():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": "invalid code"}), 400

    analysis = analyze_code_full(code)
    res = generate_test_lab(analysis)
    return jsonify(res.to_dict())


@bp.route("/test-lab/run", methods=["POST"])
def test_lab_run():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    tests = data.get("tests", [])
    if not isinstance(code, str) or len(code) > MAX_CODE_BYTES:
        return jsonify({"error": "invalid code"}), 400

    res = run_test_lab_tests(code, tests)
    return jsonify(res)


@bp.route("/voices", methods=["GET"])
def get_voices():
    try:
        voices = get_available_voices()
        return jsonify({"voices": voices})
    except Exception as e:
        return jsonify({"voices": [], "error": str(e)})


@bp.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    rate = data.get("rate", 150)
    volume = data.get("volume", 100)
    voice = data.get("voice", None)

    if not text or not isinstance(text, str):
        return jsonify({"error": "text is required"}), 400

    try:
        audio_bytes = speak_text(text, rate=rate, volume=volume, voice_id=voice)
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="ayyo_speak.wav"
        )
    except Exception as e:
        return jsonify({
            "error": "Voice unavailable — pyttsx3 not working on this system",
            "detail": str(e)
        }), 500


@bp.route("/api/emoji-view", methods=["POST"])
def api_emoji_view():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    lines = code_to_emoji(code)
    return jsonify({"lines": lines})


@bp.route("/api/emoji-palette", methods=["GET"])
def api_emoji_palette():
    palette = get_emoji_palette()
    quick_programs = get_quick_programs()
    return jsonify({
        "palette": palette,
        "quick_programs": quick_programs
    })
