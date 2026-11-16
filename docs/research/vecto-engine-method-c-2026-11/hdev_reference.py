"""HDEV-engine method C, PR #37 Part 3 code (methods_lib.fit_v2, loo_v2), recomputed here and checked against part3_predictions.csv / part3_fitted_values.csv."""
import csv
import json
import os

import numpy as np

import engines as E

ML = E.ML
HERE = E.HERE


def run():
    E.setup()
    out = {}
    for cid in E.TI.TRUCKS:
        rr = E.records(cid)
        m = E.method(cid)
        th, rms = ML.fit_v2(m, rr)
        loo = ML.loo_v2(m, rr, None)
        pred_full = np.array([m.predict(r, th) for r in rr])
        out[cid] = dict(theta=list(th), names=list(m.names), rms=rms, pred_full=pred_full.tolist(), loro_pred=[x["pred"] for x in loo],
                        loro_theta=[list(x["theta"]) for x in loo], cert=[r["cert"] for r in rr],
                        keys=[[r["mission"], round(r["payload"]), round(r["mass"], 1)] for r in rr])
    json.dump(out, open(os.path.join(HERE, "hdev_reference.json"), "w"), indent=1)
    # cross-check against PR #37 files
    ref = {}
    for r in csv.DictReader(l for l in open(os.path.join(E.TI.LIB, "part3_predictions.csv")) if not l.startswith("#")):
        if r["method"] == "C" and r["view"] == "LORO" and r["config_id"] in out:
            ref[(r["config_id"], r["mission"], int(r["payload_kg"]))] = float(r["predicted_kwh_km"])
    mx = 0.0
    for cid, d in out.items():
        for k, p in zip(d["keys"], d["loro_pred"]):
            mx = max(mx, abs(ref[(cid, k[0], k[1])] - p))
        print(cid, "full fit", np.round(d["theta"], 5), "rms %.3f %%" % (100 * d["rms"]))
    print("max |LORO prediction here - part3_predictions.csv| = %.5f kWh/km (csv has 4 decimals)" % mx)


if __name__ == "__main__":
    run()
