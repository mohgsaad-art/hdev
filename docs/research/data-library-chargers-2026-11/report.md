# EV Scope charger / CPO / charging-cost data library — pass 1 report (6 Nov 2026)

Written for Bob. Plain English. Short sentences. This is the charging-side twin
of the vehicle-side data-library pass. Same rules, same tags.

## Top-line (read this first — 15 lines)

1. **Fill now, open + commercial-safe:** AFIR targets (EUR-Lex, EU reuse); the
   Danish elafgift treatment (skat.dk); the DK spot price (Energi Data Service);
   EAFO charger counts (CC BY 4.0); the MCS standard envelope (IEC/SAE scope);
   OCPP/ISO 15118 version map; the Milence DK truck price (primary).
2. **Needs OEM documents or supplier quotes (cite the value, not the PDF):** all
   charger hardware specs (power/voltage/current/efficiency/OCPP/connectors);
   charger hardware prices; CPO ad-hoc/subscription prices; eMSP card mark-ups.
3. **No public source at all:** partial-load efficiency curves, standby watts,
   ramp rate, OCPP setpoint-response latency, MTBF, and — until the Danish tender
   documents are added — every uptime %/fix-time SLA and contract-term value.
4. **Two blockers:** (a) the Danish knowledge-base tender/concession/SLA files
   are **not in the repo**, so sections 3.5/4.1/Q9 are stubbed; (b) the Danish
   AFIR National Access Point is required by law but its URL/licence/price fields
   are unconfirmed (Q1) — the highest-value open-data fetch.
5. **COWI re-checked from the file**, not re-derived: charger+board DKK bands,
   Radius 17,950 DKK + 1,280 DKK/A (2024), trenching, and the unsourced 0.85
   load factor — all captured with caveats.

### Top 10 sources to start the charger library with
1. Milence country tariff table — primary HD-truck price (DK 2.799 DKK/kWh ex VAT).
2. AFIR Reg. (EU) 2023/1804 consolidated (EUR-Lex, open) — HDV pool targets, NAP, payment.
3. skat.dk Juridisk Vejledning — elafgift rate + EV-charging refund to 2030.
4. Energi Data Service (Energinet) — DK1/DK2 spot + DatahubPricelist tariffs.
5. IEC 61851-23-3:2026 scope + SAE/Argonne MCS FAQ — the MCS envelope.
6. Open Charge Alliance — OCPP versions + Certified Products registry.
7. EAFO Denmark (CC BY 4.0) — charger counts + consumer price indicators.
8. Current DSO takstblade (Radius/Cerius/N1/TREFOR/Konstant) — connection fee + TOU tariffs.
9. OEM datasheets (Kempower/Alpitronic/ABB/Tritium already opened; +MCS makers).
10. COWI e-truck calculator (in repo) — DK charger cost bands + Radius fee + price stack.

---

## Detail by category

### Hardware (section 3.1)
- Power, voltage, current, peak efficiency, OCPP and ISO 15118 are **well
  covered** from OEM datasheets (Kempower Satellite, Alpitronic HYC400, ABB
  Terra 360, Tritium RTM75 already opened and carried in
  `charger_specs_extracted.csv`). All **cite-only** — store values, not PDFs.
- **Not covered anywhere public:** partial-load efficiency, standby W, ramp
  rate, setpoint response. These need test reports, not datasheets.
- Keep rated/continuous/peak and per-cabinet/per-connector apart — the CSV does.
- 30+ OEMs from the brief's lead list each have a catalogue row (most are `[BOB]`
  "to fetch" with the search noted, so section-8's "every OEM has a row" holds).

### MCS (section 3.2)
- **IEC 61851-23-3:2026 is published** (Aug 2026); EV-side envelope 1250 V DC.
  SAE/CharIN envelope 3.75 MW / 3000 A / 1250 V (public FAQ). Products today are
  ~1-1.2 MW (Kempower, ABB, Heliox, Tesla Semi). Standard-allows vs
  product-delivers kept apart. See `standards_regulation.md`.

### Comms / timing (section 3.3)
- OCPP 1.6 / 2.0.1 (=IEC 63584:2024) / 2.1 (=IEC 63584-210:2025, V2X). ISO
  15118-2 PnC and -20 per model from datasheets. **Setpoint latency and ramp
  rate have no public measured source** — only OCPP/Energinet requirements.

### Costs (section 3.4)
- COWI DKK bands + Radius fee + trenching captured (2024, operator un-named,
  `[C]`). Independent points are different in scope (USD, hardware-vs-installed),
  so not a clean comparison — both listed, no silent pick (Q6). No OEM list
  prices exist. AFIF award lists are the best route to real DK/EU per-site costs
  (`[BOB]`).

### CPOs / prices (section 3.5)
- Milence DK HD-truck price is primary and date-stamped. Car-CPO prices are
  app/terms-restricted — cite published pages only; most are `[BOB]`. Every CPO
  and eMSP lead from the brief has a catalogue row. Contract models are laid out
  structurally; clause-level values are blocked on the missing Danish documents.

### Tariffs (section 3.6)
- The full DK stack is mapped: spot (Energinet, open) + DSO TOU net tariff
  (Lav/Høj/Spids, Tariff Model 3.0) + Energinet system/transmission + elafgift +
  supplier markup. The Elindsigt file gives a **modelled** example (loud caveat
  in `tariffs_dk.csv`); current official values per DSO are `[BOB]`.
- **Big 2026-27 point:** the general elafgift is cut to the EU minimum (~0.8
  øre/kWh), so for those two years the special EV refund barely moves the needle.

### Regulation (section 3.7)
- AFIR HDV targets, ad-hoc payment, price transparency and NAP data obligations
  captured from EUR-Lex (open). Exact article numbers flagged to re-confirm. The
  DK NAP itself is the top open-data question (Q1).

---

## Files in this folder
- `catalogue.csv` — every source + OEM + CPO lead, incl. "to fetch" with the search.
- `field_coverage.csv` — field × charger class → best source + coverage.
- `charger_specs_extracted.csv` — every spec value with source/section/quote/tag.
- `costs_extracted.csv` — every cost with currency, year, VAT, scope, basis, tag.
- `cpo_prices.csv` — operator prices with capture date + VAT + currency.
- `tariffs_dk.csv` — the DK electricity + tax stack, with effective dates.
- `contracts_and_sla.md` — contract-model structure; clause values blocked (BOB).
- `standards_regulation.md` — AFIR / MCS / OCPP clauses and status.
- `conflicts.md` — the 10 section-5 questions, each with a verdict or BOB.
- `library_schema.md` — the 12 proposed tables + which columns are open/cite/none.
- `bob_to_fetch.md` — what to fetch next, with how and why.
- `report.md` — this file.

## Honest limits
- The Danish tender/concession/SLA documents and the manual-fetch-list are not
  in the repo; sections 3.5/4.1/Q9 are stubbed until they are added.
- OEM figures are claims at nominal conditions; delivered power is always
  min(charger, vehicle BMS over ISO 15118, grid connection).
- Standard text (IEC/SAE/ISO) is paid — only scope/preview quoted.
- Elindsigt tariff numbers are a modelled example, not official rates.
- Nothing from the brief's lead lists is carried as fact without a V or C source;
  unopened leads are tagged BOB with the search noted.
