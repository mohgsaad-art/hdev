# STATUS: NEW (PR 7, Bob to review). the server-side PROJECT STORE for Step 7 (scenarios + audit + run log).
#
# this is the ONE place that holds the mutable project state the demo flow accumulates across requests:
#   - `run_counter`  : a monotonic integer. EVERY successful demo run (scenario-bar /api/run, an
#                      assistant rerun, a shift-end edit) draws the next N from here so the audit trail
#                      numbers are consistent. this replaces the module-level itertools.count that used
#                      to live in hdev/chat_api.py.
#   - `run_log`      : an APPEND-ONLY list of §3.4 run-log entries (newest-last on disk; listing returns
#                      newest-first). audit/run_log.py owns the §8-safe SHAPE of each entry; this module
#                      only persists them.
#   - `scenarios`    : the saved scenarios list (name + the client-facing settings/key-result summary).
#   - `inputs`       : a minimal snapshot of the current inputs (in demo this stays small - the intake
#                      tallies are derived live by audit.sources, so this is kept for completeness).
#   - `client_data`  : (Step 10 data guard) a boolean, DEFAULT TRUE. it marks whether the project holds
#                      a client's operational data. the real-mode AI path reads it before any outbound
#                      call: the free-tier Gemini backend is REFUSED for a client-data project unless an
#                      explicit opt-in / paid flag is set (ai.check_data_guard). a project is assumed to
#                      hold client data until proven otherwise, so the default is true (conservative).
#
# §0: all logic lives in Python; the browser is a dumb client. this module makes NO network call and
# imports NO AI provider - it only reads/writes one JSON file on a gitignored runtime path.
#
# PERSISTENCE: one JSON file at a gitignored runtime path. default repo-root/.hdev_runtime/project.json;
# override with env HDEV_PROJECT_STORE (an absolute or relative file path). the directory is created
# lazily on the first write, so importing this module never touches the filesystem. writes are atomic
# (write to a temp file in the same dir, then os.replace) so a crash never leaves a half-written file.
#
# TEST ISOLATION: the store is a process-level singleton keyed by the RESOLVED path. tests build a
# fresh TestClient(create_app()) per test and expect run numbering to start at 1; create_app() calls
# reset_for_tests() in demo mode so each test starts from a clean in-memory store AND a clean file
# (the runtime file is removed on reset). reset_for_tests() is also callable directly from a test.
import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

# repo root is one parent up from hdev/.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_STORE = _REPO_ROOT / ".hdev_runtime" / "project.json"

# the env var that overrides the store path (documented in the README and .gitignore).
_ENV_STORE = "HDEV_PROJECT_STORE"

# a module-level lock so concurrent requests (uvicorn worker threads) never corrupt the file. the demo
# is single-user and single-worker, but the lock keeps the atomic read-modify-write honest.
_LOCK = threading.RLock()

# the in-memory singletons, keyed by resolved path string, so a test that overrides HDEV_PROJECT_STORE
# gets its own store and the default-path store is reused across requests within one process.
_STORES: Dict[str, "ProjectStore"] = {}


def _resolve_path() -> Path:
    # resolve the store file path from the env var (if set) else the default. relative paths resolve
    # against the repo root so `HDEV_PROJECT_STORE=foo.json` lands under the repo, not the CWD.
    raw = os.environ.get(_ENV_STORE)
    if raw:
        p = Path(raw)
        if not p.is_absolute():
            p = _REPO_ROOT / p
        return p
    return _DEFAULT_STORE


def _empty_state() -> Dict[str, Any]:
    # the empty project shape persisted to disk. kept intentionally small and JSON-serialisable.
    return {
        "inputs": {},          # minimal current-inputs snapshot (demo keeps this small)
        "run_counter": 0,      # last allocated run number; next_run_number() returns counter+1
        "run_log": [],         # append-only §3.4 entries, newest-LAST on disk
        "scenarios": [],       # saved scenarios (name + client-facing summary + run_id)
        "client_data": True,   # Step 10 data guard: default TRUE (assume client data until told otherwise)
    }


