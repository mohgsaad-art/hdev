"""Part B3: size of each jump of HVAC_el versus T_amb (placeholder cab, R-744 + el. heater HD2, Q=0 and Q=100), fine grid 0.01 K.
Output: part_b_jumps.csv"""
import csv, os
import numpy as np
import hvac_common as H
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
T = np.round(np.arange(30.0, -15.0, -0.01), 2)
for Q in (0.0, 100.0):
    for S0 in (0.0, 300.0, 800.0):
        tot, _ = H.HVAC_thermal(T, S0, Q=Q, **H.base_args(H.PLACEHOLDER, "R-744", "HD2"))
        d = np.diff(tot)
        for i in np.where(np.abs(d) > 5.0)[0]:
            rows.append(dict(Q_m3h=Q, solar=S0, T_from=T[i], T_to=T[i + 1], HVAC_before_W=round(float(tot[i]), 1), HVAC_after_W=round(float(tot[i + 1]), 1),
                             jump_W_as_T_falls=round(float(d[i]), 1)))
with open(os.path.join(HERE, "part_b_jumps.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
print("wrote part_b_jumps.csv")
