"""Part F measured effects that need NO unsourced number: equivalence solves, per-unit effects, stop counts from the E2 .vmod files.
Output: part_f_effects.csv.   Variants come from reference_copy.py (Bob's code + one named patch)."""
import csv, os
import numpy as np
import pandas as pd
from scipy.optimize import brentq
import hvac_common as H
import reference_copy as R

HERE = os.path.dirname(os.path.abspath(__file__))
w = H.load_weather(verbose=False)
f = R.make_namespace()["HVAC_thermal"]
G = H.PLACEHOLDER
op = w["op"]; nop = int(op.sum())
rows = []


def mean_w(Q=0.0, ua_scale=1.0, S_scale=1.0, **kw):
    a = H.base_args(G); a["U"] = a["U"] * ua_scale; a.update(kw)
    tot, _ = f(w["T"], w["S"] * S_scale, Q=Q, **a)
    return float(tot[op].mean())


def add(item, value, unit, note):
    rows.append(dict(item=item, value=round(float(value), 3), unit=unit, note=note)); print(rows[-1])


base0 = mean_w(0.0)
add("HDEV thermal mean power, placeholders, Q=0", base0, "W (operating hours)", "reference for the rows below")
for tgt, nm in ((250.0, "VECTO lorry table Regional/LongHaul 250 W"), (187.5, "VECTO lorry table Urban 187.5 W")):
    s = brentq(lambda x: mean_w(0.0, ua_scale=x) - tgt, 0.01, 20)
    add(f"F1 UA factor (vs 60 W/K) at which HDEV thermal (Q=0) = {nm}", s, "x", f"UA would be {60 * s:.0f} W/K")
    q = brentq(lambda x: mean_w(x) - tgt, 0.0, 2000)
    add(f"F6 fresh air Q at which HDEV thermal (U*A=60 W/K) = {nm}", q, "m3/h", "equivalence only, not a recommendation")
add("F1 effect of +10 % UA while moving (all operating hours treated as moving)", mean_w(0.0, 1.1) - base0, "W", "per +10 % UA, Q=0 (no sourced driving/parked ratio found)")
add("F7 share of Q=100 annual HVAC energy that is the solar term (S=0 vs real S)", 100 * (mean_w(100.0) - mean_w(100.0, S_scale=0.0)) / mean_w(100.0), "%",
    "upper bound on what any solar refinement (sol-air, orientation) can change at the current 4 m2 window area")
add("F6 effect of Q=100 m3/h", mean_w(100.0) - base0, "W", "= +kWh/yr: " + f"{(mean_w(100.0) - base0) * nop / 1000:.0f}")

# stops per hour from E2 .vmod (v_act == 0 episodes)
for m in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
    df = pd.read_csv(os.path.join(os.path.dirname(H.HERE), "vecto", f"BEV_E2_{m}_ReferenceLoad_1Hz.vmod"), skiprows=1, encoding="latin-1", usecols=["time [s]", "v_act [km/h]"])
    stopped = (df["v_act [km/h]"].values < 0.1).astype(int)
    n_stops = int(((stopped[1:] == 1) & (stopped[:-1] == 0)).sum())
    hrs = df["time [s]"].iloc[-1] / 3600
    add(f"F2/F4 stop episodes in E2 {m} cycle (v < 0.1 km/h)", n_stops, "stops", f"in {hrs:.2f} h = {n_stops / hrs:.1f} per hour [VECTO .vmod]")
# warm-up per start and door opening: per-unit energy (needs C [J/K] and V_exchanged [m3] -> NO SOURCE, so per unit)
Tmean_op = float(w["T"][op & (w["T"] < 18)].mean())
dT_cold = float(np.mean(18.0 - w["T"][op & (w["T"] < 18)]))
add("F2 mean (18 C - T_amb) over cold operating hours", dT_cold, "K", f"energy per start = C_cab[kJ/K] * {dT_cold:.1f} K /3600 kWh; C_cab = NO SOURCE")
add("F2 warm-up energy per start per 1 kJ/K of cab heat capacity", dT_cold / 3600.0, "kWh per (kJ/K) per start", "multiply by C_cab (NO SOURCE) and starts/day")
rho = 101325.0 / (287.05 * (Tmean_op + 273.15))
add("F4 door opening: energy per m3 of cab air exchanged at mean cold-hour dT", rho * 1005 * dT_cold / 3.6e6, "kWh per m3", "multiply by V_exchanged per opening (NO SOURCE) and openings (stops)")
# setpoints seen in the two independent sources: 21 C (Daimler press, eActros 600 cab) and 22 C (Ramesh Babu 2025 target) vs VECTO 18 C
for th in (21.0, 22.0):
    for q in (0.0, 100.0):
        a = H.base_args(G); tot, _ = f(w["T"], w["S"], Q=q, T_heat=th, T_cool=23.0, **a)
        b = H.base_args(G); tot0, _ = f(w["T"], w["S"], Q=q, **b)
        add(f"F-setpoint heating set-point {th:.0f} C instead of 18 C, Q={q:.0f}", (tot[op].sum() - tot0[op].sum()) / 1000, "kWh/yr (operating h)",
            f"{100 * (tot[op].sum() / tot0[op].sum() - 1):.1f} % ; 21 C = Daimler press, 22 C = Ramesh Babu target; HDEV/VECTO uses 18 C (Bob decision 4: not reopened)")
# fuel-heater variant: electricity must not change, fuel power gets the cap and /0.80
fv = R.variant("v_fuel_eff"); a = H.base_args(G); a["hp_share_points"] = [.4, .7, .8, 1, 1]; a["eh_share_points"] = [.2, 0, 0, 0, 0]; a["fuel_share_points"] = [.4, .3, .2, 0, 0]
t1, fh = f(w["T"], w["S"], **a); t2, fp = fv(w["T"], w["S"], **a, fuel_heater_power=30000.0, fuel_eff=0.80)
add("F v_fuel_eff: max |change| of electric HVAC W (must be 0)", float(np.max(np.abs(t1 - t2))), "W", "variant only changes the 2nd return value")
add("F v_fuel_eff: annual fuel energy (heat/0.80, cap 30 kW) vs fuel_heat sum, HD3 shares", float(fp[op].sum() / 1000), "kWh fuel", f"fuel_heat (heat basis) = {float(fh[op].sum()/1000):.1f} kWh; fuel share is 20-30 % between about -3.5 and +5 C in HD3, so most of it falls in the 2 C and -5 C point bands")
with open(os.path.join(HERE, "part_f_effects.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
print("wrote part_f_effects.csv")
