---
description: Index of the 32 markdown files generated on 2026-10-06 from CELEX_02017R2400-20260101_EN_TXT.pdf — the EUR-Lex consolidated text (as of 01.01.2026) of Commission Regulation (EU) 2017/2400 (the VECTO/HDV CO2-certification regulation). Read this first to navigate the new `eu-regulation-2017-2400/` knowledge base and see the flagged OCR/ambiguity issues before relying on any formula.
sources: cowork
---

# PDF extraction batch — 2026-10-06

## What this run did

One new PDF appeared in the Project files since the last extraction batch (2026-09-20): `CELEX_02017R2400-20260101_EN_TXT.pdf`, the official EUR-Lex "consolidated text" (a documentation tool, not itself legally binding — the authentic version is the Official Journal) of **Commission Regulation (EU) 2017/2400** of 12 December 2017, implementing Regulation (EC) No 595/2009 as regards determination of CO2 emissions and fuel consumption of heavy-duty vehicles, consolidated to include all amendments in force as of **01.01.2026**:

- ►B = original 2017 baseline text
- ►M1 = Commission Regulation (EU) 2019/318
- ►M2 = Commission Regulation (EU) 2020/1181
- ►M3 = Commission Regulation (EU) 2022/1379
- ►M4 = Commission Regulation (EU) 2025/258

No PPT/PPTX files were present in the Project. The other two PDFs in the Project (`VEcto documentation.pdf`, `sr7_lot4_final_report_en.pdf`) were already fully extracted in the 2026-09-20 batch (see `pdf-extraction-index-2026-09-20.md`) and were not re-processed.

The regulation (24,743 lines of extracted text, ~170 pages of EUR-Lex layout) was split across 10 parallel subagents by Chapter/Annex, each using `project_read` + `Read(offset/limit)` for full coverage, then `project_write`. No values, thresholds, or formulas were invented — every subagent was instructed to transcribe faithfully and flag anything it could not verify. **All 32 files are at `claude/knowledge-base/eu-regulation-2017-2400/`.**

## ⚠️ Headline finding: the "electrification scope gap" flagged on 2026-09-20 is now partly closed

The 2026-09-20 index (`pdf-extraction-index-2026-09-20.md`) flagged that none of the project's then-available VECTO sources (2014 LOT3 report, 2017 SR7/LOT4 report) contained any battery / e-motor / fuel-cell component methodology, and that this would require "VECTO 3.x+ documentation... not among the current project files."

**This regulation's Annex Xb is exactly that missing piece, now confirmed from an authoritative legal source:**

- **►M3 (Commission Regulation (EU) 2022/1379, in force from 2022)** introduced the entire electric-machine-system / IEPC (Integrated Electric Powertrain Component) / IHPC Type 1 (Integrated Hybrid Powertrain Component) / battery-system / capacitor-system certification methodology.
- **►M4 (Commission Regulation (EU) 2025/258, in force from 2025)** added fuel-cell-system (FCS) certification on top of that, plus hydrogen-ICE/dual-fuel engine provisions in Annex V, hydrogen-range output fields in Annex IV, and the new Annex VIIA (wheel-end friction losses).
- No electrification content carries an M1 or M2 marker — confirms electrification entered this Regulation only in 2022 (M3) and 2025 (M4), not in the 2017 baseline or 2019/2020 amendments.

This is directly citable, authoritative, dated regulatory fact — not an estimate — and should update the project's working assumption that "VECTO has no official BEV/FCEV methodology."

## ⚠️ Important scope limitation found in the same document

**Annex Xa (on-road "Verification Testing Procedure" — the post-production CO2-conformity check performed on real vehicles) explicitly excludes electrified vehicles.** Point 3(c) (►M4) states verbatim: *"Hybrid electric, pure electric and fuel cell hybrid vehicles shall not be selected for the verification test."* So while Annex Xb gives a full **component-level** certification/test methodology for batteries, e-machines and fuel cells, there is **no equivalent in-service/on-road verification regime** for BEV/FCEV/HEV HDVs anywhere in this Regulation as of 01.01.2026. If the HDEV tool's "auditable" positioning leans on this Regulation's verification framework as a credibility reference, that claim should be scoped to conventional ICE vehicles only, pending confirmation of whether some other instrument fills this gap (not checked in this run).

## File-by-file index

