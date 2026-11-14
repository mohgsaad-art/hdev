# HDEV / EV Scope: chat summary (28–30 Oct 2026)

**Topics:** grants, grid, tenders, EEA data, revenue streams, business plan, FNA/BNA and the battery passport.

Handover for a new chat. Tags used throughout:
- **[V]** verified in a named source during this chat.
- **[J]** Claude's judgement.
- **[H]** hypothesis, e.g. untested prices.

---

## 1. What happened in this chat

1. Read the latest project memory and the previous chat summary (HC emails, competitors, research).
2. Bob uploaded the documents found for the DK/DE grant schemes, Radius, tenders and EEA. Claude extracted each one and mapped what it requires from the engine.
3. Searched for tender technical requirements. Bob then downloaded the Ressourceindsamling crane-truck tender documents and the EEA 2024–25 battery file.
4. Brainstormed revenue and value streams. Built two visual maps (artifacts) and a handover file for other AIs.
5. Bob collected ideas from ChatGPT, Grok, Gemini and Kiro. Claude ran a deep research task, which produced the strategy and business plan.
6. Asked about the first business-model steps, the template partnership, new outputs needed, FNA vs BNA, and the battery passport.

---

## 2. Key verified facts

### Danish grant pool (Vejdirektoratet, "pulje til grøn omstilling af tung vejtransport" 2026) [V]
- Closed 30 Sep 2026. Max DKK 4m per company. First come, first served. Private companies only.
- **Rates (18 Feb–30 Sep):**
  - trucks 50/40/20% (small/medium/large);
  - depot charging 30/20/5%;
  - publicly accessible part-time depot 40/30/10%.
- **Truck grant:** % × (ZE price − comparable diesel price). The comparable diesel must match use, GVW, kW, axles, suspension, cab and equipment.
- **Lease grant:** % × (NPV of ZE lease − NPV of diesel lease), excluding running costs.
- **Templates:**
  - *Budget template:* units, unit price, total and note for each line. Lines: staff (salary, overhead), external deliveries, other, transport, total, grant. Amounts in DKK excl. VAT.
  - *NPV template for trucks:* up to 8 ZE/diesel pairs, 10 years each. The applicant chooses the discount rate. Formula: cost / (1+r)^(1+year−first year), so **year 1 is discounted one full period**. A residual value goes in as an extra year.
  - *NPV template for chargers:* same layout.
  - *Linked companies:* name, CVR, employees, turnover, balance, partner or linked.
- **Eligible depot costs:** buffer batteries, grid connection, consultancy. Not eligible: costs incurred before the application is received; commissions.
- **Application form asks:** how many trucks charge daily, and the number and power of chargers.
- **Status:** DKK 197.3m to 165 projects by 7 Sep 2026. In the 7 Sep round, 38 of 59 trucks were leased. **A 2027 round is not confirmed.**

### Radius guide "Sæt strøm til den tunge transport" (2025) [V]
- **Pre-work Radius asks for, "possibly with a consultant":**
  - driving patterns;
  - existing capacity;
  - ratings of the site's own installation;
  - number and placement of chargers;
  - charger types;
  - charging patterns;
  - how fees and tariffs affect the business case.
- **Screening fields:** address, desired power, FNA/BNA, commissioning date, whether grid services will be sold.
- **Capacity charge** for 10 kV+ customers: average of the 10 most loaded hours in the last 12 months.
- **Timelines:** 12–18 months with free capacity; 2–4 years without; 5+ years if Energinet must expand.

### Grid connection: FNA vs BNA (Cerius pages) [V]
- **Connection fees from 1 Jan 2026, incl. VAT:**

  | Category | Price |
  |---|---|
  | First 25 A | DKK 23,500 |
  | C | DKK 1,812.50 per A |
  | B-lav | DKK 1,737.50 per A |
  | B-høj | DKK 1,675 per A |
  | A-lav | DKK 1,637,500 per MVA |
  | A-høj | DKK 900,000 per MVA |

  These match the Radius guide's examples: 35 A ≈ DKK 63k; 175 A ≈ DKK 304k; 3 MW ≈ DKK 4.9m.
