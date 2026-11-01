# HVAC thermal-model research — truck cab parameters, BEV HVAC power, VECTO/2017-2400 status

**For:** Bob (HDEV) · **Date:** 2026-11-01 · **Scope:** research only, no code changes.
**Rules applied:** official / peer-reviewed / OEM sources only; value + source + page/table for every
number; `NOT FOUND` where no qualifying source exists; no estimates.

> **Tooling note / verifiability caveat.** In this sandbox, PDFs and most publisher pages
> (MDPI, preprints.org, EUR-Lex HTML, NREL direct PDF) could **not** be opened by the fetch tool
> (PDF content-type unsupported; publisher/EUR-Lex anti-bot returns empty bodies). Values below marked
> **[snippet]** are taken from the search engine's **cited abstract/snippet** of the named official or
> peer-reviewed source, not from a full read of the page/table. Where a number requires a specific
> table/figure that only appears in the PDF body, it is marked **NOT FOUND (behind PDF — not verifiable here)**
> so you can pull the exact figure from the source yourself. The VECTO items (3, 4) were verified
> **directly against the VECTO source code** fetched from `mohgsaad-art/VECTO` and against the existing
> HDEV research doc `docs/research/vecto/06-auxiliaries-all.md`, so those are first-hand.

---

## Item 1 — Truck cab thermal parameters (surface area, U-value/UA, interior volume, glazing area)

| Parameter | Value | Vehicle type | Method | Source | Page/Table |
|---|---|---|---|---|---|
| Thermal-load estimation tool exists for truck cab/sleeper (surface area, glazing, volume are its **inputs**) | Tool = **CoolCalc**, "simplified, physics-based HVAC load estimation tool… flexible geometry" | US long-haul sleeper cab | Simplified physics-based model (not CFD) | NREL/TP-5400-52452, *CoolCalc: A Long-Haul Truck Thermal Load Estimation Tool* (Lustbader et al.) [snippet] | Abstract |
| Outer surface area (numeric, m²) | **NOT FOUND (behind PDF — not verifiable here)** | — | — | NREL 52452 / NREL TP-5400-66860 are the right documents to read | geometry tables |
| Overall U-value / UA (W/K) | **NOT FOUND (behind PDF — not verifiable here)** | — | — | " | " |
| Interior air volume (m³) | **NOT FOUND (behind PDF — not verifiable here)** | — | — | " | " |
| Glazing area (m²) | **NOT FOUND (behind PDF — not verifiable here)** | — | — | " | " |
| Cabin insulation thermal-resistance effect (related, peer-reviewed) | Fully-insulated config ≈ **+5.6 °C** mean cabin temp vs non-insulated (same heating load); ≈ **+9 °C** at R = 4 m²K/W | EV / truck cabin | Experimental + simulation | SAE 2023-01-0763, *Effect of Cabin Insulation on the Heating Performance in EVs at Low Temperatures* [snippet] | Abstract |

**Finding (item 1).** The HDEV placeholders (A_surface 20 m², U 3.0 W/m²K, volume 6.5 m³, window 4 m²) have
**no sourced replacement found that is verifiable in this environment.** The correct primary sources are the
NREL CoolCab/CoolCalc reports — **NREL/TP-5400-52452** (CoolCalc tool) and **NREL/TP-5400-66860**
(*Long-Haul Truck Sleeper Heating Load Reduction Package*) — which define a sleeper-cab geometry (surface,
glazing, volume) and the convective/conductive UA used by the tool. Those numbers live in the PDF body
tables, which the sandbox could not open. **Recommendation:** read NREL 52452 §"Geometry/Boundary
conditions" and 66860 directly to extract the exact m²/m³/UA, and cite the table. Do **not** adopt the
current placeholders as sourced.

