"""Self-checks: confirm we call Bob's crosswind_engine correctly, and that the
.vdri readers give sane totals. No pitch numbers here -- just trust-building.

Reproduces crosswind-verification doc Test 3 (clamp 10 deg, wind at 10 m,
CdxA(0)=5.8, h=4 m): 60 km/h -> 6.752 / 7.558 / 8.380 at 3/5/8 m/s;
100 km/h -> 6.226 / 6.752 / 7.496 m^2.

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/00_selfcheck.py
"""
import numpy as np

from vecto_data import (crosswind_engine, read_vdri, DH, DPHI_DEG,
                        CROSSWIND_COEFFS)


def cdxa_eff(cdxa0, coeff_set, veh_h, v_ref, h_ref, v_veh_kmh, clamp):
    a1, a2, a3 = CROSSWIND_COEFFS[coeff_set]
    W1, W2 = crosswind_engine(veh_h, v_ref, h_ref, a1, a2, a3,
                              0.2, DH, DPHI_DEG, v_veh_kmh, clamp)
    return cdxa0 * W1 + W2


def main():
    print("=== Crosswind Test 3 reproduction (TractorSemitrailer, CdxA0=5.8, h=4) ===")
    for vkmh, exp in [(60, (6.752, 7.558, 8.380)), (100, (6.226, 6.752, 7.496))]:
        got = cdxa_eff(5.8, "TractorSemitrailer", 4.0,
                       np.array([3.0, 5.0, 8.0]), 10.0, np.array([float(vkmh)]), 10.0)
        got = got[:, 0]
        print(f"  {vkmh} km/h: got {got.round(3)}  expected {exp}")
        # doc values are rounded to 3 dp and may use a slightly different slice
        # count; a match to ~0.1% confirms we drive the engine correctly.
        assert np.allclose(got, exp, rtol=0.0015), "crosswind mismatch!"
    print("  OK -- crosswind engine called correctly (match to ~0.1%; doc values"
          " are rounded to 3 dp).\n")

    print("=== Zero-wind sanity: W1=1, W2=0 ===")
    a1, a2, a3 = CROSSWIND_COEFFS["TractorSemitrailer"]
    W1, W2 = crosswind_engine(4.0, np.array([0.0]), 10.0, a1, a2, a3,
                              0.2, DH, DPHI_DEG, np.array([80.0]), 10.0)
    print(f"  W1={W1[0,0]:.6f}  W2={W2[0,0]:.6f}")
    assert np.isclose(W1[0, 0], 1.0) and np.isclose(W2[0, 0], 0.0)
    print("  OK\n")

    print("=== VDRI cycle totals ===")
    for f in ["MunicipalUtility.vdri", "RegionalDelivery.vdri",
              "LongHaul.vdri", "UrbanDelivery.vdri"]:
        c = read_vdri(f)
        dist_km = c["s"].max() / 1000.0
        n_stops = int(((c["stop_s"] > 0)[1:]).sum())  # exclude row 0
        vmax = c["v_kmh"].max()
        print(f"  {f:24s} dist={dist_km:7.2f} km  rows={len(c['s']):5d}  "
              f"stops(>0,excl row0)={n_stops:3d}  vmax={vmax:.0f} km/h")


if __name__ == "__main__":
    main()
