"""Part 1.3: construction check. eta_d = eta_r = 1, F0 = 0, VECTO run with mod data, per truck:
   E_terminal (vsum: E_REESS_T_dischg - E_REESS_T_chg)  versus  integral of the vmod columns
   P_wheel_in (mechanical power at the wheel from the powertrain side), P_brake_loss (energy burned in the mechanical brake because the IEPC cannot
   take it), P_aux_el_HV, P_REESS_JB_Cables_loss (junction box and cables, inside the terminal energy), and the battery internal loss P_REESS_loss.
   The balance must close:  E_terminal = E_IEPC_el + E_aux + E_JB   and  E_IEPC_el = E_wheel_in (+ brake loss) when the map is lossless.
Also compares VECTO's wheel energy with the HDEV harness wheel energy for the same result (what the two drivers/brakes ask of the powertrain).
Outputs: p1_balance.csv (per result), p1_balance_summary.csv
"""
import csv
import os
import sys

import numpy as np

import engines as E
import vecto_job as VJ

HERE = E.HERE
ATTR = TI_ATTR = E.TI.ATTR
FILEKEY = {"LongHaul": "LongHaul", "LongHaulEMS": "LongHaulEMS", "RegionalDelivery": "RegionalDelivery", "RegionalDeliveryEMS": "RegionalDeliveryEMS",
           "UrbanDelivery": "UrbanDelivery", "Construction": "Construction"}


def integrate(path):
    rows = [r for r in csv.reader(open(path, encoding="utf-8-sig")) if r and not r[0].startswith("#")]
    h = rows[0]; ix = {n: i for i, n in enumerate(h)}
    d = np.array([[float(x) if x not in ("", "NaN") else 0.0 for x in r] for r in rows[1:]])
    dt = d[:, ix["dt [s]"]]
    km = d[-1, ix["dist [m]"]] / 1000.0

    def e(col, sel=None):
        x = d[:, ix[col]] * dt
        if sel is not None:
            x = x[sel(d[:, ix[col]])]
        return x.sum() / 3600.0 / km          # kWh/km
    out = dict(km=km, dt_s_median=float(np.median(dt)), rows=len(dt),
               E_REESS_T=-e("P_REESS_T [kW]"), E_REESS_int=-e("P_REESS_int [kW]"), E_REESS_loss=e("P_REESS_loss [kW]"), E_JB=e("P_REESS_JB_Cables_loss [kW]"),
               E_IEPC_el=-e("P_IEPC_el [kW]"), E_aux=e("P_aux_el_HV [kW]"), E_IEPC_out=e("P_IEPC_out [kW]"), E_wheel_in=e("P_wheel_in [kW]"),
               E_brake_loss=e("P_brake_loss [kW]"), E_axle_loss=e("P_axle_loss [kW]"), E_trac=e("P_trac [kW]"),
               E_wheel_drive=e("P_wheel_in [kW]", lambda x: x > 0), E_wheel_regen_side=e("P_wheel_in [kW]", lambda x: x < 0))
    return out


def main(cids=("C0059", "C0091")):
    E.setup()
    rows = []
    for cid in cids:
        tr = E.truck(cid)
        d = os.path.join(E.WORK, "bal_" + cid)
        rr = E.records(cid)
        cd = rr[0]["cdxa0"] if not tr["airdrag_method"].lower() == "measured" else 0.5 * (rr[0]["cdxa_lo"] + rr[0]["cdxa_hi"])
        # CdxA must be the declared value (range middle), harness records carry cdxa0 per mission incl. trailer delta: use base from the range
        from cdxa_ranges import CDXA_RANGES
        if tr["airdrag_method"].lower() == "measured":
            lo, hi = CDXA_RANGES[tr["cdxa_range"]]
            cd = 0.5 * (lo + hi)
        job = VJ.write_job(d, tr, 1.0, 1.0, 0.0, cd, f0_mode="axle")
        rc, out, dt = VJ.run(job, mod=True)
        print(cid, "rc", rc, "%.0f s" % dt, flush=True)
        vs = VJ.read_vsum(d)
        for r in rr:
            cyc = E.MISSION_VECTO[r["mission"]]
            m = [x for x in vs if x["cycle"] == cyc and abs(x["loading"] - r["payload"]) < 1.0][0]
            ld = "LowLoading" if m["loading"] == min(x["loading"] for x in vs if x["cycle"] == cyc) else "ReferenceLoad"
            f = os.path.join(d, "job_%s%s.vmod" % (cyc, ld))
            v = integrate(f)
            # harness (HDEV driver) wheel energy per km for the same result, all rows, and drive/regen split
            Pw = r["P_wheel"]
            wh = Pw.sum() / 3.6e6 / r["km"]
            whd = Pw[Pw > 0].sum() / 3.6e6 / r["km"]
            whr = Pw[Pw < 0].sum() / 3.6e6 / r["km"]
            term_vsum = m["term_kwh_km"]
            rows.append(dict(truck=cid, mission=r["mission"], payload_kg=round(r["payload"]),
                             vsum_terminal_kwh_km=round(term_vsum, 5), vmod_E_REESS_T=round(v["E_REESS_T"], 5),
                             vmod_E_IEPC_el=round(v["E_IEPC_el"], 5), vmod_E_aux=round(v["E_aux"], 5), vmod_E_JB_cables=round(v["E_JB"], 5),
                             balance_IEPC_el_plus_aux_plus_JB=round(v["E_IEPC_el"] + v["E_aux"] + v["E_JB"], 5),
                             balance_residual_kwh_km=round(term_vsum - (v["E_IEPC_el"] + v["E_aux"] + v["E_JB"]), 5),
                             vmod_E_wheel_in=round(v["E_wheel_in"], 5), vmod_E_brake_loss=round(v["E_brake_loss"], 5), vmod_E_axle_loss=round(v["E_axle_loss"], 5),
                             lossless_residual_IEPC_el_minus_wheel_in=round(v["E_IEPC_el"] - v["E_wheel_in"], 5),
                             vmod_E_wheel_drive=round(v["E_wheel_drive"], 5), vmod_E_wheel_regen_side=round(v["E_wheel_regen_side"], 5),
                             vmod_battery_internal_loss_not_in_terminal=round(v["E_REESS_loss"], 5),
                             harness_E_wheel_net=round(wh, 5), harness_E_wheel_drive=round(whd, 5), harness_E_wheel_regen_side=round(whr, 5),
                             vecto_step_s=v["dt_s_median"]))
    path = os.path.join(HERE, "p1_balance.csv")
    with open(path, "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r["truck"], r["mission"][:12], r["payload_kg"], "term %.4f  res %.5f  wheel_in %.4f IEPC_el %.4f brake %.4f | harness wheel %.4f drive %.4f regen %.4f | VECTO drive %.4f regen %.4f" % (
            r["vsum_terminal_kwh_km"], r["balance_residual_kwh_km"], r["vmod_E_wheel_in"], r["vmod_E_IEPC_el"], r["vmod_E_brake_loss"], r["harness_E_wheel_net"],
            r["harness_E_wheel_drive"], r["harness_E_wheel_regen_side"], r["vmod_E_wheel_drive"], r["vmod_E_wheel_regen_side"]))


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or ("C0059", "C0091"))