**Candidate primary sources to extract item-1 numbers from (all NREL/DOE, public domain):**
- NREL/TP-5400-52452 — CoolCalc tool (geometry + HVAC load physics). https://docs.nlr.gov/docs/fy14osti/52452.pdf
- NREL/TP-5400-66860 — Sleeper heating load reduction. https://www.nlr.gov/docs/fy16osti/66860.pdf
- NREL CoolCab 77-inch sleeper cab test article (SAE/NREL) — "Application of Sleeper Cab Thermal Management
  Technologies…", Lustbader & Venson (NREL) + Volvo. https://digital.library.unt.edu/ark:/67531/metadc840767/

---

## Item 2 — Measured HVAC electric power of battery-electric trucks vs ambient temperature

| Finding / value | W / kWh | Vehicle | Ambient | Tag | Source | Page/Table |
|---|---|---|---|---|---|---|
| Real-world BET fleet average energy consumption | **0.96 kWh/km** (fleet avg, all conditions) | 19 × Daimler **eActros 300/400** | DE real world 2023–early 2025 | **measured** | Öko-Institut, *Real-world data analysis… battery electric trucks operating in Germany* (ELV-LIVE 2nd report, 2025) [snippet] | publication page |
| Winter vs summer total energy penalty (incl. HVAC, air density, winter tyres) | **≈ +25 %** on a representative route | **eActros 600** (pre-series) | Scandinavia winter (down to −35 °C in prior test) | **measured** (OEM) | Daimler Truck / electrive, eActros 600 final winter tests, 2025-02-25 [snippet] | article |
| Cabin-heating ("sleeping in a warm cab") overnight electric cost | **NOT FOUND (specific kWh behind paywalled trade article)** | eActros 600 | winter | measured (OEM, claimed) | eurotransport.de, "so viel Strom kostet die Kälte" 2025-02 [snippet] (number not in snippet) | article body |
| Cabin HVAC heating power of an electric **truck** cabin vs ambient (bench/chamber) | **NOT FOUND (behind PDF — not verifiable here)** — paper reports power vs ambient but W values are in PDF figures/tables | electric truck cabin (AIT rig) | climate chamber | **measured** | Dvorak, Kardos, Gellai, Šimić, *Experimental Performance Investigation of an Air–Air Heat Exchanger and Improved Insulation for Electric Truck Cabins*, World Electr. Veh. J. 2025, 16, 129 [snippet] | Results §/figures |
| HVAC efficiency improvement from heat-exchanger + insulation | **≈ 22 %** energy-efficiency gain | electric truck cabin | — | **measured** | Dvorak et al. 2025 (WEVJ 16:129) [snippet] | Abstract |
| Heating-vs-cooling energy asymmetry (cabin, electrified vehicle) | heating at **−7 °C ≈ 4–10×** the energy to cool at **35 °C** | electrified vehicle cabin (MAC) | −7 °C vs 35 °C | **measured** (JRC lab) | JRC, *Energy consumption of mobile air-conditioning systems in electrified vehicles under different ambient temperatures*, JRC133756 (2024) [snippet] | Abstract |
| Cabin heating load reduction strategies (truck, cold climate) | reductions quantified (insulation / recirculation / encapsulation) — specific kW in PDF | electric truck (Volvo GTT co-author) | cold climate | **simulated** (CFD/system model) | Ramesh Babu, Sebben, Chronéer, Etemad, *Heating load reduction strategies…*, Thermal Sci. & Eng. Progress 60 (2025), DOI 10.1016/j.tsep.2025.103417 [snippet] | Results |
| BET real-world energy-consumption characterisation (temperature effect noted) | qualitative; HDV BEV real-world | tractor / rigid BEV | EU | **measured** | ICCT, *Real-world… heavy-duty BEVs* (2023), HDV-BEVs-real-world_final.pdf [snippet] | report |
| Auxiliary-load share & heating:cooling ratio (EV, model validated on data) | heating dominates cooling ~**7:1**; heating power rises **44×** at low temp; aux = 75 % idle → 12 % highway | EV (passenger, physics+ML) | wide range | **measured + simulated** | *Predicting Auxiliary Energy Demand in EVs…*, Energies 2025, 18, 6092 [snippet] | Abstract |

