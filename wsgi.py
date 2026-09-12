# wsgi.py — Production entrypoint for AYYO Malayalam Python Playground

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting AYYO production server on http://{host}:{port}")
    serve(app, host=host, port=port)
