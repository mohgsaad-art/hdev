# During Construction: Charging Infrastructure on Shared Parking Areas (Guide for Developers and Contractors)

**Source file:** `Under_byggeriet_Ladeinfrastruktur_på_delte_parkeringspladser.pdf`
**Category:** Charging infrastructure — guide (construction-phase technical/commercial, for developers & contractors)
**Original language:** Danish (translated/summarized to English below; proper nouns kept in Danish)
**One-line summary:** The second guide in Region Hovedstaden/Copenhagen Electric's three-part series ("Under byggeriet" = "During construction"), aimed at developers ("bygherrer") and contractors ("entreprenører"), covering legislation, sizing methodology, charger technology choices, ownership/leasing models, payment structures, and detailed electrical installation requirements for EV charging on new-build shared parking areas.

## Administrative / Issuing Body
- **Publisher:** Region Hovedstaden, Center for Regional Udvikling; program Copenhagen Electric, Kongens Vænge 2, 3400 Hillerød. Phone +45 38 66 55 05. Email cph-electric@regionh.dk.
- Marked "Confidential" on every page (same note as the companion "Før byggeriet" document — likely a template artifact, not necessarily a substantive confidentiality marking).
- Second of three guides (Before/During/After construction); shares much boilerplate (glossary, legal background, sizing formula) with the other two in this series but targets the construction/procurement decision-making phase specifically.

