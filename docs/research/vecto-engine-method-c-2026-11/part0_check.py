"""Part 0: run VECTO on Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto and compare with Bob's 22 Oct numbers
(Regional 1.050, Urban 0.840 kWh/km, reference load, battery terminals = (E_REESS_T_dischg - E_REESS_T_chg) / distance).
Usage: python part0_check.py <dir with BEV_E2.vsum>  [seconds_parallel seconds_sequential]
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
BOB = {("RegionalDelivery", "ReferenceLoad"): 1.050, ("UrbanDelivery", "ReferenceLoad"): 0.840}


def main(d):
    rows = [r for r in csv.reader(open(os.path.join(d, "BEV_E2.vsum"), encoding="utf-8-sig")) if len(r) > 5]
    h = rows[0]; ix = {n: i for i, n in enumerate(h)}
    # vsum order = LongHaul low/ref, RegionalDelivery low/ref, UrbanDelivery low/ref (the console lists the same order)
    names = [(c, l) for c in ("LongHaul", "RegionalDelivery", "UrbanDelivery") for l in ("LowLoading", "ReferenceLoad")]
    out = []
    for (c, l), row in zip(names, rows[2:] if rows[1][0].startswith("[") else rows[1:]):
        km = float(row[ix["distance [km]"]])
        term = (float(row[ix["E_REESS_T_dischg [kWh]"]]) - float(row[ix["E_REESS_T_chg [kWh]"]])) / km
        fin = float(row[ix["EC_el_final [kWh/km]"]])
        ref = BOB.get((c, l))
        out.append(dict(cycle=c, loading=l, distance_km=km, terminal_kwh_km=round(term, 4), EC_el_final_kwh_km=fin,
                        bob_22_oct_kwh_km=ref if ref else "", diff_pct=round(100 * (term / ref - 1), 3) if ref else ""))
    with open(os.path.join(HERE, "part0_e2_reproduction.csv"), "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1])