| # | Topic | Files |
|---|---|---|
| 1 | Chapters 1-6 — general provisions, 39 definitions, licensing, certification/declaration procedure, conformity/remedial measures (Articles 1-27) | `01-general-provisions-licensing-procedure.md` |
| 2 | Annex I — vehicle-group classification; staged CO2 method for heavy buses | `02-annex-i-vehicle-classification-bus-co2-method.md` |
| 3 | Annex II — manufacturer IT/data-integrity processes to operate the simulation tool | `03-annex-ii-simulation-tool-operation-requirements.md` |
| 4 | Annex III — full vehicle input-parameter schema (general vehicle, powertrain components, ADAS/other) | `04a-...-vehicle-general.md`, `04b-...-powertrain-components.md`, `04c-...-other.md` |
| 5 | Annex IV — output files (manufacturer's records file / customer information file / vehicle information file) | `05-annex-iv-output-files-mrf-cif-vif.md` |
| 6 | Annex V — engine (ICE) verification: test setup, cycles, fuel-map calculations, appendices | `06a`...`06d` (4 files) |
| 7 | Annex VI — transmission / torque converter / OTTC / ADC verification | `07a`...`07c` (3 files) |
| 8 | Annex VII + VIIA — axle torque-loss verification; wheel-end friction losses (new, ►M4) | `08a-annex-vii-...md`, `08b-annex-viia-...md` |
| 9 | Annex VIII — air drag (Cd×A) verification | `09a`...`09f` (6 files) |
| 10 | Annex IX + X — auxiliary systems declaration; tyre rolling-resistance certification | `10a-annex-ix-...md`, `10b-annex-x-...md` |
| 11 | Annex Xa — on-road verification testing procedure (ICE only — see scope note above) | `11a-annex-xa-verification-testing-procedure.md` |
| 12 | **Annex Xb + XI — electric powertrain component certification (batteries, e-machines, capacitors, fuel cells) — the key new HDEV-relevant content** | `12a`...`12h` (8 files) |

## Cross-cutting issues flagged by every subagent (read before coding against any formula)

1. **OCR corrupted mathematical symbols throughout** (√, Σ, ×, ≤/≥, −, brackets came out as stray characters like "Ä", "Ü", "ð", "þ", "¼"). Every file transcribes the raw OCR text and then gives a clearly-labeled reconstructed/cleaned version of each formula. These reconstructions are engineering-judgment best efforts, not verified-exact source text — **spot-check any formula you plan to encode into simulation logic against the actual PDF page images**, especially: Annex V's WHTC/trapezoidal-integration formulas (point 5.1/5.2/5.5.1) and the n57 engine-speed formula; Annex VI/VII's torque-loss and uncertainty-propagation formulas; Annex VIII's Cd×A validity formulas; Annex Xb's battery DCIR and FCS power-correction equations.
2. **Figures/diagrams are referenced throughout but this is a text-only OCR extraction with no visual layer** — every file flags each missing figure individually with the phrase "[Figure referenced in source but not visually extracted from this text-only OCR]". Notably: Annex I's low-entry bus decision flow and 5-step bus-manufacturing data-flow diagrams; Annex Xb's Figure 5 FCS sensor-position schematic (defines sensor labels used throughout the FCS equations — worth pulling from the original PDF if FCS modelling is attempted).
3. **Several apparent drafting inconsistencies in the official consolidated text itself** (not extraction errors) were flagged rather than silently corrected, e.g.: CIF §2.4 skips from 2.4.3 to 2.4.5; Annex VIII has internal table-numbering mismatches; Annex VI's Appendix 12 lists an undefined "IHPC Type 1" transmission type; Annex VII's two-dynamometer uncertainty formula appears to have a subscript typo in the source; the UK is still listed in Annex VII's Member State certification-mark table.
4. Several files note specific **formula/table items that need verification against the real PDF rendering** rather than this OCR text — see each file's own flagged-items list; the battery current-pulse divisor sequence in `12c` and the compressed-hydrogen density table in `04c` are the two most likely to matter for calculations.

## Directly actionable for the HDEV sizing tool (pointers, not conclusions — read the source files for full detail and conditions)

- `12h-annex-xb-standard-values-and-simulation-input-parameters.md` — legally-sourced default e-motor/gearbox loss-map coefficients, battery OCV-vs-SOC curves, DCIR tables (HPBS vs HEBS), max C-rate-vs-SOC tables, capacitor defaults, and an FCS default efficiency-vs-load curve. These are citable regulatory defaults, not estimates.
- `04b-annex-iii-input-parameters-powertrain-components.md` — Table 10's SOCmin/SOCmax/DeteriorationPerformanceRatio defines the regulation's "usable battery energy window" concept (tied to Euro 7 battery-durability requirements, Reg (EU) 2024/1257).
- `07c-annex-vi-torque-converter-ottc-adc.md` — the one explicit EV driveline provision in Annex VI: certification of a belt connecting an electric machine to the main powertrain as a single-speed ADC (►M4), with EV-specific default friction/torque substitutions.
- `08a`/`08b` (axle/wheel-end) — flag that integrated e-axles are not addressed by name anywhere in Annex VII/VIIA; this is an open question, not resolved in this run.

## Not processed in this run

`eltiltrucks-beregner-ark.xlsx`, `Elindsigt2.2.xlsx`, and `ChargePointCalculator_v5.xlsx` were excluded — scope was PDF/PPT files only, per this run's instructions.

## Knowledge-base size note

After this batch, the Project's knowledge store is at roughly 1.43 MB of its 2 MB cap. Future extraction batches should watch this limit — some of the more template-heavy Annex Xb appendices were deliberately summarized rather than transcribed field-by-field for this reason (flagged inline in `12f`).