class ProjectStore:
    # a thin JSON-file-backed store. load() reads the file (or starts empty), save() writes atomically.
    # the public helpers (next_run_number / append_run / list_runs / save_scenario / list_scenarios /
    # get_run) each take the lock and persist, so callers never juggle files themselves.
    def __init__(self, path: Path):
        self._path = path
        self._state = self._read()

    # ---- low-level file i/o ------------------------------------------------
    def _read(self) -> Dict[str, Any]:
        # read the JSON file if it exists; otherwise start from an empty state. a corrupt/unreadable
        # file is treated as empty (the demo state is disposable runtime data, never source of truth).
        try:
            with self._path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                # merge over the empty shape so a partial file still has every key.
                state = _empty_state()
                state.update({k: data[k] for k in state.keys() if k in data})
                return state
        except (OSError, ValueError):
            pass
        return _empty_state()

    def _write(self) -> None:
        # atomic write: temp file in the same directory, then os.replace. the directory is created lazily
        # here (on the FIRST write) so merely importing/constructing the store never writes to disk.
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self._path.parent), prefix=".project-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._state, fh, ensure_ascii=False, indent=2)
            os.replace(tmp, self._path)
        finally:
            # if os.replace already moved the temp file this is a no-op; otherwise clean it up.
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    # ---- public API --------------------------------------------------------
    def load(self) -> Dict[str, Any]:
        # a deep-ish copy of the current state (so callers cannot mutate the store in place).
        with _LOCK:
            return json.loads(json.dumps(self._state))

    def save(self) -> None:
        # persist the current in-memory state to disk atomically.
        with _LOCK:
            self._write()

    def next_run_number(self) -> int:
        # increment and persist the shared monotonic counter, returning the new N (starts at 1).
        with _LOCK:
            self._state["run_counter"] = int(self._state.get("run_counter", 0)) + 1
            self._write()
            return self._state["run_counter"]

    def append_run(self, entry: Mapping[str, Any]) -> None:
        # append a §3.4 run-log entry (append-only; newest-LAST on disk). the SHAPE is the caller's
        # responsibility (audit/run_log.build_run_entry); this only persists.
        with _LOCK:
            self._state["run_log"].append(dict(entry))
            self._write()

    def latest_run(self) -> Optional[Dict[str, Any]]:
        # the most recently appended run-log entry (newest), or None when the log is empty. used by the
        # run-entry builder to compute the plain-word diff against the previous run.
        with _LOCK:
            log = self._state.get("run_log") or []
            return json.loads(json.dumps(log[-1])) if log else None

    def list_runs(self) -> List[Dict[str, Any]]:
        # a NEWEST-FIRST copy of the run log for the audit UI.
        with _LOCK:
            log = self._state.get("run_log") or []
            return json.loads(json.dumps(list(reversed(log))))

    def get_run(self, run_id: Any) -> Optional[Dict[str, Any]]:
        # find a run-log entry by its run_id (the numeric run number). returns a copy or None.
        with _LOCK:
            for entry in self._state.get("run_log") or []:
                if entry.get("run_id") == run_id:
                    return json.loads(json.dumps(entry))
            return None

    def save_scenario(self, scenario: Mapping[str, Any]) -> Dict[str, Any]:
        # append a saved scenario (name + client-facing summary + the run_id it came from) and persist.
        # returns a copy of the stored scenario.
        with _LOCK:
            stored = dict(scenario)
            self._state["scenarios"].append(stored)
            self._write()
            return json.loads(json.dumps(stored))

    def list_scenarios(self) -> List[Dict[str, Any]]:
        # a copy of the saved scenarios in save order (oldest-first; the UI table shows them in rows).
        with _LOCK:
            return json.loads(json.dumps(list(self._state.get("scenarios") or [])))

    def set_inputs(self, inputs: Mapping[str, Any]) -> None:
        # store a minimal current-inputs snapshot (kept small in demo). persisted for completeness.
        with _LOCK:
            self._state["inputs"] = json.loads(json.dumps(dict(inputs)))
            self._write()

    def get_client_data(self) -> bool:
        # the Step 10 data-guard flag. DEFAULT TRUE: a project is assumed to hold client data unless a
        # stored value says otherwise, so an older project.json without the key reads as true and the
        # guard stays conservative. coerced to a plain bool.
        with _LOCK:
            return bool(self._state.get("client_data", True))

    def set_client_data(self, value: bool) -> None:
        # set the data-guard flag and persist atomically. coerced to a plain bool so a truthy non-bool
        # cannot store a surprising value the guard then mis-reads.
        with _LOCK:
            self._state["client_data"] = bool(value)
            self._write()


def get_store() -> ProjectStore:
    # the process-level singleton for the currently-resolved path. constructed on first use (reads the
    # file if present; does NOT write). keyed by resolved path so an env override gets its own store.
    with _LOCK:
        key = str(_resolve_path())
        store = _STORES.get(key)
        if store is None:
            store = ProjectStore(Path(key))
            _STORES[key] = store
        return store


def reset_for_tests() -> None:
    # TEST HOOK. drop the in-memory singleton for the currently-resolved path AND remove the runtime
    # file, so the next get_store() starts from a clean, empty state and run numbering restarts at 1.
    # create_app() calls this in demo mode so each TestClient(create_app()) test is isolated. the fresh
    # state comes from _empty_state(), so after a reset client_data is back to its default of true.
    with _LOCK:
        key = str(_resolve_path())
        _STORES.pop(key, None)
        path = Path(key)
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass
