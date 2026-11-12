"""Gate 3b: Bob's HVAC_thermal (notebook, via _load_notebook) vs the VECTO port, same inputs, on a grid.

Grid: T_amb -30..+40 degC step 1, solar 0..1000 W/m2 step 100, Q = 0 (so the fresh-air term is off = VECTO).
The COPs and heating shares are looked up ONCE (with Bob's climate_lookup) and given to both sides, so this test
isolates the maths (heat balance, decision, caps, COP division, fan).  How VECTO picks COP/shares (by condition ID, not by
temperature) is a separate question: Part C.

Bob's function returns only the total HVAC_el.  The four parts are separated WITHOUT changing the code, by calling it
with one part switched off through its own arguments:
   fan only      : max_heating_power = 0 and max_cooling_power = 0
   heat pump off : cop_heat_points -> 1e30        electric heater off: eh_eff -> 1e30        AC off: cop_cool_points -> 1e30
Run: python gate3_grid.py   ->  gate3_grid_summary.csv, gate3_grid_worst_cases.csv
"""
import csv
import os
import numpy as np
from _load_notebook import NS
import vecto_ssm_port as P

HERE = os.path.dirname(os.path.abspath(__file__))
HVAC_thermal, climate_lookup = NS["HVAC_thermal"], NS["climate_lookup"]
ENVS = P.read_env_map()

# VECTO bus used for the comparison = the bus of VECTO's own unit tests (vehicle code CA, 12 m x 2.55 m x 3 m), one compartment.
BUS = dict(surface=136.5, window=23.0, U=3.0, n_pass=41, volume=76.5, vent_rate=20.0, vent_rate_heating=10.0)
T_HEAT_PTS = [-20.0, -5.0, 2.0, 8.0, 14.0]       # DefaultClimatic.aenv rows 1,2,3,4/5,6/7 (heating rows) -- unique temperatures
T_COOL_PTS = [20.5, 26.0, 33.0]                   # aenv rows 8/9, 10, 11 (cooling rows)
COP_H_R744 = [1.80, 2.04, 2.50, 2.98, 3.38]       # aenv column R-744, heating rows
COP_C_R744 = [3.80, 2.82, 2.14]                   # aenv column R-744, cooling rows
COP_H_CONT = [np.nan, 1.78, 2.22, 2.94, 3.50]     # aenv 'non R-744 continuous' (the -20 degC cell is '-' = no value)
COP_C_CONT = [3.88, 3.36, 2.74]

CASES = {
    # name: shares per heating point (hp, eh, fuel), cop_h, cop_c, caps (heat, cool), fuel heater power
    "A  R-744 + el.heater + fuel heater (HD3), caps 5 kW/5 kW": dict(
        hp=[.4, .7, .8, 1, 1], eh=[.2, 0, 0, 0, 0], fuel=[.4, .3, .2, 0, 0], cop_h=COP_H_R744, cop_c=COP_C_R744, cap_h=5000., cap_c=5000., fuel_p=30e3),
    "B  R-744 + el.heater (HD2), no caps": dict(
        hp=[.5, 1, 1, 1, 1], eh=[.5, 0, 0, 0, 0], fuel=[0] * 5, cop_h=COP_H_R744, cop_c=COP_C_R744, cap_h=1e9, cap_c=1e9, fuel_p=0.),
    "C  R-744 only (HD1), caps 3 kW/2 kW": dict(
        hp=[1] * 5, eh=[0] * 5, fuel=[0] * 5, cop_h=COP_H_R744, cop_c=COP_C_R744, cap_h=3000., cap_c=2000., fuel_p=0.),
    "D  electric heater only (HD9), no caps": dict(
        hp=[0] * 5, eh=[1] * 5, fuel=[0] * 5, cop_h=COP_H_R744, cop_c=COP_C_R744, cap_h=1e9, cap_c=1e9, fuel_p=0.),
    "E  fuel heater only (HD11), heater 30 kW": dict(
        hp=[0] * 5, eh=[0] * 5, fuel=[1] * 5, cop_h=COP_H_R744, cop_c=COP_C_R744, cap_h=5000., cap_c=5000., fuel_p=30e3),
}


