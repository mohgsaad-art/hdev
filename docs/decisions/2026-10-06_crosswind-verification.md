# Crosswind engine — verified against VECTO (6 Oct 2026)

**Status (7 Oct 2026): step F DONE.** Bob's numpy `crosswind_engine` (no loops; args: vehicle_height, v_ref, h_ref, a1, a2, a3, wind_exp, dh, dphi_deg, v_veh_kmh, beta_limit_deg) passes the test cell: max difference vs VECTO Excel 0.00599%. Full table (all wind × 60–105 km/h) runs instantly on Bob's machine → no caching or per-height precompute needed for F; recompute on demand. Output = W1, W2 tables (rows = wind speeds, columns = vehicle speeds); keep the wind/speed arrays as labels. Ranges are call arguments: 60–105 km/h from VECTO; wind range/step is HDEV's choice (top must cover DMI max, never extrapolate).

Sources: VECTO user manual (Cross Wind Correction), `AirDrag.cs`, `VCDV_parameters.csv`, `CrossWindCorrectionCurveReader.cs`, `CrosswindCorrectionVAirBeta.cs`, `Cdv_Generator_VECTO3.2.xlsx` (shipped with VECTO).

## Settled (from source)
- Polynomial gives ΔCdxA in m² (`AirDrag.cs`: `.SI<SquareMeter>()`; Excel adds it to CdxA(0)). So `CdxA_eff(v) = CdxA(0)·W1 + W2`. Only the product CdxA(0) is needed, not Cd and A separately.
- β is in degrees (Excel: `ATAN(..)*180/PI()`, units column `[°]`).
- No clamp at 10° in VECTO: the polynomial is evaluated as-is. With 3 m/s @ 4 m the max β is ~10.3° at 60 km/h (so VECTO never needs a rule — inference, not stated by VECTO).
- Wind profile exponent 0.2; v_wind 3 m/s at h_ref 4 m.
- Height: 10 slices at 5%, 15% … 95% of h_veh (midpoints), averaged equally.
- Direction: 0–180° in 10° steps, weights 5,10,…,10,5 (trapezoid over a half circle; vehicle symmetric about x-axis).
- Speeds computed 60–105 km/h in 5 km/h steps; below 60 km/h the 60 km/h value is used. VECTO lookup interpolates linearly by speed and raises an error on extrapolation.
- Reference vehicle height by vehicle group (Excel `GenericData_VehicleHeight`): groups 1–3 = 3.6/3.75/3.9 m, groups 4,5,7,8,10,11,12 = 4.0 m, group 6 = 3.75 m, group 9 = GVW-dependent (≤10 t 3.6, ≤12 t 3.75, ≤16 t 3.9, else 4.0), groups 13–17 = 3.6 m.
- Coefficients (`VCDV_parameters.csv`): RigidSolo, RigidTrailer, TractorSemitrailer, CoachBus match SR7 Table 10; plus MediumLorriesRigid (−0.0015, 0.0086, −0.00029) and MediumLorriesVan (0.0032, 0.00532, −0.00028).

## Test cell results
- Test 1 (VECTO settings, dh 0.4, 1°, no clamp): within 0.006% of Excel at 60–105 km/h. Excel 60 km/h = 7.04180 m²; 100 km/h = 6.37435 m².
- Test 2: zero wind → W1 = 1, W2 = 0.
- Test 3 (clamp 10°, wind at 10 m, CdxA(0) 5.8, h 4 m): 60 km/h → 6.752 / 7.558 / 8.380 m² at 3 / 5 / 8 m/s; 100 km/h → 6.226 / 6.752 / 7.496 m².
- Test 4: 3 m/s @ 60 km/h equals 5 m/s @ 100 km/h (only wind/vehicle speed ratio matters).

## Yaw above 10° (Danish wind) — DECISION, must be stated in every client report
- The a1–a3 polynomial is a fit valid for 0–10° (SR7). For tractor-semitrailer it peaks near 13° and turns negative above ~19.9° (arithmetic from coefficients) — a fit artefact.
- **Decision (Bob, 6 Oct 2026): clamp β at 10° (hold ΔCdxA at its 10° value), via argument `beta_limit_deg` (None = VECTO behaviour, no clamp).** This deviates from VECTO and must appear transparently in the report's assumptions list.
- Report wording: "Above 10° yaw, ΔCdxA is held at its 10° value. VECTO's yaw polynomial is only valid 0–10° and no sourced curve with coefficients exists above that. CFD (Askerdal et al. 2024) indicates drag continues to rise, so this likely underestimates air drag in strong wind at low speed."
- Alternatives examined (not adopted): linear continuation with 10° slope (0.207 m²/°) and regression of CdxA_eff in wind speed. At 60 km/h, 7 m/s: clamp 8.11, linear 8.68, regression 9.52 m² — spread ~17%, none sourced.
- Literature: Askerdal, Fredriksson, Laine (2024), Vehicle System Dynamics, https://research.chalmers.se/publication/535965 — STAR-CCM+ CFD to 60°, CdA rises with angle (per text summary; check Fig. 3b), model forms but no coefficients. NASA TM-2006-213489: tests only to ±14°, plots only.
- Excel uses `atan(y/x)`; Bob uses `atan2`. Same result while v_veh > v_wind.