**Finding (item 2).** Qualitative/measured trends are well sourced (Öko-Institut ELV-LIVE real fleet;
eActros 600 OEM winter test ~+25 %; JRC 4–10× heating/cooling asymmetry; Dvorak AIT truck-cabin rig).
**The specific W-or-kWh/h-vs-ambient curves for a truck cab live in PDF tables/figures that this environment
could not open** → marked NOT FOUND where a number is required. The Dvorak 2025 (AIT) and Ramesh Babu 2025
(Chalmers/Volvo) papers are the two that actually report cabin HVAC **power vs ambient for a truck** and
should be read directly for the numbers; tag Dvorak = **measured**, Ramesh Babu = **simulated**.

---

## Item 3 — VECTO / Regulation (EU) 2017/2400: any 2024–2026 thermal HVAC model or new HVAC values for *lorries*?

| Question | Answer | Source | Quote / locus |
|---|---|---|---|
| Latest consolidated 2017/2400 | **02017R2400-20250301** (consolidation current 2025-03-01); previous consolidation 2024-01-01 | EUR-Lex ELI 2017/2400 [snippet] | consolidated header "2017R2400 — EN — 01.01.2024 — 005.001" |
| Latest substantive amendment | **Commission Regulation (EU) 2025/258 of 7 Feb 2025** | EUR-Lex 2025/258 [snippet] | title |
| What 2025/258 adds for lorries | hybrid & pure-electric vehicles, **dual-fuel**, **waste-heat recovery**, hydrogen (FC + H2-ICE) | EUR-Lex 2025/258 XHTML [snippet] | "…added new technologies such as hybrid and pure electric vehicles, dual-fuel vehicles and waste heat recovery." |
| Does 2025/258 add a **thermal HVAC model** (heat balance / temperature-dependent heating) for **lorries**? | **NOT FOUND** — no lorry thermal HVAC / heat-balance model is introduced for lorries. Lorry HVAC remains a flat declared auxiliary (A/C-compressor power), no heating term, no temperature input. | (a) EUR-Lex 2025/258 summary [snippet]; (b) **VECTO source code**, first-hand | see VECTO-code finding below |
| Does the temperature-dependent SSM heat-balance HVAC exist anywhere in VECTO? | **Yes — but buses only.** `Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/` (`SSMRun.cs`, `SSMCalculate.cs`, `SSMInputs.cs`). Trucks use flat declaration tables (`Resources/Declaration/VAUX/HVAC-Table.csv`), A/C only. | **VECTO source** (`mohgsaad-art/VECTO`), first-hand; HDEV `docs/research/vecto/06-auxiliaries-all.md` §1–§3 | SSM is under `BusAuxiliaries`; no lorry equivalent |

**Finding (item 3).** As of the 2025-03-01 consolidation and the 2025/258 amendment, **no thermal/heat-balance
HVAC model and no new temperature-dependent HVAC values were added for lorries.** The new-tech additions for
lorries are powertrain/energy (hybrid, pure-electric, dual-fuel, waste-heat recovery, hydrogen), not cabin
thermal HVAC. The only temperature-dependent heat-balance HVAC in VECTO is the **bus SSM**, unchanged in scope
(bus-only). This matches HDEV's existing conclusion that applying the bus SSM to a lorry is an **HDEV extension
beyond VECTO declaration**.

---

## Item 4 — VECTO bus SSM `VentilationRate`: fresh outside air, or partly recirculated?

**Verified first-hand in VECTO source (`SSMInputs.cs`, `SSMCalculate.cs`, `Constants.cs`).**

