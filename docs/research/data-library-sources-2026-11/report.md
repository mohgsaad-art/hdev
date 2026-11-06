# EV Scope data-library sources — pass 3 report (6 Nov 2026)

Written for Bob. Plain English. Short sentences.

## Top-line (read this first)

1. The input files the brief points to are **not in the repo**. No pass-1,
   pass-2, Gemini, manual-fetch-list, or findings-EEA file; no `inputs/` or
   `fetched/` folder. I worked from the primary PDFs and CSVs that *are* in
   `docs/research/`, plus the VECTO repo and the web.
2. **What we can fill now from open, commercial-safe sources:** vehicle identity
   (make/model/class/VECTO group/architecture), masses and all Danish/EU legal
   limits, installed and usable battery kWh, nominal voltage and continuous motor
   power (all from EEA, CC-BY), car/van WLTP Wh/km and range, the CdxA bin, and
   the full VECTO generic/standard aux and component values (EUPL-1.2).
3. **One catch with the EEA battery data:** the battery, e-machine and IEPC
   tables are **hashed**. They give installed/usable kWh and voltage for 8,020
   BEV configs, but there is **no make/model** in the files we have. You need the
   EEA `vehicle` header to join. That is the single highest-value fetch.
4. **What needs OEM documents (cite-only):** chemistry, per-pack kWh, battery
   mass, charging curve, motor peak kW/Nm, gear ratios, ePTO electrical and
   mechanical kW, reefer cooling capacity + COP, mixer/crane/body energy.
5. **What has no public source at all:** battery internal resistance and OCV
   curve (only VECTO generic exists), battery heater kW, CIF kWh/km (private),
   per-model efficiency/torque maps, refuse/tipper/sweeper body energy, and the
   tyre rolling-resistance coefficient (EPREL gives a class only).
6. **Field coverage:** of 46 field×class cells scored — 11 full, 22 partial,
   13 none.
7. **All 11 conflicts are settled or dispositioned** from primary sources; see
   `conflicts.md`. Four were nailed from documents in the repo (eEconic battery
   and ePTO, Liebherr mixer, the Danish weight rule). One correction: COM(2025)
   589 is a **tolling** amendment, not a ZEV weights & dimensions proposal.
8. **82 extracted values** recorded, 66 opened from primary sources
   (`extracted_values.csv`). **66 catalogue rows** — 20 verified, 8 secondary,
   38 to fetch — every section-4 source and OEM has a row with the search used.

### Top 10 sources to start the library with
1. EEA HDV RP2024-25 relational electric tables (battery/e-machine/IEPC) — CC-BY,
   installed+usable kWh, voltage, continuous kW. *Plus the `vehicle` header to join.*
2. EEA `my_zev_configs` — CC-BY, make/model + PEVArchitecture + CdxA + axle ratio + masses.
3. VECTO repo generic vehicles + declaration aux tables — EUPL-1.2, the only open
   source for motor curves, battery Ri/OCV, and PEV aux demands.
4. Danish BEK 1447/2025 (+ 1415/2023 history) — public law, the weight/length limits.
5. Volvo FH/FM ESS fact sheet (PCE4) — installed vs usable per pack count, NCA, mass.
6. DAF XD Electric BBI spec sheet — **public domain**, motor/battery/ePTO/charging/masses.
7. Mercedes eEconic product sheet — refuse-truck battery, ePTO, masses.
8. EEA cars & vans CO2 datasets — CC-BY, M1/N1 Wh/km + range.
9. RDW open data (CC0) — NL registry, incl. the fuel/energy sibling dataset (to fetch).
10. Liebherr ETM + Carrier Vector eCool — body ePTO (mechanical) and reefer (electrical input).

---

## Detail by data category

### Battery
- Open: EEA `battery` table gives **installed** (TotalStorageCapacity) and
  **usable** (TotalUsableCapacityInSimulation) kWh and **nominal voltage** for
  8,020 configs (6,366 standard-values, 1,654 measured). Installed spans 1–674
  kWh, usable 1–576 kWh, voltage 348–763 V. But hashed — no make/model yet.
- Important: usable is **not** a fixed fraction of installed. Volvo PCE4 runs
  65%→70% across 2→6 packs (180→117 … 540→380). MAN is 480 of 534 (90%). EEA
  standard-values cluster at ~85.5% but real configs span 13%–86%. Store both,
  derive neither.
- OEM-cite: chemistry (Volvo NCA, eActros LFP, MAN NMC), per-pack kWh (Volvo 90,
  MAN 89 gross/80 net, Volvo FL GEN2 66 / GEN3 94), pack mass (Volvo ~500 kg).
- No public source: internal resistance, OCV, heater kW (VECTO generic only).

### Drivetrain
- Open: architecture (E2/E3/E4/IEPC) and continuous kW from EEA; axle ratio and
  gears count from EEA config export.
- OEM-cite: peak kW/Nm (eActros 400/600 kW; DAF 1500/2400 Nm), motor count, ratios.
- VECTO generic (EUPL): continuous vs peak torque, overload time, drag, maps.

### Auxiliaries
- Open: VECTO declaration tables give standard demands in Watts by mission/group,
  and flag which apply to PEVs (electric steering pump, electric air compressor,
  electric system). EEA records only the technology **code**.
- Bus HVAC from VECTO: driver ~5 kW, passenger 0.25–0.55 kW per config.
- Gap: real OEM aux kW, heat-pump vs PTC split, seasonal values → fetch Solaris,
  NOW, Oeko-Institut.

### PTO / body
- OEM-cite and partial: ePTO electrical (eEconic 52/30 kW @50% SoC; DAF 25 & 90
  kW @650 V), ePTO mechanical (Liebherr mixer 125/60 kW), reefer electrical input
  (Carrier 19 kW, 19.2 kWh). Keep electrical input and mechanical output apart;
  keep reefer input apart from cooling capacity.
- Gap: refuse compactor/lift, crane, tipper, sweeper, hook-lift energy; reefer
  cooling capacity + COP. ISO 24162 is the test **method** only (restricted).

### Masses and limits
- Best-covered open category. EEA masses (CorrectedActualMass, TPMLM) + the
  Danish BEKs. Settled: from 1 Jan 2026 a 2-axle lorry in DK is 20,000 kg flat,
  **no** extra ZEV +2 t (the old bonus is gone). 7+ axle 58 t and 4.20 m from
  1 Jan 2027.

### Aero and tyres
- Open: EEA gives the CdxA **bin** (A1–A24), not the exact m². No frontal area.
- Tyres: EPREL gives the label **class** only. RRC coefficient and C3 coverage
  need the EPREL API (key request) — open item.

### Consumption
- Open: car/van WLTP Wh/km + range (EEA CC-BY) for M1/N1.
- CIF kWh/km is per-vehicle and private — no public source (settled).
- Measured truck kWh/km with full conditions is thin: ICCT ~0.92–1.5 kWh/km
  (published unit is a typo for kWh/100 km), PVI refuse 1.7 kWh/km. Fetch RISE,
  Oeko, TNO, NAF, Enova for measured data with mass/temperature/cycle/sample.

---

## Files in this folder
- `catalogue.csv` — every source and OEM, incl. "not found" with the search used.
- `field_coverage.csv` — field × class → best source + coverage.
- `extracted_values.csv` — every value with link, page/table and quote.
- `vecto_generic_bev.md` — VECTO generic BEV + aux, with file/line refs.
- `conflicts.md` — all 11 conflicts + new ones, both links + a verdict.
- `library_schema.md` — the 8 proposed tables.
- `bob_to_fetch.md` — links to fetch next.
- `report.md` — this file.
