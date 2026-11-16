"""The two engines as functions of the method C values theta = (eta_d, eta_r, F0 [N], CdxA [m2] or absent).

hdev_predict   PR #37 harness records (HDEV driver + force engine) + method C (methods_lib), kWh/km "certified-side" = terminal energy / km / 0.995
vecto_predict  VECTO runs the same truck with method C built into its IEPC (vecto_job.py); the same definition: terminal energy / km / 0.995
Both are cached by parameter set (cache/*.json) so a run is never repeated.
"""
import hashlib
import json
import os
import shutil
import threading
import time

import numpy as np

import truck_inputs as TI
import vecto_job as VJ

HN, P3, HERE = TI.HN, TI.P3, TI.HERE
ML = __import__("methods_lib")
CACHE = os.path.join(HERE, "cache")
WORK = os.path.join(HERE, "work")
CHARGING_ETA = HN.CHARGING_ETA
MISSION_VECTO = {"Long Haul": "LongHaul", "Long Haul EMS": "LongHaulEMS", "Regional Delivery": "RegionalDelivery", "Regional Delivery EMS": "RegionalDeliveryEMS",
                 "Urban Delivery": "UrbanDelivery", "Construction": "Construction"}
_REC = {}
_TR = {}
_lock = threading.Lock()


class DeadlineExceeded(Exception):
    """Raised before a new VECTO job is started when the command's time budget (10-minute rule) would be exceeded. Re-run the same command: every
    finished job is cached and the fit replays deterministically up to this point."""


def _deadline_check(expected_s):
    dl = float(os.environ.get("VECTO_DEADLINE", "0") or 0)
    if dl and time.time() + expected_s > dl:
        raise DeadlineExceeded("budget exhausted")


def setup():
    P3.set_bounds()
    HN.AIRDRAG_MODE = "range_mid"


def records(cid):
    if not _REC:
        setup()
        recs, skipped = HN.load_or_build(P3.TEN, "ten", processes=8)
        for r in recs:
            _REC.setdefault(r["config_id"], []).append(r)
        for v in _REC.values():
            v.sort(key=lambda r: (r["mission"], r["payload"]))
    return _REC[cid]


def truck(cid):
    if cid not in _TR:
        _TR[cid] = TI.vehicle_inputs(cid)
    return _TR[cid]


def method(cid):
    rr = records(cid)
    return P3.make("C", rr[0])


def bounds(cid):
    rr = records(cid)
    m = method(cid)
    lo, hi = m.bounds_for(rr[0])
    return np.array(lo, float), np.array(hi, float), m.names


def starts(cid):
    rr = records(cid)
    m = method(cid)
    return [tuple(s) for s in m.starts_for(rr[0])]


def hdev_predict(cid, theta):
    rr = records(cid)
    m = method(cid)
    return np.array([m.predict(r, tuple(theta)) for r in rr])


def certified(cid):
    return np.array([r["cert"] for r in records(cid)])


def key_of(r):
    return (MISSION_VECTO[r["mission"]], round(r["payload"]))


def _match(cid, rows):
    """Order the VECTO rows like records(cid). Returns array of terminal kWh/km and final kWh/km, raises if a result is missing."""
    rr = records(cid)
    term, fin, meta = [], [], []
    for r in rr:
        cyc = MISSION_VECTO[r["mission"]]
        c = [x for x in rows if x.get("status") == "Success" and x["cycle"] == cyc and abs(x["loading"] - r["payload"]) < 1.0]
        if len(c) != 1:
            raise RuntimeError("VECTO result for %s %s kg not found (%d matches)" % (cyc, r["payload"], len(c)))
        if abs(c[0]["mass"] - r["mass"]) > 1.0:
            raise RuntimeError("mass mismatch %s %s: VECTO %.1f EEA %.1f" % (cyc, r["payload"], c[0]["mass"], r["mass"]))
        term.append(c[0]["term_kwh_km"] / CHARGING_ETA)
        fin.append(c[0]["final_kwh_km"] / CHARGING_ETA)
        meta.append(c[0])
    return np.array(term), np.array(fin), meta


def pkey(cid, theta, f0_mode, tag=""):
    s = json.dumps([cid, [round(float(x), 6) for x in theta], f0_mode, tag])
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def vecto_run(cid, theta, f0_mode="axle", mod=False, tag="", timeout=1500):
    """theta = (eta_d, eta_r, F0, [cdxa]). Returns dict(term=array kWh/km (certified side), final=array, wall_s, meta) ; cached on disk."""
    os.makedirs(CACHE, exist_ok=True)
    k = pkey(cid, theta, f0_mode, tag)
    f = os.path.join(CACHE, "%s_%s.json" % (cid, k))
    if os.path.exists(f):
        d = json.load(open(f))
        d["term"] = np.array(d["term"]); d["final"] = np.array(d["final"])
        return d
    _deadline_check(JOB_EXPECTED_S[cid])
    tr = truck(cid)
    eta_d, eta_r, F0 = theta[:3]
    rr = records(cid)
    cdxa = theta[3] if len(theta) > 3 else (rr[0]["cdxa0"] if not tr["airdrag_method"].lower() == "measured" else None)
    if cdxa is None:
        raise ValueError("measured air drag needs a CdxA value")
    d = os.path.join(WORK, "%s_%s" % (cid, k))
    shutil.rmtree(d, ignore_errors=True)
    job = VJ.write_job(d, tr, eta_d, eta_r, F0, cdxa, f0_mode=f0_mode)
    rc, out, dt = VJ.run(job, mod=mod, timeout=timeout)
    rows = VJ.read_vsum(d)
    if not rows or any(r.get("status") != "Success" for r in rows):
        raise RuntimeError("VECTO failed for %s theta=%s rc=%s\n%s" % (cid, theta, rc, out[-1500:]))
    term, fin, meta = _match(cid, rows)
    res = dict(term=term.tolist(), final=fin.tolist(), wall_s=dt, f0_mode=f0_mode, theta=[float(x) for x in theta], n_runs_in_job=len(rows),
               meta=[dict(cycle=m["cycle"], loading=m["loading"], mass=m["mass"], cdxa=m["cdxa"]) for m in meta])
    json.dump(res, open(f, "w"))
    if not mod:
        shutil.rmtree(d, ignore_errors=True)
    res["term"] = term; res["final"] = fin
    return res


JOB_EXPECTED_S = {"C0059": 45.0, "C0091": 130.0}     # wall seconds of one job when several run concurrently (measured)


def prewarm():
    """Load all shared state in the main thread before any worker thread starts (the harness loaders are not thread safe)."""
    for cid in TI.TRUCKS:
        records(cid)
        truck(cid)