| Aspect | Finding | Source locus |
|---|---|---|
| Ventilation power formula | `VentPower(heating) = BusVolumeVentilation × (heating ? VentilationRateHeating : VentilationRate) × SpecificVentilationPower` | `SSMInputs.cs:85-89` (`VentPower`) |
| Units | `VentilationRate` is **air changes per hour** (code comment `C29 - ( L/H )  --- !! 1/h`); `SpecificVentilationPower` = **0.56 Wh/m³** | `SSMInputs.cs:79-92`; `Constants.cs` SteadyStateModel `SpecificVentilationPower = 0.56 Wh/m³` |
| Default rates | **HighVentilation = 20 /h**, **HighVentilationHeating = 10 /h**, **LowVentilation = 7 /h** | `Constants.cs` `BusAuxiliaries.SteadyStateModel` |
| Is there a **fresh-air vs recirculation split** in the SSM? | **NO.** There is **no recirculation fraction, no fresh-air share, and no "outside air" variable anywhere** in the SSM inputs or calculation. The rate multiplies the **whole** `BusVolumeVentilation`; the energy cost is a flat specific ventilation power (fan/air-moving energy per m³). The model does **not** distinguish fresh vs recirculated air. | `SSMInputs.cs` (full file grep: only `VentilationRate`, `VentilationRateHeating`, `VentPower`, `BusVolumeVentilation`, boolean on/off flags — no `fresh`, no `recircul`) |
| On/off logic (when the rate applies) | Heating: `VentilationOnDuringHeating`; AC: `VentilationDuringAC`; both-inactive: `VentilationWhenBothHeatingAndACInactive` | `SSMInputs.cs:131-137`; `SSMCalculate.cs:272-296, 376-397, 399-428` |
| Interpretation | Because the energy term is purely a **specific air-moving power** applied to a full-volume air-change rate, and **no heat is recovered or recirculated in the ventilation term**, the SSM effectively treats the ventilated volume as **fresh/unconditioned air load at the stated air-change rate** (the heating/cooling demand is computed separately via the wall/people/solar balance, not reduced by any recirculation factor). The code does **not** model partial recirculation. | by construction, `SSMInputs.cs` + `SSMRun.cs` TotalW |
| Sourced **fresh-air share for truck cabs** (external) | Peer-reviewed truck-cab value exists: **≈100 m³/h fresh air for 2 occupants** to hold CO₂ ≈1000 ppm | Dvorak et al. 2025 (WEVJ 16:129) [snippet]: "a fresh-air volume flow of around 100 m³/h is required to keep the CO₂ concentration around 1000 ppm" |

**Finding (item 4).** In VECTO's bus SSM, `VentilationRate` is a **single air-change rate (1/h) applied to the
full cabin/bus volume**, costed by a flat **0.56 Wh/m³** specific ventilation power. **There is no
fresh/recirculated distinction in the code at all** — so it is neither explicitly "fresh" nor "recirculated";
it is an undifferentiated ventilation air-exchange term. The 2017/2400 bus annex text (the regulatory basis for
these defaults) could **not** be opened here to confirm its wording — **NOT FOUND (annex text behind EUR-Lex
anti-bot)**; read Annex Xa (bus auxiliaries / HVAC) of the consolidated 2017/2400 to confirm whether it labels
the 7/10/20 ACH as outside air. A sourced **fresh-air requirement for a truck cab** does exist: Dvorak 2025
reports ~100 m³/h for two occupants to keep CO₂ ≈1000 ppm (**measured/engineering** basis).

---

## Item 5 — Door openings on urban delivery trucks: measured air exchange / heat loss per cab door opening

| Finding | Value | Scope | Tag | Source |
|---|---|---|---|---|
| Door-opening infiltration for **refrigerated truck cargo body** | warm-air infiltration during door openings ≈ **34 %** of total refrigeration load | refrigerated delivery truck **cargo box** (not driver cab) | measured/review | Brunel Univ. thesis fulltext [snippet]; USDA tech bulletin TB-1375 *Refrigeration Requirements for Truck Bodies: Effects of Door Usage* |
| Measured air exchange / heat loss **per door opening of a heavy-truck driver cab** | **NOT FOUND** | heavy-truck **driver cab** | — | No qualifying official/peer-reviewed source located |

