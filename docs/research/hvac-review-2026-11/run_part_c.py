"""Part C: VECTO reproduction at VECTO's environmental-condition points, and the effect of each HDEV deviation.
Outputs: part_c_points.csv, part_c_deviations.csv
Geometry sets: PLACEHOLDER (Bob 20 m2 / 3.0 / 4 m2 / 6.5 m3, N=2) and VECTO_DRIVER_ANALOGUE (a BUS driver compartment).
Fixed choices (see report 'Choices I made'): R-744 heat pump + electric heater (HD2), caps 5 kW / 5 kW (HVACHeating/CoolingPowerDriver.csv),
ventilation 7 1/h (DeclarationData.cs:458 configurations 1-2), eh_eff 0.93, Q = 0 unless stated.
"""
import csv, os
import numpy as np
import hvac_common as H
import vecto_ssm_port as P
import reference_copy as R

HERE = os.path.dirname(os.path.abspath(__file__))
ENVS = P.read_env_map(); HDT = P.read_heating_distribution()
GEOMS = {"PLACEHOLDER": H.PLACEHOLDER, "VECTO_DRIVER_ANALOGUE(bus)": H.VECTO_DRIVER_ANALOGUE}


def vecto_points(geom, hd="HD2", hp="R-744", cap=5000.0):
    """VECTO way: COP and shares looked up by condition ID (not by temperature). Returns per-point electric W + weight."""
    rows = []
    bus = dict(surface=geom["A"], window=geom["Aw"], U=geom["U"], n_pass=geom["N"], volume=geom["V"], vent_rate=7.0, vent_rate_heating=7.0)
    for e in ENVS:
        ent = HDT[(hd, e.id)]
        cop_h = e.cop.get(hp, np.nan)                                  # heating COP of the row (same table is used for cooling rows)
        r = P.point_parts(e.T, e.solar, bus, cop_h, cop_h, P._nz(ent["hp"].get(hp, 0)), P._nz(ent["eh"]), P._nz(ent["fuel"]), cap, cap)
        rows.append(dict(id=e.id, T=e.T, solar=e.solar, w=e.weight, **{k: r[k] for k in ("hp", "eh", "ac", "fan", "total_el")}))
    return rows


def bob_at_points(geom, ns=None, Q=0.0, hd="HD2", hp="R-744"):
    f = (ns or R.make_namespace())["HVAC_thermal"]
    T = np.array([e.T for e in ENVS]); S = np.array([e.solar for e in ENVS])
    tot, _ = f(T, S, Q=Q, **H.base_args(geom, hp, hd))
    return tot


def mean_year(f, geom, w, Q=0.0, hd="HD2", hp="R-744", mask=None, **kw):
    a = H.base_args(geom, hp, hd); a.update(kw)
    tot, fuel = f(w["T"], w["S"], Q=Q, **a)
    m = w["op"] if mask is None else mask
    return float(tot[m].mean()), float(tot.mean()), tot


if __name__ == "__main__":
    w = H.load_weather()
    pts, dev = [], []
    for gname, g in GEOMS.items():
        vp = vecto_points(g)
        bob = bob_at_points(g)
        for r, b in zip(vp, bob):
            pts.append(dict(geometry=gname, id=r["id"], T=r["T"], solar=r["solar"], weight=round(r["w"], 5), vecto_port_W=round(r["total_el"], 4),
                            bob_W=round(float(b), 4), diff_W=float(b - r["total_el"])))
        v_w = sum(r["w"] * r["total_el"] for r in vp)
        b_w = float(np.sum([r["w"] for r in vp] * bob))
        pts.append(dict(geometry=gname, id="WEIGHTED", T="", solar="", weight=1, vecto_port_W=round(v_w, 4), bob_W=round(b_w, 4), diff_W=b_w - v_w))
        print(f"{gname}: VECTO-style weighted mean {v_w:.2f} W  Bob at same points {b_w:.2f} W (diff {b_w - v_w:.2e})")

        # ---- deviations on the Danish year (operating hours / all hours), each against the previous step ------------
        base = R.make_namespace()["HVAC_thermal"]
        m0_op, m0_all, _ = mean_year(base, g, w)
        steps = [("Bob hourly, Q=0 (VECTO maths, real weather)", m0_op, m0_all)]
        a_op, a_all, _ = mean_year(base, g, w, Q=100.0)
        steps.append(("(a) + fresh air Q=100 m3/h", a_op, a_all))
        # (c) COP method on the hourly year (Q=0): step vs interp
        c_op, c_all, _ = mean_year(R.variant("v_step_cop"), g, w)
        steps.append(("(c) Q=0, COP as step (nearest point) instead of np.interp", c_op, c_all))
        d_op, d_all, _ = mean_year(R.variant("v_linear_shares"), g, w)
        steps.append(("(d) Q=0, shares interpolated instead of nearest point", d_op, d_all))
        for name, op, al in steps:
            dev.append(dict(geometry=gname, step=name, mean_W_operating_h=round(op, 2), mean_W_all_h=round(al, 2),
                            delta_vs_Bob_Q0_W=round(op - m0_op, 2), delta_pct=round(100 * (op - m0_op) / m0_op, 2),
                            kWh_per_year_operating=round(op * w["op"].sum() / 1000, 1)))
        dev.append(dict(geometry=gname, step="(b) VECTO-weighted point mean (not hourly) for reference", mean_W_operating_h=round(v_w, 2),
                        mean_W_all_h="", delta_vs_Bob_Q0_W=round(v_w - m0_op, 2), delta_pct=round(100 * (v_w - m0_op) / m0_op, 2), kWh_per_year_operating=""))
        # (e) COP clip below -5: non-R-744 'continuous' heat pump alone (HD5-like: hp share 1) -- VECTO gives 0 W where the COP cell is '-'
        n_below = int((w["T"] < -5).sum())
        for label, cop_m20 in (("clip = value at -5 C (1.78) [parser rule 12 Nov]", 1.78), ("floor COP = 1.0 (resistive limit)", 1.0)):
            a = H.base_args(g, "non R-744 continuous", "HD1"); a["cop_heat_points"] = [cop_m20, 1.78, 2.22, 2.94, 3.50]
            tot, _ = base(w["T"], w["S"], **a)
            dev.append(dict(geometry=gname, step=f"(e) non-R744 continuous HP only, COP at -20 C: {label}; hours < -5 C = {n_below}",
                            mean_W_operating_h=round(float(tot[w['op']].mean()), 2), mean_W_all_h=round(float(tot.mean()), 2),
                            delta_vs_Bob_Q0_W="", delta_pct="", kWh_per_year_operating=round(float(tot[w['op']].sum() / 1000), 1)))
        # VECTO would give 0 W for HP-only at the '-' cell (SC 194-197): count what that hides
        print(f"  hours < -5 C in 2025: {n_below}; min T {w['T'].min():.1f} C (so the -20 C COP cell is never reached in this year)")
    for fn, rows in (("part_c_points.csv", pts), ("part_c_deviations.csv", dev)):
        with open(os.path.join(HERE, fn), "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0]) + [k for k in rows[-1] if k not in rows[0]]); wr.writeheader(); wr.writerows(rows)
        print("wrote", fn)
