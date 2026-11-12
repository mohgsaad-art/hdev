"""Collects the headline numbers of Parts C and D into summary_effects.csv (effect of each proposed change in kWh and as % of the VECTO
battery-terminal energy of the same run).  Reads the CSVs written by run_part_c.py / run_part_d.py.  Run after those."""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _rows import read_vmod, REPO  # noqa: E402

r3 = pd.read_csv(os.path.join(HERE, "partC3_rule_variants.csv"))
rows = []
for (cyc, load), g in r3.groupby(["cycle", "loading"], sort=False):
    d = read_vmod(cyc, load)
    e_batt = -d["P_REESS_T [kW]"].sum() / 3600.0
    base = g[g.variant.str.startswith("current")].iloc[0]
    for _, r in g.iterrows():
        rows.append(dict(cycle=cyc, loading=load, variant=r.variant, VECTO_battery_terminal_kWh=e_batt, VECTO_aux_kWh=r.VECTO_total_aux_kWh,
                         total_diff_vs_VECTO_kWh=r.total_diff_kWh, total_diff_vs_VECTO_pct_of_aux=r.total_diff_pct,
                         total_diff_vs_VECTO_pct_of_trip_energy=r.total_diff_kWh / e_batt * 100,
                         change_vs_current_kWh=r.total_diff_kWh - base.total_diff_kWh,
                         change_vs_current_pct_of_trip_energy=(r.total_diff_kWh - base.total_diff_kWh) / e_batt * 100, side=r.side))
pd.DataFrame(rows).to_csv(os.path.join(HERE, "summary_effects.csv"), index=False, float_format="%.5f")
df = pd.DataFrame(rows)
pd.set_option("display.width", 250, "display.max_colwidth", 60)
print(df[df.loading == "ReferenceLoad"][["cycle", "variant", "total_diff_vs_VECTO_kWh", "total_diff_vs_VECTO_pct_of_trip_energy", "change_vs_current_kWh"]].to_string(index=False))
print("\nfile written:", os.path.relpath(os.path.join(HERE, "summary_effects.csv"), REPO))
