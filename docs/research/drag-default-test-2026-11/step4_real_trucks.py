"""Step 4: HDEV V0/V1 next to real-truck kWh/km figures.

All real-truck rows are the sourced values from the 22 Oct close-out section 2
(docs/research/inputs/session-closeout-2026-10-22-validation-drivetrain-winter.md).
No new source is added without a link. This is NOT validation where truck, mass or
cycle differ from the E2 (N3, 11.99 t GVW, 9.59 t at reference load, VECTO declaration
Regional/Urban cycles). HDEV figures are Chain S (default) and Chain E, Regional ref.

Writes step4_real_trucks.csv.
"""
import csv
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

# HDEV Chain-S / Chain-E, Regional & Urban reference, from run_steps.py (this branch).
HDEV = {
    "HDEV V0 (no drag), Chain S, Regional ref": dict(kwh_km=0.946, cycle="VECTO RegionalDelivery", mass="9.59 t", note="HDEV, no drivetrain drag"),
    "HDEV V1 (E2 drag), Chain S, Regional ref": dict(kwh_km=0.975, cycle="VECTO RegionalDelivery", mass="9.59 t", note="HDEV, E2 drag table (default)"),
    "HDEV V0 (no drag), Chain S, Urban ref":    dict(kwh_km=0.809, cycle="VECTO UrbanDelivery", mass="9.59 t", note="HDEV, no drivetrain drag"),
    "HDEV V1 (E2 drag), Chain S, Urban ref":    dict(kwh_km=0.850, cycle="VECTO UrbanDelivery", mass="9.59 t", note="HDEV, E2 drag table (default)"),
}

# Real trucks / regressions — 22 Oct close-out section 2 (each already carries a link there).
REAL = [
    dict(source="MAN eTGL (OEM)", kwh_km=0.69, mass="11.99 t GVW", cycle="OEM 'up to' (160 kWh / 235 km)",
         link="https://man.eu/uk/en/trucks/all-models/the-man-etgl/etgl.html", diff_vs_E2="same GVW; spec-sheet best case, route unknown"),
    dict(source="Renault E-Tech D12 [CALC]", kwh_km=0.80, mass="12 t", cycle="176 kWh / 220 km",
         link="https://www.renault-trucks.com/en/newsroom/press-releases/e-tech-d12-and-d14", diff_vs_E2="near E2 GVW; range-based, cycle unknown"),
    dict(source="Renault E-Tech D16 [CALC]", kwh_km=1.14, mass="16.7 t", cycle="375 kWh gross / 330 km",
         link="https://www.renault-trucks.de/sites/default/files/2024-09/Renault%20Trucks%20E-TECH%20D16%20MED%20P4x2_0.pdf", diff_vs_E2="heavier (16.7 t), gross battery"),
    dict(source="Renault D16 test (Moottori)", kwh_km=0.80, mass="empty", cycle="trip computer",
         link="https://moottori.fi/koeajo/maistiainen-renault-trucks-d-16-4x2-e-tech-sahkoa-jakeluliikenteeseen/", diff_vs_E2="empty, cycle unknown"),
    dict(source="DAF XB Electric [CALC]", kwh_km=0.81, mass="12-19 t", cycle="282 kWh / 350 km",
         link="https://www.electrive.com/2023/08/24/daf-trucks-presents-the-daf-xb-electric-truck/", diff_vs_E2="range spans heavier variants"),
    dict(source="Fuso eCanter [CALC]", kwh_km=0.66, mass="7.49 t", cycle="66 kWh usable / ~100 km",
         link="https://www.fleetnews.co.uk/truck/reviews/fuso-ecanter", diff_vs_E2="lighter (7.49 t)"),
    dict(source="Volvo FL heat test", kwh_km=0.73, mass="15 t", cycle="measured, >35 degC",
         link="https://www.volvotrucks.com/en-en/news-stories/stories/2022/march/volvo-electric-fl-truck-heat-test-in-australia.html", diff_vs_E2="heavier (15 t), hot weather"),
    dict(source="Volvo FL fleet guide", kwh_km=1.00, mass="n/s", cycle="200 kWh / 200 km",
         link="(Guide til Flaadeejere, 22 Oct close-out)", diff_vs_E2="mass/cycle not stated"),
    dict(source="NREL Smith Newton (measured DC)", kwh_km="0.79-0.87", mass="~10 t", cycle="measured fleet",
         link="https://www.energy.gov/sites/default/files/2015/10/f27/64238.pdf", diff_vs_E2="older tech, ~10 t"),
    dict(source="Oeko-Institut eActros (measured)", kwh_km="0.67 (>60 km/h), 0.72 (20-60)", mass="19 t", cycle="measured medians",
         link="https://www.oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks-operating-in-Germany.pdf", diff_vs_E2="much heavier (19 t)"),
    dict(source="MAN fleet average (measured)", kwh_km=0.90, mass="mixed", cycle="on-road",
         link="https://www.sustainabletruckvan.com/man-electric-trucks-on-road-consumption/", diff_vs_E2="mixed fleet/cycle"),
    dict(source="Danish fit at 11.99 t", kwh_km=0.796, mass="11.99 t (extrapolated)", cycle="cross-truck regression",
         link="(22 Oct close-out)", diff_vs_E2="regression across trucks, not one truck"),
    dict(source="Liimatainen fit at 11.99 t", kwh_km=0.855, mass="11.99 t", cycle="cross-truck regression",
         link="(22 Oct close-out)", diff_vs_E2="regression across trucks"),
]


def main():
    rows = []
    for name, d in HDEV.items():
        rows.append(dict(source=name, kwh_km=d["kwh_km"], mass=d["mass"], cycle=d["cycle"],
                         comparable="HDEV", note=d["note"]))
    for r in REAL:
        rows.append(dict(source=r["source"], kwh_km=r["kwh_km"], mass=r["mass"], cycle=r["cycle"],
                         comparable="NOT like-for-like (truck/mass/cycle differ)" if "11.99" not in str(r["mass"]) else "near GVW only",
                         note=r["diff_vs_E2"] + "  [" + r["link"] + "]"))
    with open(os.path.join(_HERE, "step4_real_trucks.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["source", "kwh_km", "mass", "cycle", "comparable", "note"])
        w.writeheader()
        w.writerows(rows)
    print("Step 4 — HDEV vs real trucks (see CSV). E2 = N3, 11.99 t GVW, 9.59 t at reference load.")
    for r in rows:
        print(f"  {r['source']:42s} {str(r['kwh_km']):>22s} kWh/km  [{r['mass']}]  {r['comparable']}")
    print("\nNOTE: rows where truck, mass or cycle differ from the E2 are NOT validation.")


if __name__ == "__main__":
    main()
