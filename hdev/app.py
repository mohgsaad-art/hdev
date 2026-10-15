# STATUS: NEW (PR 2, Bob to review). runnable entrypoint for the local UI server: `python -m hdev.app`.
#
# HARD RULE: bind the loopback interface (127.0.0.1) ONLY, never 0.0.0.0. this is a local tool; the
# server must not be reachable from the network. the host is a constant here, not configurable, so it
# cannot be widened by an env var. only the port is overridable (HDEV_PORT, default 8000).
#
# one start command (also wired as `make run`), documented in README.md.
import os

import uvicorn

from .server import create_app

# loopback only. do NOT change to 0.0.0.0 or expose via an env var.
HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def _port() -> int:
    # read HDEV_PORT if set, else default. a bad value falls back to the default rather than crashing.
    raw = os.environ.get("HDEV_PORT")
    if not raw:
        return DEFAULT_PORT
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_PORT


def main() -> None:
    # build the app (reads HDEV_MODE at startup) and serve it on 127.0.0.1 only.
    app = create_app()
    uvicorn.run(app, host=HOST, port=_port())


if __name__ == "__main__":
    main()
