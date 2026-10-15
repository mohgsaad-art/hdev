# STATUS: NEW (PR 2, Bob to review). the FastAPI app factory for the local UI server (Step 2).
#
# create_app() builds the app without starting a server, so fastapi.testclient.TestClient and the
# runnable entrypoint (hdev/app.py) share the exact same app. §0: this layer only serves data; all
# logic lives in Python (the registry / inputs_api), the browser is a dumb client.
#
# it does three things:
#   (a) reads HDEV_MODE once at startup (demo|real, default demo) and stores it on app.state so the
#       demo pill is server-driven, and exposes it in /api/inputs via build_inputs_payload().
#   (b) exposes GET /api/inputs returning the client-safe registry payload (no maps_to, no collapsed
#       names, no hidden fields - see hdev/inputs_api.py and tests/test_server.py).
#   (c) serves the static UI (hdev/static) at / via StaticFiles(html=True) so index.html loads at /.
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .inputs_api import build_inputs_payload, normalize_mode

# the static dir sits next to this module: hdev/static/{index.html,css,js,fonts}.
STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    # build the FastAPI app. importable without binding a socket (TestClient / entrypoint share it).
    # read the mode ONCE at startup; the UI reads it back from /api/inputs to show the demo pill.
    mode = normalize_mode(os.environ.get("HDEV_MODE"))

    app = FastAPI(title="HDEV local UI", docs_url=None, redoc_url=None)
    app.state.mode = mode

    @app.get("/api/inputs")
    def api_inputs():
        # registry-derived, client-safe inputs payload, built per-request. the mode is the startup
        # value captured on app.state.mode (read once in create_app); it is not re-read here, so
        # there is no runtime mode switching - a mode change requires restarting the app.
        return build_inputs_payload(app.state.mode)

    # serve the static UI shell at /. html=True makes GET / return static/index.html.
    # mounted last so /api/* routes take precedence. the dir is created by FEAT-002 (and a minimal
    # placeholder index.html exists so the server works today); guard against it being absent.
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    return app
