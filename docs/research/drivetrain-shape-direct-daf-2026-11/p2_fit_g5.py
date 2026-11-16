"""Part 2.2: per-config full fits of L1 and L1b on group 5, in config batches of 30 (cache from PR #38).

Usage: python p2_fit_g5.py <shape_key> [L1|L1b ...]       shape_key: arch | S3a_IEPC_1speed | S3b_IEPC_3speed | S2_busIEPC_PSM | S2_busIEPC_ASM | S4_std_ASM
Writes p2_fits_<kind>_<shape>.csv (508/254 rows per kind). 8 worker processes; every batch prints its wall time (limit 10 min).
"""
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import lib_g5 as L
import p2_methods as PM

ML, HN = L.ML, L.HN
HERE = L.HERE
_G = {}


def _fit(job):
    kind, shape_key, cid = job
    rr = _G["by"][cid]
    m = PM.make(kind, shape_key, rr[0])
    th, rms = ML.fit_v2(m, rr)
    lo, hi = m.bounds_for(rr[0])
    hit = ";".join(n for n, v, a, b in zip(m.names, th, lo, hi) if min(abs(v - a), abs(b - v)) <= 1e-3 * (b - a))
    e = np.array([m.predict(r, th) / r["cert"] - 1 for r in rr])
    sh = m.base.shape_for(rr[0]) if hasattr(m, "base") else m.shape_for(rr[0])
    row = dict(config_id=cid, make=_G["cfg"][cid]["Make_clean"], model=_G["cfg"][cid]["Model"], method=PM.label(kind, shape_key), shape_used=sh.name,
               n_results=len(rr), n_fitted=len(th), at_bound=hit, in_sample_mean_abs_err_pct=round(100 * float(np.mean(np.abs(e))), 3),
               in_sample_worst_abs_err_pct=round(100 * float(np.abs(e).max()), 3), in_sample_mean_err_pct=round(100 * float(e.mean()), 3),
               s=th[0] if kind == "L1" else "", s_drive=th[0] if kind == "L1b" else "", s_regen=th[1] if kind == "L1b" else "",
               s_max=lo and (hi[0] if kind == "L1" else ";".join("%.4g" % x for x in hi[:2])),
               cdxa_declared_m2=(th[-1] if rr[0]["airdrag_measured"] else ""))
    return row


def main(shape_key, kinds):
    L.setup()
    by = L.records()
    ids, cfg = L.g5_config_ids()
    _G.update(by=by, cfg=cfg)
    for kind in kinds:
        rows = []
        for b in range(0, len(ids), L.BATCH):
            t0 = time.monotonic()
            with mp.get_context("fork").Pool(8) as pool:
                rows += pool.map(_fit, [(kind, shape_key, c) for c in ids[b:b + L.BATCH]], chunksize=1)
            dt = time.monotonic() - t0
            print("%s %s batch %d: %d fits, %.1f s" % (kind, shape_key, b // L.BATCH, len(rows), dt), flush=True)
            if dt > 600:
                raise SystemExit("BLOCKED: batch exceeded 10 minutes")
        L.write(os.path.join(HERE, "p2_fits_%s_%s.csv" % (kind, shape_key)), rows)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or ["L1", "L1b"])