- **BNA (limited access):**
  - Only for sites at 10 kV or above.
  - Cuts of **0–100%, at any time, without warning, with no compensation.** Can become permanent, down to 0.
  - Ignoring the grid company's signals means disconnection.
  - You pay only your own cable and equipment plus fees; no published price.
  - You can't convert an existing FNA to BNA, and you can't buy BNA capacity for future needs. You can switch to FNA later by paying the normal fee.
- Cerius-Radius pushed its bigger BNA expansion to 2027 (Transportmagasinet, 2 Sep 2026).

### Germany: BMV e-truck charging programme (BAnz 15.05.2026, €1bn 2026–2029) [V]
- **Call A (SMEs):** €500 per kW installed. The applicant must first confirm the grid connection is big enough. Closed the same day.
- **Call B (all companies):** ranked on € requested per kW; cut-off about €230/kW.
- **Call C (public charging):** 70% €/kW + 20% AFIR site + 10% Durchleitungsmodell.
- Battery storage is funded only if technically necessary. **Planning costs are not eligible.**

### Tenders [V]
- **Ressourceindsamling, 6 electric crane trucks (2025), requirement spec (kravspecifikation):**
  - minimum 250 kWh usable, ≥80% left after 8 years;
  - CCS2, ≥150 kW between 10% and 75% charge;
  - crane and compactor running at the same time at full speed;
  - minimum 5.8 t load;
  - after servicing, the truck must be at 80% by 06:00;
  - workshop within 15 km "because of limited range";
  - **no range, consumption or route requirement.**
- **Scoring (linear):**

  | Criterion | 1 point at | 10 points at | Weight |
  |---|---|---|---|
  | Battery | 250 kWh | ≥450 kWh | 25% |
  | Charging power | 150 kW | ≥350 kW | 15% |
  | Load | 5.8 t | ≥9.5 t | 15% in the table, 10% in section 5.4.6 (the document is inconsistent) |
  | Price | +50% vs cheapest | cheapest | 15% |
  | Length, 2nd-axle function, cab entry height | | | 10% each |

  3-axle and 4-axle trucks are weighted ⅓ and ⅔. Awarded to Scania, DKK 66.5m.
- **Ressourceindsamling refuse-truck contract:**
  - 10-year service up to 30,000 km/year;
  - usable battery after 8 years is guaranteed (third-party ohm test);
  - downtime beyond 5 days/year means a loan truck or DKK 2,000 per truck per day.
- **Other tenders:**
  - ARC 2022: min 150 kWh total / 105 kWh available; max 25% loss in 8 years; SMS alerts if a truck isn't charging; battery weighted 10%.
  - ARC 2025: 14 trucks, DKK 122.6m.
  - Thy Recycle 2026: range weighted 20%, COWI advised, one bid. Documents are on Mercell, which only companies can access.
  - Frederiksberg 2026: price 60 / technical 25 / delivery 15.
- **Rambøll for Forsyningstilsynet (Feb 2025):**
  - six firms win 71% of household collection contracts (Verdis, Meldgaard, Remondis, Marius Pedersen, City Container CPH, Lemvig Beton);
  - 87% of contracts with private firms have penalties;
  - tenders increasingly require a minimum share of collections done electrically.

### EEA HDV CO₂ monitoring, reporting period 2024–25 [V]
- Licence CC-BY 4.0 (commercial reuse allowed with attribution).
- **Battery table:** total kWh, usable kWh in simulation, voltage and certification method for 8,020 vehicles (35,021 pack rows).
  - 3,410 rows are "Measured" and 31,611 are VECTO "Standard values".
  - Median usable/total = 0.855. This is the value VECTO uses in its simulation; it may not equal OEM-stated usable capacity.
