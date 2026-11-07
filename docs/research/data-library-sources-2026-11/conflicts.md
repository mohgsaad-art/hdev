# Open conflicts — verdicts (research pass 3, 6 Nov 2026)

Rules followed: both sides are listed, nothing is picked silently, every verdict
cites a link, a page/table and the exact quote. Facts and inferences are on
separate lines. `[V]` = I opened the primary source. `[C]` = secondary.
`[BOB]` = could not open; URL given.

A note Bob should read first: the input files named in the brief
(`research-pass1-...md`, `research-pass2-...md`, `gemini-research-...txt`,
`manual-fetch-list-...md`, `findings-eea-...md`) and the `docs/research/inputs/`
and `docs/research/inputs/fetched/` folders are **not in the repo** on this
branch or any other. I worked from the primary PDFs and CSVs that *are* present
in `docs/research/` (the eEconic sheet, Liebherr ETM, Carrier reefer, the Volvo
battery sheet, the Scania BEV booklet, both Danish BEKs, ISO 24162, COM 2025/589,
the EEA electric CSVs and table definitions) plus the VECTO repo and the web.
Where a conflict needed a file I did not have, I say so and mark it `[BOB]`.

---

## Conflict 1 — eEconic battery: 336 kWh installed vs 3×~105 = 315 kWh. Usable?

**Verdict: 336 kWh installed is correct and is the OEM figure. Usable kWh is not stated.** `[V]`

- Fact: Mercedes-Benz eEconic product sheet, p.3 technical-data table:
  "Installed battery capacity — **336 kWh** with three battery packs".
  Source id `eeconic_sheet`, `E_Produktblatt_eEconic_ENG_screen.pdf`, p.3.
  Brochure date 15.11.2021 (p.4). OEM claim.
- Fact: the sheet gives no usable-kWh figure. It footnotes (p.3, note **)
  "Nominal capacity of new battery ... may vary depending on use case".
- Inference `[INFERENCE]`: 336 / 3 = 112 kWh per pack installed, not 105. The
  "3×105 = 315" figure is a different (earlier) pack or a rounded external
  estimate; it is not in this sheet. Do not carry 315 as the installed value.
- To get usable: no public Mercedes document I could open states eEconic usable
  kWh. `[BOB]` — ask Mercedes for the VECTO `TotalUsableCapacityInSimulation`
  for the eEconic, or read it from its EEA `battery` record once the make/model
  join (see conflict notes on EEA) is available.

## Conflict 2 — eEconic ePTO: ~30/~52 kW electrical @50% SoC vs 31/55 mech vs eWorX 33/58

**Verdict: ~52 kW max / ~30 kW continuous is the OEM figure, stated as electrical
at 50% SoC. The 31/55 and 33/58 figures are a different basis and should not be
mixed with it.** `[V]`

- Fact: eEconic sheet, p.3 table: "ePTO High Power (max./cont.) — **~52 kW / ~30 kW at 50 % SOC**".
  Source id `eeconic_sheet`, p.3. OEM claim, 15.11.2021.
- The sheet labels this ePTO figure by SoC (50%), which is the electrical side.
- The 31/55 kW ("mechanical") and the ZF eWorX 33/58 kW are not in this sheet; I
  could not open a primary ZF eWorX document, so I cannot confirm their basis.
  `[BOB]` — ZF eWorX data sheet, to confirm whether 33/58 kW is electrical input
  or mechanical output.
- Keep electrical input and mechanical output on separate lines in the library.

## Conflict 3 — DAF XD torque: 930/1,370 Nm (daf.global) vs 1,500/2,400 Nm (electrive)

**Verdict: 1,500 Nm and 2,400 Nm are DAF's own stated maximum motor torques
(EX-D1 / EX-D2). The 930/1,370 Nm pair is not DAF's stated motor torque.** `[C]` + `[V]` spec sheet

