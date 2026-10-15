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
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastapi import Request

from .chat_api import build_chat_payload
from .inputs_api import build_inputs_payload, normalize_mode
from .intake_api import build_intake_payload
from .run_api import build_run_payload

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

    @app.get("/api/intake")
    def api_intake():
        # DEMO-mode intake: returns the illustrative sample-case fixture plus registry+fixture-derived
        # from_data/standard/missing tallies, through the §8 chokepoint (hdev/intake_api.py). no AI
        # provider is called and nothing hits the network - it only reads demo/sample_case/.
        # the mode is the startup value on app.state.mode (read once in create_app). in real mode the
        # payload is {"available": false, ...} with a 404 so the demo fixture never leaks.
        payload = build_intake_payload(app.state.mode)
        if not payload.get("available", False):
            return JSONResponse(status_code=404, content=payload)
        return payload

    @app.post("/api/run")
    async def api_run(request: Request):
        # DEMO-mode scenario run: validate the levers and return the §3.3 illustrative results JSON
        # through the pure chokepoint (hdev/run_api.py). the mode is the startup value on
        # app.state.mode (read once in create_app). in real mode the chokepoint returns
        # {"available": false, ...} with a 404 (the real runner is Step 9) and demo_engine is NOT
        # called. a lever the validator rejects comes back as a 400 with a plain-language error and no
        # results. nothing hits the network and no AI provider is involved.
        try:
            body = await request.json()
        except Exception:
            body = {}
        if not isinstance(body, dict):
            body = {}
        status, payload = build_run_payload(app.state.mode, body)
        return JSONResponse(status_code=status, content=payload)

    @app.post("/api/chat")
    async def api_chat(request: Request):
        # DEMO-mode assistant turn: the §4.4 suggestion buttons, the server-side typed-question keyword
        # router and the shift-end field-edit rerun, all answered by explain/ templates through the
        # pure chokepoint (hdev/chat_api.py). the mode is the startup value on app.state.mode (read
        # once in create_app). in real mode the chokepoint returns {"available": false, ...} with a 404
        # (the real LLM assistant is Step 10) and NO AI provider is imported or called. every reply is
        # passed through the §4.3 number-check inside the chokepoint. nothing hits the network.
        try:
            body = await request.json()
        except Exception:
            body = {}
        if not isinstance(body, dict):
            body = {}
        status, payload = build_chat_payload(app.state.mode, body)
        return JSONResponse(status_code=status, content=payload)

    # serve the static UI shell at /. html=True makes GET / return static/index.html.
    # mounted last so /api/* routes take precedence. the dir is created by FEAT-002 (and a minimal
    # placeholder index.html exists so the server works today); guard against it being absent.
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    return app