- Vehicle IDs are hashed VINs. **Make and model are in `hdv_2024_vehicle.zip` (392 MB), which hasn't been processed yet.**
- The 2024 table definition has no electric kWh/km or range fields. Whether the mission-profile file has them is still unchecked.
- Bob's direction: build the library **per model** from spec sheets, with EEA data as a cross-check. Don't average.

### Finance, insurance, battery passport [V]
- Residual value is now called the main e-truck financing risk (Vertelo at an ICCT panel, Sep 2026).
- Munich Re's E-Mobility Warranty Cover targets manufacturers and suppliers. TWAICE's accuracy guarantee is underwritten by a Munich Re subsidiary.
- **Battery passport:**
  - Mandatory from **18 Feb 2027** for EV batteries, including truck and bus packs.
  - Format: DIN DKE SPEC 99100.
  - Contents: ID; materials; static performance values (rated capacity and fade, power and fade, internal resistance and increase, round-trip efficiency, expected lifetime); state of health / state of certified energy, which is kept up to date; usage history.
  - Access: some data public; state of health and usage only for parties with a "legitimate interest".
  - Battery management systems must already (since Aug 2024) store state-of-health data with read-only access for owners.

### Market and funding [V, from the research report]
- EU 2025: 12,858 e-trucks sold (Germany 4,766). Denmark's BEV truck share was 14.8% in 2025 (EAFO). Danish Q3 2026 truck registrations were 558, down from 730 a year earlier.
- The 2026 EU CO₂ flexibility amendment could cut the required 2030 ZE-HDV share from 32% to 16% (ICCT).
- Danish km-toll: CO₂-differentiated, extended to trucks ≥3.5 t from 1 Jan 2027. ETS2 starts 2028.
- Dynamon report from £4,990. ChargeSim eYardPlanner €175/month.
- **Innobooster** requires a CVR plus either DKK 250k gross profit in a published annual account or DKK 100k external risk capital.

---

## 3. Decisions and directions (Bob)

- The streams must be **multiple and independent**, so that if one stream fails, others survive.
- Free "value" partnerships (Vejdirektoratet templates, Radius/Green Power Denmark intake format, Energinet data) count as streams.
- **Spec library per model**, not averages.
- Bob can't access Mercell. The workaround is to ask COWI or request document access (aktindsigt).

---

## 4. Final plan (from the deep research report, simplified)

### NOW (0–12 months): three paid products
1. **Second Opinion pack** [H: DKK 25–45k; first 3 pilots at 50%]
   - Payers: hauliers and collection firms.
   - Content: route energy (normal vs bad day), year-8 battery check, depot kW and grid product, toll/TCO, grant-ready numbers.
2. **Tender help** [H: DKK 30–80k]
   - Payers: a waste company OR one bidder, **never both in the same tender**.
3. **Crane/compactor energy sheet** [H: DKK 30–60k per body type]
   - Payers: body builders (Norba, Geesinkgroup, HMF, Palfinger).

### NOW: free assets
- EEA vehicle catalogue.
- Tender-requirements library.
- DSO intake format.
- Vejdirektoratet-ready numbers.

### NOW: business basics
- ApS before the first invoice.
- Adviser liability insurance (rådgiveransvarsforsikring), with liability capped at the fee.
- **A data clause in every contract** (anonymised measured data feeds the proof record).
- Written neutrality rules.
- Aim for DKK 250k gross profit in year 1, which unlocks Innobooster.

### NEXT (12–24 months)
- Engine licence for consultancies (COWI, Rambøll, NIRAS).
- Lessor check: "fit for the whole lease?"
- Dealer fit check, always labelled as paid for by the dealer.
- 8-year verification of delivered trucks.
- Winter check, **only after cold HVAC is validated.**
- Morning-readiness pilot at one depot.
- Germany: €/kW check and battery-necessity memo.
- Netherlands: grid time-slot check.

### LATER (24+ months)
- "Bankable" named-standard report.
- Residual-value / battery-health index (using passport data).
- Used e-truck checks.
- Insurance-backed guarantees.
- API, marketplace, telematics add-ins.
- Flexibility income.
- ISO 14083 CO₂ reports for shippers; buses; UK.

