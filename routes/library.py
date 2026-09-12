# routes/library.py — Blueprint for AYYO Emoji Code Library page and API

from flask import Blueprint, render_template, request, jsonify
from core.emoji_library import get_all_concepts, search_concepts

library_bp = Blueprint("library", __name__)


@library_bp.route("/library", methods=["GET"])
def library_page():
    return render_template("library.html")


@library_bp.route("/api/library", methods=["GET"])
def api_library():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    concepts = search_concepts(query, category)
    return jsonify({
        "concepts": [c.to_dict() for c in concepts],
        "count": len(concepts)
    })
