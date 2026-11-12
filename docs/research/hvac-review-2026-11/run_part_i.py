"""Part I: HDEV (placeholder cab - NOT the measured vehicles, so NOT like-for-like) against the two independent datasets read in full.
 (1) Ramesh Babu et al. 2025 (Chalmers/Volvo, SIMULATED CFD + 0D, electric truck cab), Table 4 p.9: heater rate at -10 C ambient 3.87-4.25 kW (CFD),
     4.07-4.45 kW (0D) for 0-90 km/h; cabin target 22 C (Sec. 5.1, p.12).  [SOURCE full text: research.chalmers.se/publication/545506]
 (2) Daimler Truck press release 25 Feb 2025 (OEM, full page read): average -2 C, cab climate at 21 C = ~5 percentage points of a ~25 % consumption
     increase; battery heating < 1 point.  [SOURCE full text, press text]
Output: part_i_comparison.csv"""
import csv, os
import numpy as np
import hvac_common as H
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
def heat_demand(T, Q, T_heat, g=H.PLACEHOLDER):
    r1 = H.ssm_total_w(np.array([T]), 0.0, T_heat, g["A"], g["U"], g["N"], g["Aw"], (50., 80.), (.65, .8), 17.0, .95, .25, 101325., 287.05, 1005., Q)
    return float(-r1[0])
for label, g in (("PLACEHOLDER cab", H.PLACEHOLDER), ("VECTO bus driver-compartment analogue", H.VECTO_DRIVER_ANALOGUE)):
    for Q in (0.0, 100.0):
        for Th in (18.0, 22.0):
            hd = heat_demand(-10.0, Q, Th, g)
            rows.append(dict(item=f"HDEV heat demand at -10 C, {label}, Q={Q:.0f} m3/h, cab set-point {Th:.0f} C", value_kW=round(hd / 1000, 3),
                             note="heat (thermal) W, before COP; no solar, night"))
for v, cfd, d0 in ((0, 3.87, 4.07), (30, 4.15, 4.32), (60, 4.21, 4.39), (90, 4.25, 4.45)):
    rows.append(dict(item=f"Ramesh Babu 2025 Table 4: heater rate at -10 C, {v} km/h (CFD / 0D)", value_kW=f"{cfd} / {d0}", note="SIMULATED, target 22 C, fresh-air and humidity rules of the paper (Sec 5.3)"))
rows.append(dict(item="[CALC] implied total conductance heater_rate/(22-(-10)) at 0 km/h and 90 km/h (0D)", value_kW=f"{4.07/32*1000:.0f} / {4.45/32*1000:.0f} W/K",
                 note="includes wall + ventilation/fresh air + window losses minus occupant heat; compare placeholder UA 60 W/K (+37 W/K for Q=100)"))
rows.append(dict(item="[CALC] speed effect on heater rate (0 -> 90 km/h)", value_kW=f"CFD +{(4.25/3.87-1)*100:.1f} %, 0D +{(4.45/4.07-1)*100:.1f} %", note="SIMULATED; only the heating load with ventilation as modelled"))
# electric power at -2 C
for Q in (0.0, 100.0):
    tot, _ = H.HVAC_thermal(np.array([-2.0]), 0.0, Q=Q, **H.base_args(H.PLACEHOLDER))
    rows.append(dict(item=f"HDEV electric HVAC at -2 C, night, placeholder cab, Q={Q:.0f}, R-744 HD2, set-point 18 C", value_kW=round(float(tot[0]) / 1000, 3), note="electric W"))
rows.append(dict(item="[CALC] Daimler press: 5 points x E2 Regional 0.9749 kWh/km x 61.2 km/h", value_kW=round(0.05 * 0.9749 * 61.2, 2),
                 note="ONLY an order of magnitude: the eActros 600 is a different truck and the 5 points are relative to its own class-A-tyre consumption; set-point 21 C; not a measurement of E2"))
with open(os.path.join(HERE, "part_i_comparison.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["item", "value_kW", "note"]); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