### Gates
- **Day 90:** at least 2 paid pilots and 1 tender conversation.
- **Month 12:** 10 validation cases and DKK 250k gross profit.
- **Month 24:** 25 cases.

### Biggest risk
One public case of underestimating energy would hurt every stream at once. Stay conservative, keep a validation record, and put a receipt on every report.

### Template partnership (plain terms)
- It is not an endorsement. You make your output fit their forms exactly, then ask for feedback.
- Email Radius (markedsdialog@cerius-radius.dk) with a 2-page intake draft and three questions: what's missing, what's duplicated, would this make review easier?
- Ask Vejdirektoratet (VDM-puljer@vd.dk) what makes applications incomplete, and whether a 2027 pool is planned.
- This is value, not revenue.

### Other streams considered
- Morning-readiness service: the liable parties are the collection firm (fines), the truck supplier (DKK 2,000/day), the workshop (80% by 06:00), the charger supplier, and the depot owner on BNA. An independent evidence log is the core.
- Bid-score optimiser; residual-value index for lessors (candidates: Nordania, Jyske Finans, VFS Denmark, Scania/Daimler finance); telematics marketplace (Geotab EVSA precedent); per-km underwriting (JUNA, PragmaCharge).

---

## 5. New outputs needed now

**Every report**
- Receipt block (engine version, input fingerprint, every default with its source).
- A label on every number: measured / standard / assumed.
- A status line per result.

**Second Opinion pack**
- Component energy split and a monthly table.
- Normal vs bad day (P50/P90 across weather years).
- Usable vs nominal battery.
- Year-8 check (hardest day at the guaranteed capacity).
- Charging: kW per truck and per depot, the 150 kW 10–75% check, slack before 06:00.
- Grid: amperes and kW, customer category, connection fee from the price list, FNA vs BNA, lead-time band, top-10-hour capacity charge with and without smart charging.
- Cost: km-toll by CO₂ class, ETS2 diesel from 2028, NPV using Vejdirektoratet's rule.
- Grant-ready numbers.

**Tender help**
- Minimum usable kWh at year 8 in winter, shown on the tender's score curve.
- Crane and compactor running together (energy and peak).
- Battery vs payload trade-off.
- Offer sheet (bids on the same routes, buyer's weights).
- Spare-truck count.

**Crane/compactor sheet**
- kWh per cycle and per shift, and peak kW, as a VECTO `.vptoel`-style profile.

**BNA**
- "How big a cut can the depot survive and still be ready by 06:00?", run as labelled what-if cases.

**Battery passport preparation**
- Use the passport's field names in the battery data model.
- Have the engine output the passport's usage quantities: energy throughput, full equivalent cycles, charging rates, time at temperature extremes.
- Add a contract clause for sharing BMS or passport data.
- Read DIN DKE SPEC 99100 for the exact field list.

---

## 6. Files and artifacts produced

**Project docs**
- `claude/doc-findings-grants-grid-tenders-2026-10-28.md`
- `claude/handover-tool-and-streams-2026-10-28.md` (tool description plus 30 ranked streams, written for other AIs)
- `claude/outputs-fna-bna-battery-passport-2026-10-28.md`

**Artifacts**
- "EV Scope Stream Map": 35 streams by payer, with a check of which streams fail together.
- "EV Scope Roadmap": a simple NOW / NEXT / LATER map.

**Research report**
- "EV Scope Strategy and Business Plan" (task wf-f57bbbea-2d16-8c9f-8a5c-5ec3815ae2c6).

## 7. Open items

- Process `hdev_2024_vehicle.zip` to link batteries to make and model. Check whether the mission-profile file has electric kWh/km.
- Get the ARC 2025 requirement spec (ethics.dk) and the Thy Recycle Delaftale 1 bilag 1.1 (via COWI or a document-access request).
- Typical fine per missed route in Danish collection contracts: unknown.
- Read DIN DKE SPEC 99100.
- Fix the driver-model bugs and validate consumption first. This gates every paid product.
