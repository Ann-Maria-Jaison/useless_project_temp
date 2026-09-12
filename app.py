# app.py

from flask import Flask, render_template
from routes import run_bp, library_bp


def create_app():
    app = Flask(__name__)

    # simple hardening
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB request cap
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(run_bp)
    app.register_blueprint(library_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    # dev only — use gunicorn in production
    app.run(host="127.0.0.1", port=5000, debug=True)