# EV charger hardware — research pass 4 (6 Nov 2026)

Written for Bob. Plain English. Short sentences. This is the charger (EVSE) side,
a separate domain from the pass-3 vehicle research. Same discipline: every value
has a source, a section/quote, and a tag.

## Top-line

1. **Covered all classes:** AC home/destination (Type 2), public DC (CCS2),
   destination DC, fleet/off-grid DC, Tesla, and heavy-truck MCS (megawatt).
2. **64 spec values** recorded; **32 opened straight from OEM datasheets** I
   downloaded (Kempower, ABB, Alpitronic, Tritium). The rest are OEM web pages,
   press, or market price guides — tagged `[C]`.
3. **31 catalogue rows**: 5 primary datasheets opened, 16 secondary sources,
   10 still to fetch (`[BOB]`).
4. **Max power, connectors, voltage/current, efficiency, OCPP and ISO 15118** are
   all well-sourced from datasheets. Reliable.
5. **Prices** are market/installer estimates only — no OEM publishes list prices.
   Treat them as rough bands, tagged `[C]`.
6. **Ramp / response times are the real gap** — almost never on datasheets. You'd
   need test reports. Logged as `[BOB]`.
7. **A modelling point:** the charging *curve* is negotiated by the vehicle's BMS
   over ISO 15118, not fixed by the charger. Pair the charger's max power with the
   pass-3 vehicle accept-curve to get real session times.

### What the numbers look like by class
- **AC home/destination:** 7.4 / 11 / 22 kW, Type 2, ~€400–700 hardware,
  ~$900–2,500 installed. Networked units speak OCPP 1.6.
- **Public DC:** 50–400 kW. Alpitronic HYC400 (100–400 kW, 150–1000 V, up to
  98% efficient), ABB Terra 360 (360 kW, 4 outputs, >95%), Tesla V4 (up to
  500 kW/stall from a 1.2 MW cabinet). ~$45k–200k hardware per unit.
- **Destination / fleet DC:** Tritium RTM75 (50/75 kW, liquid-cooled, IP65,
  −35…+50 °C), Tritium PKM150 (modular 50–150 kW, 950 V site bus, up to 8 plugs),
  Kempower Satellite (400 kW/output, 600 kW/unit, dynamic 25 kW sharing).
- **Heavy-truck MCS:** standard allows up to 3.75 MW (3000 A, 1250 V). Real 2025–26
  products ~1 MW–1.2 MW: Kempower Mega Satellite Flex (1.2 MW MCS / 560 kW CCS),
  ABB (1.2 MW continuous), Heliox (1 MW shared, 6×180 kW), Tesla Semi (1.2 MW).

### Top sources to start the charger library with
1. Kempower Satellite V2 datasheet — distributed DC, full specs incl. protocols.
2. Alpitronic HYC400 datasheet — modular public DC, efficiency, 1000 V.
3. ABB Terra 360 datasheet + ABB product data chart — whole ABB lineup.
4. Tritium RTM75 datasheet — the most complete single sheet (comms + environment).
5. Open Charge Alliance (openchargealliance.org) — authoritative OCPP spec + the
   Certified Products registry.
6. CharIN (charin.global) — authoritative MCS and CCS specs.
7. Tesla V4 (press/wiki until an OEM datasheet exists).
8. Argonne MCS FAQ — public, authoritative MCS power/voltage/current.

## Detail by field

- **Max power:** fully covered, reliable. Per-output *and* per-cabinet both
  captured where the system is distributed (Kempower, Tesla, Tritium PKM150).
- **Connector / standard:** covered (Type 2, CCS2, CHAdeMO, NACS, MCS).
- **Voltage / current:** covered from datasheets (e.g. 150–1000 VDC, 500–600 A CCS,
  3000 A / 1250 V MCS).
- **Efficiency:** covered for DC (>95% typical, up to 98.2% Alpitronic S2).
- **OCPP:** covered — which version per model, plus the standards timeline
  (1.6 → 2.0.1=IEC 63584:2024 → 2.1=IEC 63584-210:2025).
- **ISO 15118 / Plug & Charge / bidirectional:** covered per model; see
  `standards_and_protocols.md`.
- **Cooling / IP / temperature:** partial (Tritium full; others vary).
- **Power sharing / dynamic allocation:** covered qualitatively (Kempower 25 kW
  granularity; ABB dynamic DC; Alpitronic power-stack; Tritium site DC bus).
- **Prices:** partial, secondary only. Hardware bands by power level; no OEM list
  prices. Public per-kWh session pricing = `[BOB]` (network-specific).
- **Ramp / setpoint-response times:** **not covered** — not on datasheets. `[BOB]`.

## Files
- `catalogue.csv` — every source + maker, incl. "to fetch" with status.
- `charger_specs.csv` — every spec value with link, section/quote, tag.
- `standards_and_protocols.md` — connectors, ISO 15118, OCPP versions/IEC, MCS.
- `report.md` — this file.

## Honest limits
- No OEM publishes list prices; price bands are installer/market estimates.
- Ramp and smart-charging response times need test data, not datasheets.
- MCS is still finalising; treat 3.75 MW as the standard ceiling, ~1.2 MW as
  today's real product.
- Datasheet values are OEM claims at nominal conditions; delivered power is always
  the minimum of charger, vehicle, and grid connection.
