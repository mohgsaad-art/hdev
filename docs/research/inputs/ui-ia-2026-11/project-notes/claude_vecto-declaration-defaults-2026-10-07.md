# VECTO declaration data for defaults.py (7 Oct 2026)

Source: VECTO repo `VectoCore/VectoCore/Resources/Declaration/` (stable branch), files pasted by Bob: `SegmentTable.csv`, `Body_Trailers_Weights.csv`, part of `Payloads.csv`.

## Mission cycles available (`Resources/Declaration/MissionCycles/`)
Trucks: LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction (.vdri). Buses: HeavyUrban, Urban, Suburban, Interurban, Coach (.vdri). Plus MunicipalUtility_PTO_generic .vptoc/.vptol/.vptoel (refuse-body PTO data; meaning of each ending not yet checked). Matches SR7 §4.3.5.1. HDEV rule: VECTO files are never altered.

## Payload defaults (SegmentTable.csv, mission columns, kg "low/reference")
- Group 4 (rigid 4x2 >16 t): LH 1900/14000; RD 900/4400; UD 900/4400; MU 600/3000; Constr 900/4400.
- Group 5 (tractor 4x2 >16 t): LH 2600/19300; LH EMS 3500/26500; RD 2600/12900; RD EMS 3500/17500; UD 2600/12900; Constr 2600/12900.
- Group 9 (rigid 6x2): LH 2600/19300; LH EMS 3500/26500; RD 1400/7100; RD EMS 3500/17500; MU 1200/6000; Constr 1400/7100.
- Group 10 (tractor 6x2): LH 2600/19300; LH EMS 3500/26500; RD 2600/12900; RD EMS 3500/17500; Constr 2600/12900.
- Group 11 (rigid 6x4): as group 9 (MU 1200/6000). Group 12 (tractor 6x4): as group 10. Group 16 (rigid 8x4): LH 2600/19300, EMS 3500/26500, RD 1400/7100, RD EMS 3500/17500, Constr 2600/12900.
- Groups 1, 1s, 2, 3 and medium lorries 51–56: pc10/pc50 (pc75 for group 2 LH) = percentage functions of GVW from `Payloads.csv` (R = rigid, V = van). Payloads.csv rows seen so far (GVW kg → 10% / 50% / 75% payload kg): 3500 → 80/420/630; 7400 → 240/1210/1840; 7500 → 250/1250/1900; 16000 → 920/4600/6900 (may be incomplete; presumably interpolated by GVW — interpolation method not yet confirmed from code).
- These match SR7 Table 8 (e.g. group 5 LH 19.3 t / 2.6 t).

## Other defaults found in SegmentTable.csv
- Reference vehicle height [m]: groups 1/1s 3.6; 2 3.75; 3 3.9; 4,5,7,8,9,10,11,12 4.0; 6 3.75; 13,14,15,16 3.6; 17 3.6 (8x6) / 4.0 (8x8); medium lorries 51/53/55 3.5; vans 52/54/56 2.9.
- Crosswind coefficient set depends on vehicle group AND mission: e.g. group 5 long haul TractorSemitrailer, EMS RigidTrailer, other TractorSemitrailer; group 4/9/11/16 long haul RigidTrailer, other RigidSolo; medium lorries MediumLorriesRigid; vans MediumLorriesVan.
- .vacc file: Truck.vacc for all trucks (official accel/decel curve in `Resources/Declaration/VACC/`).
- CdxA_Default [m²]: e.g. group 1–1s 7.1, 2 7.2, 3 7.4, 4 8.4, 5 8.7, 9 8.5, 10 8.8, 11 8.5, 12 8.8, 16 9.0, medium rigid 5.8, van 2.5; CdxA_Construction column separately (e.g. group 5 7.2). Likely the standard values for vehicles without a measured air-drag certificate (Reg. 2017/2400 Annex VIII Appendix 7) — to verify before use.
- Design speed 85 km/h for all trucks.
- Axle load shares per mission are in the table (needed later for VECTO's per-axle rolling resistance).

## Body / trailer masses (Body_Trailers_Weights.csv), curb mass kg
B-II 800; B1 1600; B2 1900; B3 2000; B4 2100; B5 2200; BT1 2000, BT2 3230, BT3 4355 (tipper bodies, construction); MU4 6000, MU9 6750, MU11 6750 (refuse bodies); T1 3400 (max 10500); T2 5400 (max 18000); ST1 7500 (max 24000; "fully loaded GVM of tractor semitrailer combination = 40000 kg"); Dolly 2500 (EMS only); STT1 6100, STT2 5600 (tipper semitrailers). Also cargo volume and trailer ΔCdxA for long haul (T1 1.3; T2 1.5/1.5; ST1 0/2.1 first/second trailer).
- Vehicle mass in VECTO = vehicle curb mass + body/trailer curb mass + payload (payload capped by GVWR / 40 t / 60 t EMS, SR7 §4.3.5.4).