def bob_parts(T, S, c):
    base = dict(A_surface=BUS["surface"], U=BUS["U"], N_persons=BUS["n_pass"], A_window=BUS["window"],
                T_heat_points=T_HEAT_PTS, cop_heat_points=c["cop_h"], T_cool_points=T_COOL_PTS, cop_cool_points=c["cop_c"],
                hp_share_points=c["hp"], eh_share_points=c["eh"], fuel_share_points=c["fuel"],
                max_heating_power=c["cap_h"], max_cooling_power=c["cap_c"], cab_volume=BUS["volume"],
                vent_rate=BUS["vent_rate"], vent_rate_heating=BUS["vent_rate_heating"])      # all other args = Bob's defaults
    tot, fuel_heat = HVAC_thermal(T, S, **base)
    off = lambda **kw: HVAC_thermal(T, S, **{**base, **kw})[0]
    big = 1e30
    fan = off(max_heating_power=0.0, max_cooling_power=0.0)
    no_hp = off(cop_heat_points=[big] * 5)
    no_eh = off(eh_eff=big)
    no_ac = off(cop_cool_points=[big] * 3)
    return dict(total=tot, fan=fan, hp=tot - no_hp, eh=tot - no_eh, ac=tot - no_ac, fuel_heat=fuel_heat)


def port_parts(T, S, c):
    cop_h, cop_c, hp, eh, fu = climate_lookup(T, T_HEAT_PTS, c["cop_h"], T_COOL_PTS, c["cop_c"], c["hp"], c["eh"], c["fuel"])
    out = {k: np.zeros_like(T) for k in ("total", "fan", "hp", "eh", "ac", "fuel_heat")}
    flat = [(i, j) for i in range(T.shape[0]) for j in range(T.shape[1])]
    bus = dict(BUS)
    for i, j in flat:
        r = P.point_parts(T[i, j], S[i, j], bus, cop_h[i, j], cop_c[i, j], hp[i, j], eh[i, j], fu[i, j],
                          c["cap_h"], c["cap_c"], waste_heat=0.0, eh_eff=0.93, fuel_eff=0.80, fuel_power=c["fuel_p"])
        out["total"][i, j] = r["total_el"]; out["fan"][i, j] = r["fan"]; out["hp"][i, j] = r["hp"]
        out["eh"][i, j] = r["eh"]; out["ac"][i, j] = r["ac"]
        out["fuel_heat"][i, j] = r["demand"] * (fu[i, j] if not np.isnan(fu[i, j]) else 0.0)     # heat basis, to compare with Bob's fuel_heat
    return out


if __name__ == "__main__":
    Tg, Sg = np.meshgrid(np.arange(-30, 41, 1.0), np.arange(0, 1001, 100.0), indexing="ij")
    rows, worst = [], []
    for name, c in CASES.items():
        b, p = bob_parts(Tg, Sg, c), port_parts(Tg, Sg, c)
        row = {"case": name, "n_points": Tg.size}
        for k in ("total", "hp", "eh", "ac", "fan", "fuel_heat"):
            d = np.abs(b[k] - p[k])
            row[f"max_abs_diff_{k}_W"] = float(d.max())
            if d.max() > 1e-6:
                i, j = np.unravel_index(np.argmax(d), d.shape)
                worst.append(dict(case=name, part=k, T=Tg[i, j], solar=Sg[i, j], bob=b[k][i, j], port=p[k][i, j]))
        rows.append(row)
        print(name, {k: v for k, v in row.items() if k.startswith("max")})
    with open(os.path.join(HERE, "gate3_grid_summary.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, "gate3_grid_worst_cases.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["case", "part", "T", "solar", "bob", "port"]); w.writeheader(); w.writerows(worst)
    print("wrote gate3_grid_summary.csv, gate3_grid_worst_cases.csv")
