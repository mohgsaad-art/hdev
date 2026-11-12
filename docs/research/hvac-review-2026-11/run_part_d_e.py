"""Part D (sensitivity / tornado) and Part E (HDEV thermal vs VECTO constant table on Danish weather).
Outputs: part_d_sensitivity.csv, part_d_tornado.png, part_e_annual.csv, part_e_monthly.csv, part_e_weeks.csv, part_e_waste_heat.csv
ILLUSTRATIVE: operating schedule Mon-Fri 06:00-16:00 local; the truck drives the whole shift at the mission's average speed.
"""
import csv, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import hvac_common as H
import reference_copy as R

HERE = os.path.dirname(os.path.abspath(__file__))
w = H.load_weather()
f = R.make_namespace()["HVAC_thermal"]
G = H.PLACEHOLDER
BASE_Q = 100.0        # Bob's proposed parser default (pending the Dvorak check); the sensitivity is around this point


def kwh(args=None, Q=BASE_Q, **kw):
    a = H.base_args(G); a.update(args or {}); a.update(kw)
    tot, _ = f(w["T"], w["S"], Q=Q, **a)
    return float(tot[w["op"]].sum() / 1000.0), tot


def scaled(name, fac):
    a = H.base_args(G)
    if name == "cop_heat": a["cop_heat_points"] = list(np.array(a["cop_heat_points"]) * fac); return a, BASE_Q, {}
    if name == "cop_cool": a["cop_cool_points"] = list(np.array(a["cop_cool_points"]) * fac); return a, BASE_Q, {}
    if name == "Q": return a, BASE_Q * fac, {}
    key = {"A_surface": "A_surface", "U": "U", "A_window": "A_window", "cab_volume": "cab_volume", "vent_rate": "vent_rate",
           "max_heating_power": "max_heating_power", "max_cooling_power": "max_cooling_power"}.get(name)
    if key: a[key] = a[key] * fac; return a, BASE_Q, {}
    return a, BASE_Q, {name: {"eh_eff": 0.93, "g": 0.95, "solar_factor": 0.25}[name] * fac}