- Fact: DAF (daf.global, XDC/XFC Electric page): the PACCAR "EX-1 and EX-2"
  e-motors have "maximum torques of 1500 Nm and 2400 Nm, respectively." `[C]`
  (OEM site, snippet).
- Fact: DAF press release 13-01-2026 (daf.com): XG/XG+ Electric use "the most
  powerful PACCAR EX D2 electric motor ... a torque of 2,400 Nm." `[C]` OEM.
- Fact: DAF BBI specification sheet (public domain, `dafbbi.com`,
  `TSXHEN991G0100AAAA202545.pdf`, dated 10-07-2025) lists the XD Electric with
  PACCAR EX-D2 at 270/310/350 kW. `[V]` (I downloaded and read it); the torque
  line did not extract cleanly from the PDF text layer.
- Inference `[INFERENCE]`: 1,500 Nm = smaller EX-D1 motor, 2,400 Nm = larger
  EX-D2. The 930/1,370 Nm pair is likely a per-gear or at-wheel figure, or an
  error; it does not match DAF's published motor torque.
- `[BOB]`: if you need the exact continuous-vs-peak split, the DAF BBI sheet PDF
  needs OCR of its torque cell, or request DAF's XD Electric technical infosheet.

## Conflict 4 — DAF ePTO: 25/90 kW vs 60/100 kW added?

**Verdict: both the 25 kW and the 90 kW ePTO sockets are current options. I found
no primary evidence of 60/100 kW options on the XD BBI sheet.** `[V]`

- Fact: DAF BBI spec sheet (`TSXHEN991G0100AAAA202545.pdf`, 10-07-2025) lists two
  ePTO options: "E-PTO socket 650V DC < **90 kW**" (option 04320) and
  "E-PTO socket 650V DC < **25 kW**" (option 01809). Source id `daf_bbi_xd`, p.1. `[V]`
- Both are the electrical socket rating (650 V DC), not mechanical output.
- No 60 kW or 100 kW ePTO option appears on this sheet.
- `[BOB]`: if electrive's "60/100 kW added" (Jan 2026) refers to a newer sheet,
  re-pull the 202625 revision of the BBI sheet and check the PTO section.

## Conflict 5 — MAN chemistry NMC vs LFP; usable 480 of 534 vs "534 usable"