**Finding (item 5).** The measured door-opening literature is for **refrigerated cargo bodies** and for
**commercial-building/store doors**, not for a truck **driver cab**. **No measured air-exchange or heat-loss
figure per door opening for a heavy-truck driver cab was found** → `NOT FOUND`. (The refrigerated-body 34 %
figure and the USDA TB-1375 door-usage work are the closest measured analogues, but they are cargo-box, not cab,
and should not be transferred to the driver cab without caveat.)

---

## Item 6 — SAE J2765: what it covers and current revision

| Aspect | Finding | Source |
|---|---|---|
| Title | *Procedure for Measuring System COP [Coefficient of Performance] of a Mobile Air Conditioning System on a Test Bench* | SAE / ANSI webstore [snippet]; US EPA 40 CFR 86 IBR [snippet] |
| What it covers | A **bench-test procedure** to measure **capacity (performance) and efficiency (COP)** of mobile A/C refrigerant systems under **steady-state** conditions. System scope: one or two evaporator coils, compressor, expansion device, one condenser, ±chiller. | SAE J2765 §1 / §1.2 via accuristech & regulations.gov [snippet] |
| Is it a MAC-system COP bench test? | **Yes** — confirmed. | as above |
| Current revision | **J2765_201707** (issued **July 2017**). Prior IBR reference was **J2765 OCT2008**. So current ≈ 2017 revision; it is the latest listed in SAE/ANSI stores as of this research. | SAE J2765_201707 (accuristech / ANSI) [snippet]; 40 CFR 86.1 lists the older OCT2008 for IBR [snippet] |

**Finding (item 6).** J2765 is confirmed as the **mobile-A/C system COP steady-state bench-test** procedure.
**Current revision: J2765_201707 (July 2017).** (Caveat: SAE occasionally reaffirms/"stabilizes" standards
without a new number; I could not open the SAE page body to read a reaffirmation date, so 201707 is the latest
revision identifier found. Verify on sae.org if a reaffirmation/stabilization notice matters.)

---

## Links

**Item 1 — truck cab parameters (NREL CoolCab/CoolCalc):**
- NREL/TP-5400-52452 *CoolCalc: A Long-Haul Truck Thermal Load Estimation Tool* — https://docs.nlr.gov/docs/fy14osti/52452.pdf
- NREL/TP-5400-66860 *Long-Haul Truck Sleeper Heating Load Reduction Package for Rest Period Idling* — https://www.nlr.gov/docs/fy16osti/66860.pdf
- NREL CoolCab 77-in sleeper cab test (Lustbader & Venson, NREL + Volvo) — https://digital.library.unt.edu/ark:/67531/metadc840767/
- SAE 2023-01-0763 *Effect of Cabin Insulation on the Heating Performance in EVs at Low Temperatures* — https://www.sae.org/publications/technical-papers/content/2023-01-0763/

**Item 2 — BEV truck HVAC power / cold-weather consumption:**
- Öko-Institut ELV-LIVE 2nd report (2025), *Real-world data analysis… battery electric trucks operating in Germany* — https://www.oeko.de/publikation/real-world-data-analysis-of-energy-consumption-activity-and-charging-patterns-of-battery-electric-trucks-operating-in-germany/ · PDF: https://www.oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks.pdf
- ICCT (2023) *Real-world… heavy-duty BEVs* — https://theicct.org/wp-content/uploads/2023/04/HDV-BEVs-real-world_final.pdf
- Dvorak, Kardos, Gellai, Šimić (2025) WEVJ 16:129 (AIT) *Air–Air Heat Exchanger and Improved Insulation for Electric Truck Cabins* — https://www.mdpi.com/2032-6653/16/3/129
- Ramesh Babu, Sebben, Chronéer, Etemad (2025) *Heating load reduction strategies… electric trucks… cold climates*, Thermal Sci. Eng. Progress 60 — https://research.chalmers.se/publication/545506/file/545506_Fulltext.pdf
- JRC (2024) JRC133756 *Energy consumption of mobile air-conditioning systems in electrified vehicles under different ambient temperatures* — https://publications.jrc.ec.europa.eu/repository/handle/JRC133756
- *Predicting Auxiliary Energy Demand in EVs…* Energies 2025, 18, 6092 — https://www.mdpi.com/1996-1073/18/23/6092
- Daimler eActros 600 final winter tests (OEM, 2025) — https://www.electrive.com/2025/02/25/daimler-truck-subjects-the-eactros-600-to-final-winter-tests/

