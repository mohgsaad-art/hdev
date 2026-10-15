# STATUS: NEW (PR 2, Bob to review). trivial targets for the local UI server (Step 2).
# global site-packages is read-only in the sandbox, so everything runs out of the .venv virtualenv.
.PHONY: venv run test

# create the virtualenv and install the minimal web deps (fastapi + uvicorn + httpx).
venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

# ONE start command for the local UI: binds 127.0.0.1 only, serves UI + /api/inputs from one process.
run:
	.venv/bin/python -m hdev.app

# run the full test suite (registry/slot/levers/validator from Step 1 + the Step 2 server tests).
test:
	.venv/bin/python -m pytest tests/ -q