## Glossary (Ordforklaring) — as defined in source
Largely identical to the "Før byggeriet" glossary, with these additions/differences:
| Term | Definition |
|---|---|
| Højeffektlader (High-power charger) | Collective term for "hurtiglader" and "lynlader" (fast and rapid/ultra-fast chargers) |
| Laveffektlader (Low-power charger) | Also called "normallader" (normal charger) |
| Hurtiglader | DC charger, **50–100 kW** |
| Lynlader | DC charger, **at least 150 kW** — the most expensive type, highest charging speed |
| Normallader | AC charger, **3.7–22 kW** |
(Other terms — EMSP, Ladeboks, Ladeinfrastruktur, Ladeoperatør, Ladeplads, Ladepunkt, Lader, Ladestander, Ladepark, Ladeøer, Lastbalancering, Udtag, V2G — defined identically to the "Før byggeriet" glossary; see that document's knowledge file for full text.)

## Introduction
- Cites the same **Bilkommissionen Delrapport 2 (February 2021)** as the companion guide.
- States: **"Der er for nuværende ikke nogen lovgivning, der stiller krav om opsætning af ladestandere ved nyetablering af boligbyggeri."** (There is currently no legislation requiring the installation of chargers when newly constructing residential buildings.)
- EV owners in housing organizations with shared parking are often left with only public charging infrastructure access — more inconvenient and expensive, since they typically lack their own parking space for a home charger. This can be a barrier to EV adoption.
- Whether charging is available at a given residence/lease can materially affect prospective residents'/buyers' choice of housing organization.
- Same list of benefits as in "Før byggeriet" (time/cost savings from overnight charging, lower kWh price at normal chargers, gentler AC charging on batteries, reduced grid peak, reduced need for public charging infrastructure) — reproduced identically.
- Recommends developers/contractors seek guidance from an authorized electrical installer or knowledgeable consultant on expected charging demand, charger type, installation, maintenance, and operations.
- **Key framing line:** "Bygherrer og entreprenører har de bedste muligheder for at sikre, at flest muligt med delt parkering kan få dækket deres ladebehov på den fælles parkeringsplads." (Developers and contractors have the best opportunity to ensure that as many people as possible with shared parking can have their charging needs met on the shared parking area.)

## Relevant Legislation (Three Laws Identified — Narrower List Than "Før byggeriet")
This guide identifies **three** relevant laws/executive orders (vs. four in the "Før byggeriet" guide, which also covered Vejloven/Privatvejsloven in more depth): **Planloven**, **Ladestanderbekendtgørelsen**, and **AFI-loven**.

### Planloven
- Same core content as "Før byggeriet": no legal basis to require charging-infrastructure installation; municipality may require parking-layout provisions for EV/car-share vehicles; normal chargers (≤22 kW) generally not classified as a technical installation requiring planning/access review.
- Adds a developer-facing framing: **"Hvilke krav til ladeinfrastruktur kan bygherren blive stillet over for i lokalplan/kommuneplan?"** (What charging-infrastructure requirements might the developer face in the local/municipal plan?) — municipal plan may embed policy goals in hovedstruktur/retningslinjer/rammebestemmelser, primarily as land-use restrictions on where building may occur and whether only low- or high-power chargers may be installed in a given area. Local plans can require a certain number of parking spaces be used for EV/car-share vehicles, similar to disabled-parking space requirements (citing the same Overliggeraftale, 25 June 2020).

### Ladestanderbekendtgørelsen
- Same core provisions as "Før byggeriet" (entry into force 10 March 2020; EU EPBD basis; building-owner categories; SME exemption with the same definition; Figure 1/Rambøll table — again not extractable in detail as text; "larger renovation" 4-criteria test identical, incl. the same **>10 parking spaces**, **<7% of total renovation cost** thresholds).
- Adds: at new construction/expansion/major renovation, the Executive Order's requirement is **part of the building permit** — it is therefore at minimum addressed during building-application review if not already discussed during the planning/local-plan phase.
- Same "expected revision" discussion as "Før byggeriet" (autumn 2023 EPBD recast proposal), but this guide adds more detail on anticipated changes:
  - Preparation may be defined as **more than just empty conduit** in the revision proposals, which could affect installation economics.
  - **"Right to plug"** — a proposed requirement giving residents on shared parking the *right* to have a charger installed on request; if enacted, the housing organization/property board becomes responsible for ensuring chargers for residents on request.

### AFI-loven (New Section — Not Covered in "Før byggeriet")
- **Lov om infrastruktur for alternative drivmidler til transport (AFI-loven)** — entered into force **6 April 2022**. Retsinformation: retsinformation.dk/eli/lta/2022/412
- Purpose: sets requirements for establishment and operation of **publicly accessible** chargers.
- **Figure 2 in source** lists AFI-loven's underlying executive orders (reproduced as a structured list since the figure was an image/diagram):
  - **BEK nr. 1073 af 28/06/2022** — Executive Order on procuring entities' conclusion of agreements on the right to act as operator of publicly accessible charge points
  - **BEK nr. 414 af 04/04/2022** — Executive Order on municipalities' and regions' payment to operators of publicly accessible charge points
  - **BEK nr. 1010 af 27/06/2022** — Executive Order on requirements for technical specifications for publicly accessible infrastructure for fuels and alternative drive means for transport
  - **BEK nr. 688 af 07/06/2023** — Executive Order on requirements for publicly accessible infrastructure for fuels and alternative drive means, etc.
  - **BEK nr. 2635 af 28/12/2021** — Executive Order on the Danish Road Traffic Authority's (Færdselsstyrelsen) tasks, powers, and appeal access
- AFI-loven and its executive orders set requirements for procuring entities installing publicly accessible chargers, for charging operators, and technical requirements for chargers incl. signage — relevant when tendering charger work, especially if chargers become publicly accessible.
- AFI-loven implements parts of the **AFIR directive** (EU Alternative Fuels Infrastructure Regulation), giving international compatibility standards. In practice: all newer EVs in Europe can use the **Type 2** connector for low-power charging and **CCS Combo** for high-power charging.

## Placement and Number of Charge Points

### Number of Charge Points
- Same framing as "Før byggeriet": no one benefits from over-installing; important to hit the right level given shared-parking exclusivity concerns.
- **Pre-assessment questions (developer-facing, new in this guide):**
  - How many cars need to charge simultaneously, and thus how many charge points (outlet count) are needed across the whole shared parking area — from day 1 and in future?
  - What type of chargers are needed? Distinguishes **laveffektladere (≤22 kW AC)** vs. **højeffektladere (≥50 kW DC)**.
  - Is fast charging needed for residents, guests, the housing organization's fleet vehicles, and/or others sharing the parking area — e.g., to use the charge space more dynamically?
  - If few high-power chargers or many low-power chargers are installed such that overall ampere demand is high, the installation should be split off from the building's electrical panels onto **separate electrical panels**; load balancing via a load-management system is advantageous for ampere demand/purchase.
- **Same calculation formula as "Før byggeriet":** A × B/(C/D), with A=100 cars, B=31% EV share by 2030 (1M EVs of 3.26M fleet), C=350 km average EV range, D=45.5 km/day average driving distance → suggests ~4 outlets/2 double-outlet stands for 100 parking spaces. Same caveats about overdimensioning and plug-in hybrid higher relative demand (3.7 kW AC limit, ~50 km electric range) reproduced identically.

### Placement Considerations
- Recommends **ladeøer/-grupper** (charging islands/clusters) for easy discovery, and cheapest to install together near the connection point; accessibility/visibility also factor in.
- **Wall-mounted charge box on the building facade** often minimizes installation cost, though many charge boxes have only a single outlet, requiring more boxes.
- **Key efficiency insight (elaborated more here than in "Før byggeriet"):** if sufficient free parking spaces exist for a fully-charged car to move to, this is a valuable resource for collective charging — a single charge outlet can effectively serve **around three EVs** if they charge at staggered times across the day. Utilization and infrastructure economics improve significantly with free parking spaces available, vs. a charger usable by only one EV per day.
- **Strategic placement alternative achieving a similar effect (Figure 3, credited to Rambøll):** a two-outlet charge stand placed at the **corner between four parking bays** can potentially serve up to **four cars over a 24-hour period** without needing to move any car — only the charging cable needs to be unplugged/replugged when one session ends and the next begins.
- If every unit has a dedicated parking space, guest parking or other shared areas can be used for collective charging; equipping every individual dedicated space with its own charger is possible but **significantly increases total installation cost**.
- Placement must comply with local plans and road law. If parking is on a **private fællesvej**, changes (incl. signage) require road-authority and police approval. Local-plan changes are handled by the municipality. A rapid-charging station requires considering noise/traffic impact and police/road-authority rules and approvals.

## Choice of Charger and Charging Strategy

### Types of Chargers and Boxes
- First key decision: normal chargers (AC), high-power chargers (DC), or a combination — depends on how fast charging needs to be met.
- For most residential construction, normal chargers are the right solution; high-power chargers may be desirable in some situations. Normal chargers are cheapest to install.

**Normallader (Normal Charger) details:**
- AC chargers, up to **22 kW**, primarily using the European 3-phase **Type 2** connector.
- Most solutions based on: a free-standing charge stand with two outlets, a charge box with one or two outlets, or two charge boxes on a shared post (Figure 4, credited to **DTU Wind**).
- Free-standing/post-mounted charge points typically supplied via empty conduit ("tomrør"); wall-mounted ones via cable tray ("kabelbakke").
- **Recommendation: supply 22 kW (32 amps/3-phase) to each charge outlet**, regardless of stand or box type — even though not all EVs currently support 22 kW (many 3-phase-charging cars are limited to 11 kW; single-phase cars limited to 3.7 or 7 kW, citing ev-database.org). Rationale: all car models can then use their maximum charging speed, and the price difference between 11 kW and 22 kW installations is relatively small. **Condition:** load balancing should be considered simultaneously (see below), so supporting 22 kW doesn't itself increase the parking area's total power-capacity requirement — requiring "intelligent"/smart-charging-capable chargers.
- Some two-outlet chargers/boxes can perform **internal load balancing ("power sharing")** — e.g., splitting 22 kW so one EV gets the full 22 kW alone, or two simultaneously-charging EVs each get 11 kW.
- **Sidebar "Smartladning - Intelligente ladestandere":** Not all chargers are "smart" — cheapest chargers just deliver the rated power and nothing else. Smart chargers cost somewhat more but enable lower TCO and allow: adjusting power up/down (incl. load balancing); time-shifting charging to when power prices are lowest or greenest; communication with the grid and building about available capacity, letting e.g. a charging operator/EMSP adjust power (kW) based on the current grid/building situation.

**Højeffektslader (High-Power Charger) details:**
- For large parking facilities, adding a DC charger (e.g., **50 kW**) may be worth considering. **Significantly more expensive to install: up to 450,000–600,000 DKK (2022 prices)**, and requires greater power capacity (**up to 125 amps**).
- May be appropriate at shared-parking housing as a supplement to normal chargers in special cases: e.g., a shared electric car-share vehicle, buildings with frequent visitor traffic, or (**rule of thumb**) buildings with **more than 20 normal chargers**. Can serve uneven charging demand typical of car-share vehicles or residents with multiple daily errands.
- **A 50 kW charge stand can satisfy extraordinary needs, delivering up to 250 km of range per hour of charging.**
- If made publicly accessible, can also serve short-stay visitors; recommend introducing **time-limited parking** (e.g., **1 hour**) to ensure higher utilization, improving the overall economics of establishment and operation.

### Lastbalancering (Load Balancing) — Expanded Technical Section
- Should be considered as a functionality in the desired charger(s); especially relevant beyond just a couple of normal chargers, but can be economically relevant even with few chargers.
- Ensures EVs on the parking lot share available power, with total load never exceeding a predefined cap — both a safety measure (preventing fuses from blowing) and a way to serve more simultaneously-charging EVs without expensive capacity upgrades, by dynamically redistributing power among charging EVs.
- **Worked numeric example (Figure 5, credited to Rambøll):** With load balancing, a supply scope of **32 amps (22 kW)** can suffice instead of **80 amps** (equivalent to five 11 kW chargers all charging at full power simultaneously).
  - At **17:00**: two cars both charge at full 11 kW.
  - At **18:00**: a third car arrives; load balancing reduces power to **7.3 kW per car**.
  - At **20:00**: two more cars start charging and get full power, since the other three have finished charging in the meantime.
- Notes EVs on shared parking often charge at staggered times and/or park long enough (e.g., overnight) that they don't need full 11 kW power for the entire connected duration to achieve a full charge.
- If a load management system is used to purchase fewer amps than would be needed for all chargers to deliver full power simultaneously, **residents should be informed** and expectations set that charging may sometimes take longer than at full 11 kW power. Power delivered depends on the ampere purchase and desired service level; overnight charging rarely has a problem if it takes **7–12 hours**.

**Table 1 — Ampere purchase vs. number of outlets, with/without load balancing, and cost savings (Figure 6, credited to Rambøll):**
| Number of charge outlets | Amps at full power (11 kW/outlet) | Amps with load balancing (recommended min. kW) | Savings on ampere purchase @ 1,250 DKK/amp |
|---|---|---|---|
| 2 | 32 | 25 | 8,750 DKK |
| 3 | 50 | 25 | 31,250 DKK |
| 4 | 63 | 25 | 47,500 DKK |
| 5 | 80 | 32 | 60,000 DKK |
| 6 | 100 | 40 | 75,000 DKK |
| 7 | 125 | 50 | 93,750 DKK |
| 8 | 125 | 50 | 93,750 DKK |

- **Table note (verbatim meaning):** with load balancing accepting down to **4.3 kW**, an EV with a **50 kWh battery** takes **~7 hours** to charge from 20–80%, while an EV with an **80 kWh battery** takes **just over 11 hours** to charge from 20–80%.

### Eje eller leje ladestanderne? (Own or Lease the Chargers?)
- With enough shared-parking chargers, most residents can meet their charging needs at home; only on long trips would public charging infrastructure be needed — payable via the operator's app, and (for chargers ≥**50 kW** installed after AFI-loven took effect) by **credit card**. No operator customer relationship is required for occasional away-from-home charging.
- If chargers are ready at building commissioning, the developer must decide: does the housing organization/property board **own** or **lease** the chargers?

**Owning the chargers:**
- Developer can handle all installation, with the housing organization/property board handling subsequent operations, OR the developer/organization can contract a **charging operator/EMSP** to handle some or all operations.
- A service agreement with an operator/EMSP can secure **tax refund** ("afgiftsrefusion"), lowering electricity costs; the operator/EMSP can also handle back-end operations, administration, and resident/end-user billing.
- Higher upfront establishment cost (purchasing chargers, excavation, ampere purchase); organization must handle billing/collection, operations, and allocate resources if self-managing — though systems exist to make this manageable. In exchange, per-kWh price for residents is typically **lower**. A suitable kWh price must be set so establishment and operating costs balance.
- **Tax note:** cannot receive both tax exemption and tax refund on the same electricity — chargers must therefore be connected to their **own settlement meter with its own "aftagenummer"** (off-take number) if the building has electric heating or other tax-exempt electricity or solar panels.
- Footnote: **2 September 2020**, the "sideaktivitetsbekendtgørelsen" (ancillary-activities executive order) was amended making it possible for housing organizations to establish and operate EV chargers (bl.dk link cited).

**Leasing the chargers:**
- Charging operator typically handles both establishment and all subsequent operations — often free or low-cost to the developer/organization. Easiest/cheapest for the developer, but the operator needs to recoup its investment, typically via a **higher kWh price** for residents — bounded by what the market will bear (residents could otherwise charge at nearby public chargers or en route to/from work, risking underuse of the housing chargers).
- Developer may alternatively handle excavation/ampere-purchase itself to give more flexibility elsewhere and secure lower resident prices.
- If leasing/operating via a charging operator, developer must decide: single shared operator for all collective chargers, or let residents choose among **multiple** operators on the shared parking area. Multiple operators can create price competition, though operators may be reluctant to compete once they've made an establishment investment to recoup. Downside: **load balancing across chargers from different operators is not possible** — a larger total number of chargers may be needed before multiple operators becomes sensible.

**Choosing before/after building commissioning:**
- If not decided before commissioning whether charger operations are part of facility management or a pre-arranged operator agreement, this becomes a later decision — harder or easier to push through depending on the operational decision-making structure at that point.
- Deferring the decision to residents/property boards has downsides: difficult market to navigate (many and growing business models); hard to get resident-democracy buy-in for financing a solution only a minority currently benefits from; shared parking areas often already feel short of spaces, and an EV effectively getting a "private" space at the charger can feel unfair — partially mitigated via shared guidelines (e.g., the charge space is the last space used if free).
- **Recommendation: choose a solution for the housing organization already at commissioning**, and incorporate excavation work / at minimum empty-conduit installation into the building's construction works to minimize later charger-installation costs.

### Betalingsstrukturer (Payment Structures)
**When chargers are owned and operated by the housing organization:**
- Developer/subsequent property board/resident democracy can decide the payment structure itself.
- Establishment costs/charger purchase can be taken from the construction budget (centrally funded infrastructure improvement, potentially reflected in higher sale/rent prices later) — benefiting an expected growing user base, but imposing a cost on all units regardless of near-term EV ownership.
- Alternatively, keep charging-infrastructure economics separate, e.g., as its own construction/financing budget funded via a surcharge per kWh — administered by the property board/organization afterward. This means early EV adopters bear a larger share of financing a shared infrastructure that more people benefit from over time — an uneven cost distribution. A middle-ground/balanced approach between these two models is also possible.

**When chargers are owned by the housing organization but operated by a charging operator:**
- Developer may need to choose the best future charging solution on behalf of future residents; best solution depends on economics for developer, organization, and end users, plus operational resourcing.
- Business models vary; developer could consider a model where a **percentage of the kWh price** goes to the operator for running operations, with the rest to the organization/property board — kWh pricing could follow the electricity **spot price**, or an average spot price over a preceding period (e.g., a month).
- Alternative model: **a fixed monthly price per charger** paid to the operator for administration, regardless of how much is charged.
- Despite potentially larger establishment costs, revenue from electricity sales at the chargers can mean investment payback within a few years — timing depends on establishment costs and the kWh price charged to residents/guests. If chargers (or some of them) are made publicly accessible, possibly only at certain times (e.g., daytime), a slightly higher price for outside guests can further reduce payback time.
- Different operators run different business models; most offer relatively few but well-tested/documented solutions. Some operators value a recognizable design and known/trusted charger models, so **not all operators are willing to operate hardware they don't own** — potentially limiting competition under this ownership model.
- When the first operator contract for charger operations expires, a new operator willing to take over must be found (unless new, more technologically mature chargers are purchased at that point). How operator business models/the charging industry will look at that future time is hard to predict.

**When the charger is leased/owned by the operator:**
- Operator handles everything related to the chargers. If the operator funds all excavation/installation work incl. ampere purchase, it needs to recoup this via a higher kWh price for residents.
- **Caution flagged:** such agreements often have very long terms — **typically 10 years** — so it matters to consider the kWh price carefully when the agreement is made, since a bad/expensive deal is lived with for a long time.
- Easier for the operator to build a good business case with no excavation/ampere costs. If only a single charger is installed, the operator's risk is much lower, potentially supporting lower kWh prices for users. If excavation, empty conduit, and ampere are part of the developer's own construction works, switching to a new operator later is also easier, since there's no question of buried-cable ownership to resolve. If the operator has paid for excavation/ampere, it's worth considering upfront what happens post-contract, and whether the operator may resell this to the succeeding operator.
- If quotes are obtained from multiple operators or a tender is run, end-user prices can become a competitive parameter — potentially fixing an amount per kWh addable on top of the spot price.
- Residents often prefer chargers on shared parking closed to non-residents (via charge cards or an app). Worth considering whether some chargers should be publicly accessible, perhaps only part of the day, to increase operator revenue potential and thus support lower kWh prices for residents — the potential here depends heavily on the housing organization's location and nearby workplaces/other shared-parking housing.
- Few operators currently offer subscription/all-inclusive solutions; for most typical-driving-pattern EV owners this hasn't been the most economical choice — though some drivers prefer simplicity over tracking fluctuating kWh prices, and high-mileage drivers might benefit from a fixed price regardless of charging location (home vs. away).

## Installation of Charging Infrastructure
- All electrical work on charge boxes and their installation is **subject to authorization ("autorisationspligtigt")**. Recommend an installer already experienced with charging infrastructure, since EV-charging installation dimensioning differs from standard installation dimensioning.
- First sensible step: assess the building's electrical capacity. If this assessment was done earlier in planning without chargers as part of the construction project, determine how much extra power/how many amps can be drawn without overloading the system.
- Buying too many amps is expensive and unnecessary — total power demand for planned chargers should be determined based on desired charging speed (kW) and number of stands to be installed. Consider implementing a **load management system** to distribute power evenly and avoid overload (load balancing); such systems can also enable time scheduling and power control.
- Installation should have its **own electrical panel** and own supply from the grid company's designated connection point/transformer. Installation must at minimum have a **sub-meter ("bimåler")** to separate charging consumption from other consumption.
- **Each charge outlet must be protected by its own RCD (residual-current device / fejlstrømsafbryder) with a maximum trip current of 30 milliamps (mA).** Must check whether the charger has built-in protection against DC fault currents; where not assured, a **"type B" RCD** must be used.
- To ensure all EV types can charge, **transition resistance to earth must be under 50 ohm**. If publicly accessible, chargers must be protected against **transient overvoltage** — transient protection must be installed upstream of the chargers.

### Charging on 3 Phases (technical sidebar)
- For an EV capable of 11 kW charging to charge at full power, it must charge on 3 phases — charging infrastructure should therefore always be installed as a 3-phase installation.
- Even when prepared for 3-phase charging, some EVs (e.g., plug-in hybrids) only charge on a single phase, limited to 3.7 kW or 7 kW. Recommend **"rotating" phases** between charge outlets to spread load evenly across all three phases rather than one. Some intelligent chargers handle this themselves and don't need manual rotation.

### Kabeltrækning (Cable Routing), Now and for Future Expansion
- Cost of conduit/cable-tray routing is markedly lower during the construction phase than at later installation — important to plan good solutions from the start. Consider oversized empty conduit or routing paths, plus cable wells for joining cables and bends for future inspection, and the ability to pull new cables if existing ones are damaged.

**Tomrør (Empty Conduit):**
- **Rule of thumb: at least one 110 mm empty conduit per area of 4× 11 kW charge outlets.**
- Conduit routing must always allow future cable-pulling (no sharp bends) — bend radius max. **one 15-degree bend per 500 mm**. All conduits prepared with a pull cord and marked on drawings. "As-built" drawings must measure/mark conduit positions, ensuring conduits can always be located. All conduit ends must be capped to prevent debris ingress.
- Where cable trays/grid trays/ladders are installed for future chargers, allocate **min. 50 mm tray width per 4 chargers** — e.g., preparing for 11 chargers requires a tray width of at least **150 mm (3 × 50mm)**. Cable routing must comply with **DS/EN60363** [note: likely a typo for DS/EN60364, the same standard referenced elsewhere in this document series — reproduced as written in the source].

**Nedgravning (Underground Burial):**
- Recommend burying all empty conduit at a **minimum depth of 0.7 meters** to minimize damage risk to conduit and future cables.
- Per **Bekendtgørelse om sikkerhed for udførelse og drift af elektriske installationer (BEK 1082 § 41)** (Executive Order on safety in the execution and operation of electrical installations):
  - Cables must be buried at least **0.35 m deep** in finished terrain.
  - Cables buried at **less than 0.7 m depth** must be protected by pipe, U-profile, or cover plates.
  - Cables buried at **more than 0.7 m depth** need no further mechanical protection, provided a **marking tape** is placed approx. **0.2 m above** the cable. Where multiple cables are within 0.2 m of each other (outermost cables), only one marking tape is required.
- Cables must be properly protected against mechanical impact and weather. Cables/conduit can advantageously be installed via directional/guided underboring; where the route passes under existing structures, a ground-displacement "rocket" (jordfortrængningsraket) can be used to avoid disturbing surface pavement.

### Tilslutning af ladestandere til elnettet (Grid Connection)
- Local grid companies are **obligated to connect** customers geographically within their supply area upon payment of a connection fee — regardless of whether the customer is a public authority, private company, or citizen. Grid connection includes purchasing a **delivery scope (a number of amps)** from the grid company.
- **A single ampere costs approx. 1,000–1,500 DKK incl. VAT (2023 price).**
- Registering installation work must follow the grid company's business procedures; registration must occur **before** installation work begins. Customer must state expected power demand and consumption pattern (consumer type: EV charger, whether a load-management system is used, etc.) when contacting the grid company. The grid company then typically responds regarding connection options; only once the contractor submits an actual connection request does the grid company prepare an offer and timeline.
- If the grid company determines a **new transformer station** is needed, delivery time can be very long — **up to 3 years**. Especially relevant if multiple fast/rapid chargers are desired.
- **Sidebar "Behov for ampere" (Ampere Demand):** An **11 kW** charger on 3 phases needs **16 amps**; a **22 kW** charger on 3 phases needs **32 amps**. If no spare capacity exists, extra amps must be purchased from the local grid company — future needs (how many chargers desired longer-term) should be considered, since it can be cost-effective to plan conduit etc. for the expected expansion from the start.

### Anlæg/etablering (Construction/Establishment)
- Scope of establishment work depends partly on whether chargers are building-mounted or free-standing at the end of (selected) parking bays.
- Excavation work requires obtaining info on existing cable/line routing (**LedningsEjerRegistret, LER.dk** — Danish registry of buried utility lines) to prevent damage — applies even to ostensibly new areas, since lines may run through the project area. Excavation should generally be done cautiously, as marked-line accuracy can carry some uncertainty. Applicable environmental requirements for disposal of excavated material must be observed. After work, new lines must be reported by the line owner to LER.dk.
- Charger installation requires **registration with the grid company** even when using an existing connection/existing capacity — to help register electricity demand (Fællesregulativet 2022 point 2.1).

## Considerations on Electric Car-Sharing (Delebiler på El)
- Same content/framing as in "Før byggeriet": car-sharing can let some residents forgo car ownership, reducing parking pressure among tenants; potential economic, health, congestion, and environmental benefits; municipality has authority under **Færdselsloven** to determine EV/other electric-vehicle parking locations and may set restrictions in its parking policy; per **Erhvervsstyrelsen**, municipalities may set requirements on parking layout for EV/car-share vehicles even though Planloven doesn't allow mandating charger installation itself. Municipality may, per the Planning Act, set local-plan provisions on the number of parking spaces for different uses (e.g., EV and car-share vehicles), their location and layout on a given property.

## Where to Find More Information
Identical reference list to "Før byggeriet": AlmenNet's toolbox, Elbilviden.dk, KL's page on municipal charging-infrastructure rollout, Ladestanderbekendtgørelsen (retsinformation.dk/eli/lta/2020/181), Building Regulation guidance on the Executive Order, AFI-loven (retsinformation.dk/eli/ft/201712L00027), and Vejdirektoratet's handbook on planning/establishing EV charging infrastructure (vejregler.dk link, same hash as noted in the companion document, corresponding to `ac359ff9cfba478b8f60cae21d0030dc.pdf` elsewhere in this project).

## Referenced Legislation/Regulation (consolidated, including items unique to this guide)
- Planloven, Ladestanderbekendtgørelsen (retsinformation.dk/eli/lta/2020/181), AFI-loven (retsinformation.dk/eli/lta/2022/412) and its five listed executive orders (BEK 1073/2022, BEK 414/2022, BEK 1010/2022, BEK 688/2023, BEK 2635/2021)
- Færdselsloven, Erhvervsstyrelsen guidance basis (Overliggeraftale, 25 June 2020)
- **BEK 1082 § 41** — Executive Order on safety in execution/operation of electrical installations (cable burial depth rules)
- **DS/EN60363/60364** — electrical installation standards (cable routing / simultaneity factor)
- **Fællesregulativet 2022** (grid registration requirement)
- **LER.dk** (Ledningsejerregistret) — utility line registry
- **Sideaktivitetsbekendtgørelsen** amendment of 2 September 2020 (enabling housing organizations to establish/operate EV chargers)

## Named Organizations / Credits
- Region Hovedstaden, Center for Regional Udvikling, Copenhagen Electric
- Rambøll — credited for Figures 3, 5, 6 (placement diagram, load-balancing example, ampere/outlet table)
- DTU Wind — credited for Figure 4 (charger type illustrations)
- ev-database.org — cited for EV charging-capability data

## Key Numeric Data Table (consolidated quick reference, verbatim from source)
| Metric | Value |
|---|---|
| Normal charger power range | 3.7–22 kW AC |
| Recommended supply per outlet | 22 kW (32A/3-phase) |
| Typical 3-phase-limited EV | 11 kW |
| Typical single-phase-limited EV | 3.7 or 7 kW |
| DC/fast charger power | 50–100 kW |
| DC/rapid ("lynlader") charger power | ≥150 kW |
| 50 kW DC charger install cost (2022 prices) | up to 450,000–600,000 DKK |
| 50 kW DC charger power requirement | up to 125 amps |
| Range delivered by 50kW charger | up to 250 km per hour of charging |
| Rule of thumb for considering a fast charger | >20 normal chargers on site |
| RCD max trip current per outlet | 30 mA (Type B if no built-in DC-fault protection) |
| Min. earth transition resistance | <50 ohm |
| Min. empty-conduit burial depth (recommended) | 0.7 m |
| Min. legal cable burial depth (BEK 1082 §41) | 0.35 m (with protection if <0.7m) |
| Marking tape height above cable (if >0.7m deep) | ~0.2 m |
| Empty conduit sizing rule of thumb | 1× Ø110mm conduit per 4× 11kW outlets |
| Conduit bend limit | max. one 15° bend per 500mm |
| Cable tray width rule of thumb | 50mm per 4 chargers |
| Cost per ampere (grid connection, 2023 price) | ~1,000–1,500 DKK incl. VAT |
| Transformer station lead time (if new one needed) | up to 3 years |
| Typical operator lease/ownership contract term | ~10 years |
| Ampere cost used in load-balancing savings table | 1,250 DKK/ampere |
| 50kWh battery charge time (20-80%) with load balancing (4.3kW floor) | ~7 hours |
| 80kWh battery charge time (20-80%) with load balancing (4.3kW floor) | just over 11 hours |

## Relevance Notes for HDEV/Depot Tool (Claude's own framing, not from source)
- Like its companion guides, this document targets light-duty/passenger EV residential charging, but the **detailed electrical installation specifications** (RCD Type B requirement, 50-ohm earth resistance, phase rotation, conduit sizing rules, cable burial depth rules per BEK 1082 §41, ampere-cost benchmarks) are Danish regulatory/practical reference points that would also apply as baseline electrical-code context for HD depot charging installations in Denmark, even though the power scale (11-50kW) is far below HD truck charging (150kW-1MW+).
- The **load-balancing worked example and ampere-savings table** is a directly transferable methodology pattern (not the numbers themselves) for depot-scale load management economics — i.e., quantifying DKK savings from load balancing vs. full-simultaneous-power provisioning.
- The **10-year typical charging-operator contract term** and revenue-share/fixed-fee operator business models described here parallel the municipal on-street contracts (see `roskilde-charging-contract.md` and `lyngby-taarbaek-charging-contract-draft.md` in this knowledge base) and may be a useful cross-reference for depot/CPO commercial structuring.