**Verdict: MAN BatteryPack is NMC, not LFP. 534 kWh is GROSS; 480 kWh is NET/usable.
"534 usable" is wrong.** `[C]` (multiple, consistent with MAN's own statement)

- Fact: MAN's EnergyDecentral 2024 statement, reported verbatim by several
  outlets: the MAN BatteryPack is "based on nickel-manganese-cobalt (NMC)
  batteries"; one pack "stores 89 kWh of energy, of which 80 kWh can be used."
  Sources: constructionbriefing.com, powertraininternationalweb.com,
  electrive.net (DE), gagadget.com (FR). `[C]`
- Fact: 6 packs → "up to 534 kWh gross (480 kWh net)"
  (powertraininternationalweb.com; electrive.com). `[C]`
- Fact: gen-2 eTGX (electrive.com, 14-09-2026): each new pack 92 kWh gross /
  88 kWh net. `[C]`
- The "LFP" claim (madeingermany.de) is contradicted by MAN's own NMC statement.
- The "534 usable" claim (electrive) confuses gross with net; 480 is net.
- `[BOB]`: MAN eTGX/eTGS/eTGL technical data sheet (MAN press/portal) for the
  per-pack nominal voltage, Ah, mass and MCS rating — not in any doc I opened.

## Conflict 6 — Volvo FL battery: 175–565/3–8 packs vs 280–565/3–6 packs

**Verdict: the Volvo FL/FE battery fact sheet shows 3–6 packs, GEN2 200–395 kWh and
GEN3 280–565 kWh. The "175 kWh" and "8 packs" are not in this fact sheet.** `[V]`

- Fact: Volvo battery fact sheet (`2BATT170_Eng_05_331735919.pdf`, 2022-09-12,
  Version 05), p.3: GEN2 packs are 66 kWh each, GEN3 94 kWh each. FL/FE sales
  variants: ESS200K/265K/330K/395K (GEN2, 3/4/5/6 packs) and
  ESS280K/375K/470K/565K (GEN3, 3/4/5/6 packs). Source id `volvo_batt_factsheet`, p.3. `[V]`
- So FL GEN3 = 3–6 packs, 280–565 kWh; FE is limited to 3–4 packs.
- The "175 kWh / 8 packs" wording matches neither GEN2 nor GEN3 in this sheet.
- Inference `[INFERENCE]`: the "175–565 / 3–8" range on the global page probably
  mixes the smaller FE and a marketing round-off; trust the fact-sheet table.
- Note: this sheet is the older PCA3/PCA4 FL/FE line. The newer heavy FH/FM line
  (conflict 12) is the PCE4 NCA battery at 90 kWh/pack.

## Conflict 7 — Liebherr ETM peak: 120 kW (p.5) vs 125 kW (p.7)

**Verdict: 125 kW peak / 60 kW continuous (technical-data table, p.7) is the precise
figure. 120 kW (p.5 prose) is a rounded value. Both are mechanical drum-drive power.** `[V]`

- Fact: Liebherr ETM brochure (`electric-truck-mixer-etm.pdf`, Lacher LMT_8203,
  dated 04.22), p.5 prose: "a peak power of **120 kW**, which can power drum
  sizes up to 12 m³." Source id `liebherr_etm`, p.5. `[V]`
- Fact: same brochure, p.7 technical-data table: "Drive power — **125 kW peak
  power / 60 kW continuous power**"; "Battery capacity 32 kWh"; "Operating
  voltage 650 Volt DC". Source id `liebherr_etm`, p.7. `[V]`
- Both describe the electric drum drive (mechanical output). 125/60 kW is the
  table value; 120 kW is the rounded prose value. Use 125/60 kW.
- Charging: 22 kW, <1 h, 400 V / 32 A Type 2; generator charges while driving (p.5).

## Conflict 8 — Frederiksberg PVI e-RCV: 1.7 vs 2.25 kWh/km in collection

**Verdict: 1.7 kWh/km is sourced (2013 trade-press pilot). The 2.25 kWh/km figure
has no primary source I could find.** `[C]` + `[BOB]`

- Fact (per the brief's summary of the 2013 Varebilogtransport.dk article, which
  is not in the repo): 255 kWh pack, 80% usable = 204 kWh; collection range
  ~120 km → 204/120 = **1.7 kWh/km**. `[C]` trade press, 2013, one pilot truck.
- I could not locate any primary document giving **2.25 kWh/km**. Web search for
  the Frederiksberg/PVI figures returned only the Wikipedia PVI entry
  (255 kWh pack, 9 t payload) and unrelated noise.
- Inference `[INFERENCE]`: 2.25 kWh/km would be a worst-case (winter / heavier
  route) number, probably from a later municipal (ARC / Frederiksberg) readout,
  not the 2013 article.
- `[BOB]`: find the origin of 2.25 kWh/km — likely an ARC or Frederiksberg
  operational report; give the document so it can be tagged by season and load.

## Conflict 9 — ICCT Aug 2025 "92 to 150 kWh/km" — typo?

**Verdict: yes, a unit error. It should read kWh/100 km (0.92–1.5 kWh/km).** `[C]` + `[INFERENCE]`

- Fact: ICCT publication page (theicct.org, "Real-world use cases for
  zero-emission trucks: Heavy tractor-trailers ...", 6 Aug 2025): "Energy
  consumption of the trucks in this study ranged from **92 to 150 kWh/km** and
  was on average 65% lower than ... equivalent diesel trucks." `[C]`
- Inference `[INFERENCE]`: 92 kWh/km is physically impossible for a 40 t
  tractor-trailer (it would empty a 500 kWh pack in ~5 km). A 65%-lower-than-
  diesel 40 t e-tractor sits near 1.0–1.5 kWh/km, i.e. 100–150 kWh/100 km. The
  unit is a typo for **kWh/100 km**; read 92–150 kWh/100 km = 0.92–1.5 kWh/km.
- `[BOB]`: confirm from the ICCT report body (ID-359 PDF) which uses the correct
  unit in its tables; link `https://theicct.org/wp-content/uploads/2025/08/ID-359-%E2%80%93-EU-goods-transport_report_final.pdf`.

## Conflict 10 — Danish ZEV +2 t (BEK 1415/2023) vs new 20 t two-axle (BEK 1447/2025)

**Verdict: they do NOT stack. The new flat 20,000 kg two-axle limit (BEK 1447/2025)
replaces the old 18,000 kg + 2,000 kg ZEV bonus. The two-axle ZEV bonus is gone.** `[V]`

- Fact: BEK nr 1415 af 30/11/2023 (now *Historisk*), `B20230141505.pdf`, §22 stk.2:
  nr.1 two-axle motor vehicle (except bus) = **18,000 kg**; nr.3 two-axle lorry
  not in a combination, zero-emission, "forhøjes den tilladte vægt med den ekstra
  vægt af nulemissionsteknologien, **dog højst 2.000 kg**." So 18,000 + 2,000 =
  20,000 kg. Source id `bek_1415_2023`, p.7–8. `[V]`
- Fact: BEK nr 1447 af 27/11/2025, `DG1229.pdf`, §21 stk.2 nr.1: "For lastbil med
  to aksler: **20.000 kg**." — a single flat value with **no** alternative-fuel
  or ZEV bonus line for two-axle lorries. Source id `bek_1447_2025`, p.6-7. `[V]`
- Fact: BEK 1447/2025 keeps a ZEV/alternative-fuel allowance only for **length**
  (§ for lorry+semitrailer combinations), not for two-axle total weight.
  `DG1229.pdf`, length section (the "nulemissionsteknologi ... forøges den
  tilladte længde" clause). `[V]`
- Fact: entry into force 1 Jan 2026 (§38 stk.1); §21 stk.2 nr.9 (7+ axle, 58,000
  kg) and §13 apply from 1 Jan 2027 (§38 stk.2). `DG1229.pdf`, p.8. `[V]`
- So for a two-axle BEV refuse truck in Denmark from 1 Jan 2026 the ceiling is
  20,000 kg regardless of drivetrain; there is no extra +2 t on top.
- (Conflict 8b in the brief = same issue; `c54ce48d-B20230141505.pdf` is BEK
  1415/2023, confirmed above.)

## Conflict 11 — EEA PEVArchitecture: VECTO input or EEA-added, and which release

**Verdict: PEVArchitecture is a VECTO declaration input (the PEV drivetrain
architecture: E2/E3/E4/IEPC), surfaced in the EEA RP 2024-25 relational release /
config export. It is present in the 2024 data, not in the 2019-2023 flat file.** `[V]`

- Fact: `my_zev_configs.csv` (the RP 2024-25 config export present in the repo)
  has a `PEVArchitecture` column with values **E-IEPC (2378), E3 (247), E2 (192)**
  and NaN (3318). Source id `eea_my_zev_configs`. `[V]`
- Fact: the 2019-2023 flat-file schema (`HDV-tabledefinition (1).xlsx`, 464 rows)
  has **no** PEVArchitecture or battery/kWh columns — it is a diesel/fuel schema
  (Engine_*, WHTC/WHSC, *_FuelConsumption_*). Source id `eea_hdv_tabledef`. `[V]`
- Inference `[INFERENCE]`: PEVArchitecture mirrors the VECTO powertrain-
  architecture classification (E2/E3/E4 axle layouts, IEPC) that the
  manufacturer declares; EEA carries it through from the VECTO input/VIF, it is
  not an EEA-invented field. The 3318 NaN rows are mostly N3 tractors where the
  field was not populated in this export.

## Conflict 12 — Volvo FM installed 360–540 kWh vs usable "up to 460 kWh"

**Verdict: on the current PCE4 FM/FH, 540 kWh installed → 380 kWh usable (ESOP-R,
6 packs). The "up to 460 kWh usable" is the NEW 2026 Aero generation, not PCE4. Do
not assume a fixed ratio — usable differs by generation and ESOP variant.** `[V]`

- Fact: Volvo traction-battery fact sheet
  (`ESS180K,ESS270K,ESS360K,ESS450K,ESS540K_Eng_010_338907029.pdf`, stpi.it.volvo.com,
  2024-12-02, Version 10, PCE4), p.1: chemistry is **lithium-ion NCA**
  (LiNiCoAlO2); p.2: 90 kWh nominal per battery, 137.8 Ah, ~500 kg, 2–6 batteries
  = 180–540 kWh installed; "the useable battery energy is lower than the
  installed nominal energy." Source id `volvo_ess_pce4`. `[V]` (downloaded & read)
- Fact: same sheet, p.4 table — installed vs maximum usable:
  180→117, 270→183, 360→250, 450→309, **540→380** kWh. Source id `volvo_ess_pce4`, p.4. `[V]`
  (that is 65%→70% usable, rising with pack count; NOT a flat 85%.)
- Fact: ESOP-R = 380 kWh usable @ 6 packs (standard); ESOP-P (NL/LUX, 23 t cert) =
  369 kWh usable @ 6 packs. Source id `volvo_ess_pce4`, p.3. `[V]`
- Fact: thedriven.io (16 Apr 2026, quoting Volvo): the **new** Aero Electric has
  "on-board energy of up to 540 kWh, and Usable Battery Energy (UBE) of up to
  460 kWh." `[C]` — this is the 2026 range, a different battery, not PCE4.
- So 460 kWh usable belongs to the 2026 Aero pack (540 installed), while the 2024
  PCE4 pack gives 380 usable for the same 540 installed. Tag by generation.
- `[BOB]`: the 2026 Volvo electric-range fact sheet (per-pack installed vs UBE for
  the Aero generation) to confirm the 460 kWh figure's pack count.

---

## New conflicts / corrections found in pass 3

### N1 — COM(2025) 589 is NOT about ZEV weights & dimensions
- The brief's fetch list calls `f9e6fc4d-COM_2025_589.pdf` "Commission proposal ...
  what changes for ZEV weights/dimensions." It is not.
- Fact: `COM_2025_589.pdf`, p.1: "COM(2025) 589 final, 2023/0134 (COD) — Amended
  proposal ... amending Directive 1999/62/EC [road charging/tolls], Council
  Directive 1999/37/EC and Directive (EU) 2019/520 as regards the **CO2 emission
  class of heavy-duty vehicles with trailers** and clarifying ... certain
  provisions", Brussels 2.10.2025. Source id `com_2025_589`, p.1. `[V]`
- It is a tolling / road-charging simplification (74 mentions of toll/road
  charge/CO2 emission class vs only incidental weight/axle mentions). The ZEV
  weights & dimensions file is the separate 2023/0265(COD) (EP Legislative Train),
  which this document does not amend.

### N2 — eEconic installed-per-pack is 112 kWh, not 105
- See conflict 1: 336 / 3 = 112 kWh per pack. `[D]`

### N3 — VECTO generic BEV usable ≈ 85.5% but EEA real configs vary 13%–86%
- Fact: the EEA `battery` table (`hdv_2024_battery.csv`) standard-value rows
  cluster at usable/installed ≈ 85.5% (e.g. 490→419, 306→233), but real
  sub-configurations span 12.9%, 29%, 48%, 70% as well. `[V]`
- So "85%" is only the VECTO standard-value default, not a safe universal ratio.
  This reinforces: never derive usable from installed by a fixed factor.