if __name__ == "__main__":
    base, _ = kwh()
    base_q0, _ = kwh(Q=0.0)
    rows = []
    for name in ("A_surface", "U", "A_window", "g", "solar_factor", "Q", "cab_volume", "vent_rate", "cop_heat", "cop_cool", "eh_eff",
                 "max_heating_power", "max_cooling_power"):
        res = {}
        for fac in (0.9, 1.1):
            a, q, extra = scaled(name, fac)
            tot, _ = f(w["T"], w["S"], Q=q, **a, **extra)
            res[fac] = float(tot[w["op"]].sum() / 1000.0)
        rows.append(dict(input=name, kind="elasticity +-10% (no sourced range)", kWh_minus10=round(res[0.9], 1), kWh_base=round(base, 1),
                         kWh_plus10=round(res[1.1], 1), swing_kWh=round(abs(res[1.1] - res[0.9]), 1), swing_pct_of_base=round(100 * abs(res[1.1] - res[0.9]) / base, 2)))
    # discrete options with a VECTO source
    def opt(label, src, **kw):
        a = H.base_args(G, kw.pop("hp", "R-744"), kw.pop("hd", "HD2")); a.update(kw.pop("args", {}))
        q = kw.pop("Q", BASE_Q)
        tot, _ = f(w["T"], w["S"], Q=q, **a, **kw)
        v = float(tot[w["op"]].sum() / 1000.0)
        rows.append(dict(input=label, kind=f"option [{src}]", kWh_minus10="", kWh_base=round(base, 1), kWh_plus10=round(v, 1),
                         swing_kWh=round(abs(v - base), 1), swing_pct_of_base=round(100 * abs(v - base) / base, 2)))
    opt("U = 4.0 (VECTO low-floor bus)", "VECTO DeclarationData.cs:557", args={"U": 4.0})
    opt("U = 3.5 (VECTO semi-low-floor bus)", "VECTO DeclarationData.cs:559", args={"U": 3.5})
    opt("no heat pump: electric heater only (HD9)", "VECTO HeatingDistribution.csv HD9", hd="HD9")
    opt("heat pump = non-R-744 continuous, HP only (HD1-type shares), -20 C cell filled by parser clip 1.78", "VECTO DefaultClimatic.aenv + parser rule 12 Nov", hp="non R-744 continuous", hd="HD1",
        args={"cop_heat_points": [1.78, 1.78, 2.22, 2.94, 3.50]})
    opt("N_persons = 1 (driver only)", "physical option", args={"N_persons": 1})
    opt("N_persons = 2", "physical option", args={"N_persons": 2})
    opt("Q = 0 (VECTO, no fresh-air term)", "VECTO", Q=0.0)
    opt("vent 20 / 10 1/h (VECTO config 3-10 rates)", "VECTO DeclarationData.cs:469-470", args={"vent_rate": 20.0, "vent_rate_heating": 10.0})
    opt("setpoints 18/23 -> 20/23 (ILLUSTRATIVE; no source for other setpoints)", "ILLUSTRATIVE", T_heat=20.0)
    # waste heat per VECTO M14: usable = EM loss * 0.9 * 0.75 (M14Impl.cs 58-60, Constants.cs 196-200); E2 .vmod mean P_E2-em_loss
    wr = []
    for m in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
        df = pd.read_csv(os.path.join(os.path.dirname(H.HERE), "vecto", f"BEV_E2_{m}_ReferenceLoad_1Hz.vmod"), skiprows=1, encoding="latin-1",
                         usecols=["P_E2-em_loss [kW]"])
        loss_w = float(df["P_E2-em_loss [kW]"].mean() * 1000)
        wr.append(dict(mission=m, mean_EM_loss_W=round(loss_w, 1), usable_waste_heat_W=round(loss_w * 0.9 * 0.75, 1)))
    wh = wr[0]["usable_waste_heat_W"]
    opt(f"waste_heat = {wh:.0f} W (VECTO M14 formula, E2 Regional mean EM loss) while driving", "VECTO M14Impl.cs:58-60 + E2 .vmod", args={"waste_heat": wh})
    pd.DataFrame(wr).to_csv(os.path.join(HERE, "part_e_waste_heat.csv"), index=False)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "part_d_sensitivity.csv"), index=False)
    # tornado
    t = out[out.kind.str.startswith("elasticity")].sort_values("swing_kWh")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(t.input, t.kWh_plus10 - t.kWh_base, color="tab:red", label="+10 %")
    ax.barh(t.input, t.kWh_minus10 - t.kWh_base, color="tab:blue", label="-10 %")
    ax.axvline(0, color="k", lw=.8); ax.set_xlabel(f"change of annual HVAC kWh (operating hours; base {base:.0f} kWh, Q=100 m3/h)")
    ax.set_title("Part D tornado, +-10 % of each input (PLACEHOLDER cab, ILLUSTRATIVE schedule)"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "part_d_tornado.png"), dpi=130)
    print(out.to_string()); print("base kWh", base, "base Q=0", base_q0)

    # ---------------- Part E ----------------
    e2 = H.vecto_e2()
    ann, mon, wk = [], [], []
    sets = {"(ii) HDEV placeholders Q=0": (H.PLACEHOLDER, 0.0), "(ii) HDEV placeholders Q=100": (H.PLACEHOLDER, 100.0),
            "(iii-bus) VECTO driver-compartment analogue Q=0 [BUS values]": (H.VECTO_DRIVER_ANALOGUE, 0.0),
            "(iii-bus) VECTO driver-compartment analogue Q=100 [BUS values]": (H.VECTO_DRIVER_ANALOGUE, 100.0)}
    idx = w["local"]
    for m, d in e2.items():
        v_avg = d["dist_km"] / d["time_h"]
        op_h = int(w["op"].sum())
        series = {"(i) VECTO lorry table (.vmod P_aux_AC_el)": np.full(len(w["T"]), d["ac_w"])}
        for k, (g, q) in sets.items():
            a = H.base_args(g); tot, _ = f(w["T"], w["S"], Q=q, **a); series[k] = tot
        for k, s in series.items():
            kw_year = float(s[w["op"]].sum() / 1000)
            per100 = kw_year * 1000 / op_h / v_avg / 1000 * 100          # kWh/100 km when driving the whole shift at v_avg
            share = per100 / (100 * d["kwh_km_chainS_V1"]) * 100 if d["kwh_km_chainS_V1"] == d["kwh_km_chainS_V1"] else np.nan
            ann.append(dict(mission=m, source=k, annual_kWh_operating_h=round(kw_year, 1), mean_W_operating_h=round(kw_year * 1000 / op_h, 1),
                            kWh_per_100km=round(per100, 2), share_of_trip_energy_pct=round(share, 2) if share == share else "n/a (no Chain S V1 for LongHaul)",
                            v_avg_kmh=round(v_avg, 1)))
            df = pd.DataFrame({"hvac": s, "op": w["op"]}, index=idx)
            mm = df[df.op].groupby(df[df.op].index.month).hvac.sum() / 1000
            for mo, val in mm.items():
                mon.append(dict(mission=m, source=k, month=int(mo), kWh=round(float(val), 1)))
            if m == "RegionalDelivery":
                tw = pd.Series(w["T"], index=idx)[w["op"]]
                wkmean = tw.groupby(tw.index.isocalendar().week).mean()
                cold, hot = int(wkmean.idxmin()), int(wkmean.idxmax())
                for lab, wn in (("coldest week", cold), ("hottest week", hot)):
                    sel = df[df.op & (df.index.isocalendar().week == wn).values]
                    wk.append(dict(source=k, which=lab, iso_week=wn, mean_T_C=round(float(wkmean[wn]), 1),
                                   mean_W_operating_h=round(float(sel.hvac.mean()), 1), kWh_week=round(float(sel.hvac.sum() / 1000), 2)))
    for fn, rws in (("part_e_annual.csv", ann), ("part_e_monthly.csv", mon), ("part_e_weeks.csv", wk)):
        pd.DataFrame(rws).to_csv(os.path.join(HERE, fn), index=False); print("wrote", fn)
    mdf = pd.DataFrame(mon); mdf = mdf[mdf.mission == "RegionalDelivery"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for k, g in mdf.groupby("source"):
        ax.plot(g.month, g.kWh, marker="o", label=k)
    ax.set_xlabel("month 2025"); ax.set_ylabel("HVAC kWh in operating hours"); ax.legend(fontsize=7); ax.set_title("Part E: monthly HVAC energy, Copenhagen 2025 (ILLUSTRATIVE schedule)")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "part_e_monthly.png"), dpi=130)
    print(pd.DataFrame(ann).to_string()); print(pd.DataFrame(wk).to_string())