**Item 3 — regulation / VECTO:**
- Commission Regulation (EU) 2025/258 (7 Feb 2025) — https://eur-lex.europa.eu/eli/reg/2025/258/oj/eng · XHTML: http://data.europa.eu/eli/reg/2025/258/oj/eng/xhtml
- Consolidated 2017/2400 (2025-03-01 / 2024-01-01) — http://data.europa.eu/eli/reg/2017/2400
- VECTO (EU Commission page) — https://climate.ec.europa.eu/eu-action/transport/road-transport-reducing-co2-emissions-vehicles/vehicle-energy-consumption-calculation-tool-vecto_en
- VECTO source (first-hand): `mohgsaad-art/VECTO` — `VectoCore/VectoCore/Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/{SSMRun,SSMCalculate,SSMInputs}.cs`, `VectoCore/VectoCore/Configuration/Constants.cs`
- HDEV internal: `docs/research/vecto/06-auxiliaries-all.md` (§1 lorry P_aux flat tables; §2 bus SSM)

**Item 4 — ventilation:**
- VECTO `SSMInputs.cs` (`VentPower`, `VentilationRate`), `Constants.cs` (7/10/20 ACH, 0.56 Wh/m³) — first-hand
- Dvorak et al. 2025 (fresh-air ~100 m³/h for 2 persons @1000 ppm CO₂) — https://www.mdpi.com/2032-6653/16/3/129

**Item 5 — door openings:**
- USDA TB-1375 *Refrigeration Requirements for Truck Bodies: Effects of Door Usage* — http://ageconsearch.umn.edu/bitstream/171539/2/tb1375.pdf
- Brunel thesis (door-opening ≈34 % of refrigeration load, refrigerated body) — https://v-lib-bura1.brunel.ac.uk/bitstream/2438/18126/1/FullText.pdf

**Item 6 — SAE J2765:**
- SAE J2765_201707 (ANSI webstore) — https://webstore.ansi.org/standards/sae/sae27652017
- SAE J2765_201707 (accuristech) — https://store.accuristech.com/standards/sae-j2765_201707
- US EPA 40 CFR 86.1 IBR of J2765 OCT2008 — https://www.gpo.gov/fdsys/pkg/CFR-2013-title40-vol19/pdf/CFR-2013-title40-vol19-sec86-000-2.pdf

---

### Bottom line for HDEV
1. **Cab geometry placeholders stay unsourced.** No verifiable sourced A_surface/U/volume/window value was
   obtainable here; NREL 52452 / 66860 are the correct sources — extract the exact table numbers directly.
2. **BEV-truck HVAC vs ambient:** solid measured *trends* (Öko-Institut, eActros 600 +25 % winter, JRC 4–10×);
   the exact W/ambient truck-cab curves are in Dvorak 2025 (measured) and Ramesh Babu 2025 (simulated) PDFs.
3. **No lorry thermal HVAC model in 2017/2400 (incl. 2025/258).** Thermal heat-balance HVAC is **bus-only (SSM)**;
   using it for a lorry is an HDEV extension — confirmed against VECTO source.
4. **SSM `VentilationRate` has no fresh/recirc split** — one ACH on full volume × 0.56 Wh/m³; neither labelled
   fresh nor recirculated in code. Confirm the 2017/2400 bus-annex wording separately (NOT FOUND here).
5. **Per-door-opening cab air exchange: NOT FOUND** (only refrigerated-cargo-body and building-door data exist).
6. **SAE J2765 = MAC-system COP steady-state bench test; current rev J2765_201707 (2017).**
