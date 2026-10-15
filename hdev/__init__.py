# STATUS: NEW (PR 2, Bob to review). the hdev web layer package: the local UI server (Step 2).
# this package is the FIRST web layer on top of the registry/engine. it owns NO logic of its own
# beyond shaping registry data into a client-safe payload: §0 says all logic lives in Python and the
# browser is a dumb client, so everything here only reads the registry (src.registry) and serves it.
#
# public surface:
#   create_app()           -> a FastAPI app (hdev/server.py); importable without starting a server.
#   build_inputs_payload() -> the client-safe /api/inputs dict (hdev/inputs_api.py).
# the runnable entrypoint is hdev/app.py (`python -m hdev.app`), bound to 127.0.0.1 only.
from .inputs_api import build_inputs_payload
from .server import create_app

__all__ = ["create_app", "build_inputs_payload"]
