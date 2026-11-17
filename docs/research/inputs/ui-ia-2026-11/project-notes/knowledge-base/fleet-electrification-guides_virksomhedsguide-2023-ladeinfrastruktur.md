# Charging Infrastructure for Businesses (Virksomhedsguide 2023)

**Source file:** `Virksomhedsguide 2023.pdf`
**Category:** Fleet electrification guide / policy report
**Original language:** Danish (translated to English below; proper nouns kept in Danish)
**One-line summary:** A September 2023 Region Hovedstaden / Copenhagen Electric guide (prepared by Rambøll, updating a 2021 edition) on planning and establishing EV charging infrastructure at businesses — covering legal requirements (Ladestanderbekendtgørelsen), needs assessment by user group, charger types/costs, load balancing/smart charging, rollout process, and three detailed company case studies (Dansk Miljø- og Energistyring, Rambøll, Grundfos).

## Publisher, Year, Audience

- **Publisher:** Region Hovedstaden, **Center for Regional Udvikling**, **Copenhagen Electric**. Contact: Kongens Vænge 2, 3400 Hillerød; Tel +45 38 66 55 05; Email cph-electric@regionh.dk; Web www.regionh.dk.
- **Authors:** **Line Engell Nørby, Sebastian Ovesen, Mette Hoé**, from **Rambøll**.
- **Publication date:** **September 2023**.
- **Provenance:** "Guiden er en opdatering af den tidligere guide fra 2021" (This guide is an update of the earlier guide from 2021). Reusable text/graphics from the original guide were reused with permission from **Peter Bach Andersen, DTU Wind** (Technical University of Denmark, Wind Energy department). The guide builds on content from the **vejregel-håndbogen "Planlægning og etablering af ladeinfrastruktur til elbiler"** (the official Danish road-regulation handbook "Planning and establishing charging infrastructure for electric vehicles").
- **Contributors/reviewers thanked:** Kim Villadsen (Dansk Miljø- og Energistyring), Peter Rosen Christensen and Søren Høgh (Grundfos), Morten Frydkjær (Rambøll), Kathrine Jørgensen (Copenhagen Electric, Region Hovedstaden). Also thanks unspecified contributing charge operators and platform operators.
- **Intended audience:** Primarily businesses with parking areas used by their own vehicles, employees, guests, and/or the public; also usable by educational institutions and other public/private organizations with parking areas.
- **Explicit disclaimer:** "Denne vejledning er ikke en erstatning for professionel vejledning fra en autoriseret installatør." (This guide is not a substitute for professional guidance from an authorized installer.)
- **Marked "Confidential"** on every page in the extracted text — note this classification as given in the source; treat accordingly within the project.

## Policy Context

- Denmark's 70% greenhouse-gas reduction target is cited as the driver requiring a large share of passenger transport to be electrified within a relatively short timeframe ("inden for en årrække").
- Home charging expected to remain the largest share of EV charging, but public/semi-public charging (including at businesses) plays a major role, especially in urban areas where fewer people have home-charging access.

## Terminology / Glossary (Ordforklaring) — Full List with Definitions

| Term (Danish) | English gloss | Definition (from source) |
|---|---|---|
| EMSP | E-mobility service provider / platform operator | A service company providing software to manage charging facilities; does not supply chargers themselves, only the software solution. Often used when a business wants to operate its own chargers. |
| Hurtiglader | Fast charger | Also called DC charger. High-power charger, charges at **50-100 kW**. DC; conversion from AC to DC happens in the charger, not the vehicle. Typically larger/more expensive than a normal charger; usually requires expansion of existing electrical installation/capacity. |
| Ladeboks | Charging box | A wall-mounted EV charger, typically with one or two outlets. |
| Ladeinfrastruktur | Charging infrastructure | Collective term for the entire infrastructure for charging EVs. |
| Ladeoperatør | Charge point operator | A company that establishes, installs, services, and operates charging stations; may include fuel stations that add chargers (typically fast chargers). |
| Ladeplads | Charging space | The area allocated for an EV to charge; includes a charging point. |
| Ladepunkt | Charging point | Where an EV can charge — in practice, the charging plug/socket. |
| Lader | Charger | Collective term for various charging units (charging box, charging station, etc.); also called "ladefacilitet" in some places. |
| Ladestander | Charging station | A stand that delivers power to EVs; may have multiple charging points/plugs. |
| Ladepark | Charging park | Geographically defined area with many charging stations, typically fast chargers, often at motorways or major roads. |
| Ladeøer | Charging islands | Multiple normal chargers grouped in clusters/"islands" so EV drivers can easily find an available charger. |
| Lastbalancering | Load balancing / load sharing / load management | Technical solution ensuring chargers on a parking lot share available power between them, so total charging load never exceeds a predefined ceiling — slows other EVs' charging rather than overloading the local fuse/breaker. |
| Lynlader | Rapid/ultra-fast charger | Also called DC charger. High-power charger, charges at **150 kW or more**. DC; conversion happens in the charger, not the EV's battery. The most expensive charger type, offering the highest charging speed; usually requires expansion of existing electrical installation/capacity. |
| Normallader | Normal charger / destination charger / AC charger | Low-power charger delivering AC power between **3.7-22 kW**. The most common charger type, typically cheapest to install; used for home charging, businesses, and retail. Can often be installed with very few electrical additions to the existing installation. |
| Udtag | Outlet | The plug/socket on a charging station that the car connects to. |
| V2G / Vehicle to Grid | Vehicle to Grid | A technology/method that, via bidirectional charging, lets an EV function as a grid battery, able to (for payment) supply power back to the grid during peak-load situations, reducing grid-overload risk. |

**Note on charger power terminology:** this document defines "Hurtiglader" (fast charger) as 50-100 kW and "Lynlader" (rapid charger) as ≥150 kW — a stricter/different threshold than the companion "Guide til Flådeejere" documents, which used "hurtigladning" more loosely for higher-power AC charging (7-43 kW or 20-25 kW depending on edition) and "lynladning"/DC for 50-350 kW. **This terminology inconsistency across the project's source documents is noted explicitly here, not reconciled** — readers should check which document's definition is in play when comparing charging-power figures across guides.

## Legal Requirements — Ladestanderbekendtgørelsen (Charging Station Executive Order)

- **Ladestanderbekendtgørelsen** entered into force **10 March 2020**. It implements parts of **EU directives on the energy performance of buildings** (bygningsdirektivet), issued under authority of the **Byggeloven** (Danish Building Act).
- Applies to building owners: businesses, housing organizations (boligorganisationer), municipalities, regions, and others owning buildings.
- **SMV'er (Små og Mellemstore Virksomheder / SMEs)** — defined per source footnote as "virksomheder med mindre end 250 medarbejdere og en årlig omsætning på under 50 mio. EUR eller en samlet årlig balance på under 43 mio. EUR" (companies with fewer than 250 employees and annual revenue under EUR 50 million, or total annual balance sheet under EUR 43 million) — are, at time of writing, **exempted from the requirement for existing buildings**.

### Key requirements (minimum requirements):
- **Existing non-residential buildings with more than 20 parking spaces:** must have **at least 1 charging station installed by 1 January 2025** (SMEs exempted).
- **Renovation ("større ombygninger" / major renovations) of buildings with more than 10 parking spaces:** a charging station must be installed **if** the cost of doing so is **under 7% of the total renovation cost**. "Larger renovation" is defined by ALL of: (a) more than 10 parking spaces associated with the building post-renovation; (b) construction work is occurring on the building; (c) the parking facility or the building's electrical infrastructure is being rebuilt; (d) the cost of establishing/preparing for charging stations is under 7% of total renovation costs.
- **New construction / expansion / major renovation:** the charging-station requirement is part of the building permit (byggetilladelse).
- No requirement that charging stations be publicly accessible and/or operated by a charge operator.
- The charging station must be located on parking spaces associated with the building — not necessarily a single parking space or on the same land parcel (matrikel) as the building.
- **Recommendation beyond the legal minimum:** the guide recommends treating the Bekendtgørelse as a floor, not a target — suggests businesses prepare for **at least 20% of parking spaces** to have charging capability, regardless of building type/size, to avoid falling behind actual demand.
- A separate **vejledning (guidance document)** to the Bekendtgørelse exists, covering rules for "mixed users" parking areas, etc.
- At time of writing, a proposed revision to the **European Parliament and Council directive on the energy performance of buildings (recast)** had been tabled, which may lead to a revised/tightened Ladestanderbekendtgørelse.
- **Legal sources cited (footnotes):**
  - Ladestanderbekendtgørelsen: https://www.retsinformation.dk/eli/lta/2020/181
  - EU building directive: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32010L0031
  - SME definition source: "Vejledning til ladestanderbekendtgørelsen," 1 January 2021
  - Vejledning (guidance) to the Bekendtgørelse: https://bygningsreglementet.dk/Vejledninger/Andre_vejledninger/Vejledning/Vejledning-om-laderstander
  - Proposed EU directive recast: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=EP%3AP9_TA%282023%290068

## Needs Assessment Methodology (Behovsafdækning)

The guide frames needs assessment around four user groups of a business's parking facilities:

### 1. Own fleet vehicles (Virksomhedens egne biler)
- If vehicles are out driving most of the day, they need only overnight-to-morning charging, but require a **dedicated charging station per vehicle**.
- If vehicles are both out and parked at the business for extended periods during the day, daytime charging may suffice.
- Reference: for fleet-owner-specific considerations, the guide cross-references the **"Anskaffelse af elbiler & ladestandere"** guide on Elbilviden.dk (i.e., the "Guide til Flådeejere" documents processed elsewhere in this knowledge base) — confirmed via footnote URL: `https://elbilviden.dk/wp-content/uploads/2020/09/Guide-Til-flaadeejere-nyeste.pdf`.

### 2. Employees (Medarbejdere)
- Rule of thumb: an EV driver needs to charge **approximately once a week**, meaning theoretically **up to 5 employees with EVs could share one charging space** if all need workplace charging.
- Plug-in hybrids are different: their battery can typically only accept a limited charge rate (**typically 3.7 kW AC**) and provides roughly **50 km of electric range**, so they need charging daily or near-daily depending on commute distance — plug-in hybrids occupy disproportionate capacity in shared charging infrastructure relative to their battery size.
- Actual need depends primarily on: number of employees who have/plan to acquire an EV; employees who genuinely need/want workplace charging; plug-in-hybrid employees wanting workplace charging.
- Particularly relevant in dense urban areas (poor home-charging access) and for employees with long commutes.
- Recommendation: actively involve employees in the decision by surveying their EV purchase plans and workplace charging needs.

### 3. Guests (Gæster)
- Guests typically have shorter visits; **normal charging at 11-22 kW** is typically sufficient, providing **55-110 km of range per hour** of visit.
- **Rule of thumb: at least 20% of a business's guests will eventually need charging.**

### 4. Other users of the business's parking facilities (Andre brugere)
- The public can be given access during periods the infrastructure is otherwise idle (e.g., at night).
- Clear parking rules are important to prevent the public from occupying spaces needed by the business's own users.
- Relevance depends on business location (especially dense urban areas) or desire to build goodwill with the local community.
- Public-facing chargers should be made discoverable (typically via an app) so EV drivers can see availability — becomes visible on the relevant charge/platform operator's online charging map once enabled, or can be manually registered on an open-source charging map.

### Needs-assessment recommendation table (per user group)

| User group | Recommendation |
|---|---|
| Own fleet | Up to 1 charging station per vehicle |
| Employees (private or company car) | At least 20% of shared parking spaces for employees and guests |
| Guests | Depends on guest volume — shared with employees, or an additional 20% of shared parking spaces for employees and guests |
| Other users of the business's parking facilities | If chargers are made publicly accessible: access intended for employees/guests, possibly restricted to outside business hours only |

### Key questions to determine total demand (from source):
- How many users need charging?
- How often does each user need to charge?
- How long do users typically stay at the business?
- How long do the EVs need to charge?
- How much power is needed?

## Checklist (Tjekliste) — Full List

- Who uses the parking lot, and how many need/should be offered charging?
- What charging pattern do users have? Do they typically park for many hours spread across the day, or do many users arrive during daytime hours for only 1-2 hours?
- Is there a need for one or more fast chargers (20-50 kW)?
- How many charging stations are needed now, and how many parking spaces should eventually be electrified?
- What power access exists for installation at the parking lot, i.e., power groups and amperage at the main/sub distribution board? (If more Amperes must be purchased, costs rise quickly — consider load balancing.)
- How should charging points be placed — freestanding, wall-mounted? Is asphalt work involved?
- Should the chargers support smart charging, to relieve the grid and optimize use of renewable energy, etc.?
- Should the business own or rent the charging stations? Should the business handle access control and billing with users, or leave it to an operator?
- Should there be chargers dedicated to own vehicles, employees, guests? And what should pricing be for each group?
- Can guests charge outside the business's opening hours?

## Payment Structures (Betalingsstruktur)

- Charge operators use varying price structures — some differentiate via app, others via charge tags (ladebrikker); tag users vs. spontaneous ("ad hoc") sessions may be priced differently; prices can be adjusted based on daily or average prices.
- Employees can be given free or reduced-price charging, administered via the employee's app or charge tag.

### Tax treatment of employee charging
- If a business offers **free charging to employees' private cars**, this is treated by **Skat** (the Danish Tax Agency) as a taxable employee benefit ("medarbejdergode"), requiring the business to track individual employee consumption and report it to Skat.
- This does **not** apply to company cars on white or yellow plates ("hvide eller gule plader").
- Employees with a company car who get an employer-paid home charging solution installed are **not** taxed on the cost of that solution or its installation. This originally applied to company cars on yellow plates, and **from 1 July 2021** was extended to company cars on white plates too.
- **Footnoted sources:**
  - Skat guidance: https://info.skat.dk/data.aspx?oid=2364648
  - Elbilviden.dk on company-car EV taxation: https://elbilviden.dk/erhverv/saet-stroem-til-jeres-bilflaade/elbil-som-firmabil/

### Guest charging tax note
- Free charging for guests does **not** carry the same Skat tax complications that apply to employees.

### VAT/duty refund (Refusion)
- A business can get a refund of the electricity duty ("elafgift") if it is the business's own electricity being used for the charging stations. If power is drawn from a roadside cabinet ("elskab ved vejen"), refund cannot be obtained.

## Choosing a Solution (Valg af løsning)

### Charger types

**Normallader (Normal charger)** — most businesses install these due to cost-effectiveness. Uses the European 3-phase Type 2 plug, often handling **22 kW (32A/3 phases)**, though not all EVs can use the full rate. At full utilization, 22 kW adds up to **110 km of range per hour**; 11 kW adds about half that (**55 km/hour**).

- Recommended physical formats: freestanding charging station with two outlets; charging box with one or two outlets; or two charging boxes on a shared post (see source Figure 2, credited to DTU Wind).
- Freestanding/post-mounted charging points typically supplied via ducting/conduit (tomrør); wall-mounted typically via cable tray (kabelbakke).
- **Recommendation:** install chargers dimensioned for 22 kW, since all car models can then use their maximum possible charge rate, and the price difference between 11 kW and 22 kW installations is relatively modest — conditional on the business also considering load balancing so that supporting 22 kW doesn't simultaneously increase the overall power-capacity requirement (Ampere purchase) at the parking lot. Some dual-outlet chargers/boxes can internally load-balance/share power (e.g., one EV gets 22 kW if charging alone, or two simultaneous EVs each get 11 kW).

**Hurtiglader og Lynlader (Fast and rapid chargers)**
- At larger parking areas (**more than 20 charging outlets**), consider adding a **50 kW fast charger**, though costs are higher (**up to 450,000-600,000 DKK**) and power requirements are greater (**up to 125 Amperes**). In some locations a rapid charger (lynlader) may be the right choice instead.
- **Hurtigladere (fast chargers)** charge EVs at typically **50 kW**; can charge an EV from **10% to 80% in 30-60 minutes**.
- **Lynladere (rapid chargers)** charge EVs at **100 kW or more**; can charge an EV from **10% to 80% in 20-30 minutes**.
- Charging speed for all three charger types depends on many additional factors — battery temperature (hot/cold) and current state of charge significantly affect how many kW the EV actually accepts.

### Load balancing (Lastbalancering)
- Economically sensible, especially for businesses with multiple chargers; ensures optimal power distribution, prevents overload, and can reduce the need for costly electrical upgrades, since EVs often charge on a staggered schedule and don't always require maximum power simultaneously.
- **Static load balancing (Statisk lastbalancering):** predetermined, fixed power split among connected vehicles regardless of individual need. E.g., 22 kW total capacity split evenly between two connected cars = 11 kW each, regardless of actual need.
- **Dynamic load balancing (Dynamisk lastbalancering):** adjusts power distribution based on the actual/current needs of connected EVs, allocating power per vehicle's specific requirement for more efficient use of available capacity.
- **Worked example (source Figure 4, credited to Rambøll):** Five 11 kW charging points (16A per charger) used simultaneously would nominally require an 80A supply. But with load balancing, a business can get by with a **32A (22 kW)** supply instead. Example schedule: at 10:00, two cars charge at full 11 kW each; at 12:00 a third car arrives and load balancing reduces each car to 7.3 kW; at 14:00 two more cars start charging at full power because the original three have finished charging by then.

### Smart charging (Smartladning)
- Allows EV charging to be shifted to times when electricity is cheapest and/or greenest — if an EV is parked for a full workday, consumption can often be shifted without affecting the driver's need to drive. Businesses wanting this functionality should ensure it is offered by the specific charging station chosen.
- Load balancing is described as the first/primary function businesses should consider; smart charging is described as an important way to future-proof the charging infrastructure.
- **Cross-reference:** the guide explicitly refers readers to the report **"Smartladning og V2X for virksomheder"** on Elbilviden.dk — i.e., the companion document `Rapport om Smartladning og V2X for virksomheder.pdf` processed elsewhere in this knowledge base.

## Rollout Process (Udrulning) — 4 Steps

1. **Plan and prepare charging spaces:** Investigate how much power access exists at the parking lot and decide how power will be routed. Install ducting/conduit or cable trays for all future charging spaces as early as possible — this strategy aligns with the Ladestanderbekendtgørelse's requirements.
2. **Upgrade power supply (if necessary):** Additional power capacity for the parking area may be needed; can be a major cost due to potential excavation and connection fees. Consider whether load balancing can reduce/postpone this need.
3. **Run power cable:** Route cables from the distribution board to the parking area via the preparations made in step 1.
4. **Install charging point:** Charging points are set up, connected, and commissioned by an authorized electrician.

**Principle:** early preparation (step 1) should be tackled immediately by the business; steps 2-4 can be executed/repeated as demand grows — future expansion becomes cheaper and faster because ducting/cable trays are already in place per an established plan.

### Technical rollout recommendations
- **Ensure a good earth/ground connection:** transition resistance to earth must be **under 50 ohm** — some charging stations and EVs require this to function.
- **Don't skimp on cable thickness:** the marginal cost of a thicker power cable (higher cable cross-section) is low relative to the overall installation cost, and future-proofs the infrastructure.
- **Charging simultaneity (Ladesamtidighed):** typically, at most **30-40%** of a parking area's EVs will charge at the same time — though this depends heavily on the number of EVs and the type of EV users. If in doubt, use load balancing.

## Cost Structure and Pricing (Den samlede løsning og pris)

- Total cost = (1) the charging solution itself (station/box) plus installation, and (2) the underlying site preparation (klargøring).
- Site-preparation costs vary significantly based on charging-station placement and available capacity at the nearest distribution board; **total price per 22 kW charging point can range from 20,000-50,000 DKK** depending on these factors.
- Framing: businesses offering charging near the actual electricity price can play a key role in making the green transition accessible to people without home-charging options (space constraints, housing type, etc.), who would otherwise rely on public chargers with markedly higher prices than the actual electricity cost.
- Public-charger attractiveness for a charge operator (relevant if a business wants an operator to fund/install for free or even pay the business) depends on: traffic volume, accessibility/visibility from the road, whether the location is where people actually need to charge (e.g., areas without home charging, shopping areas, motorway exits). Common requirement: chargers must be publicly accessible 100% of the time for such deals.

### Cost estimate table — fixed and variable costs per charging point (2023 prices, excl. VAT)

| Cost type | Price (excl. VAT) |
|---|---|
| **Fixed costs per charging point** | |
| Charging point 22 kW (3-phase / 32A) | 6,000 – 12,000 DKK |
| Establishment and installation | 5,000 – 6,000 DKK |
| **Variable costs — site preparation** | |
| Power-capacity upgrade / Ampere purchase | 1,200 DKK/Ampere |
| Cabling to charging station incl. excavation | 500 – 1,500 DKK/meter |

*Source: Rambøll's experience-based pricing ("Rambølls erfaringspriser"), as stated in the source table caption (Tabel 1).*

- Additional costs beyond the above: operations and any fixed payments to an operator (monitoring, servicing, and possibly charger rental).

## Getting Quotes (Tilbudsindhentning)

- Charging-infrastructure providers often offer impartial meetings for quote submission. Small numbers of chargers typically get standard quotes; larger projects involve personal consultation for detailed quotes.
- For many businesses, a few quotes suffice for a good price and insight. For larger multi-location projects, a formal tender (udbud) can be advantageous — specifies requirements and makes quotes comparable — but requires time, competence, and can be costly. Consulting a tender-process expert is recommended, especially for businesses without experience. Tenders are ideal for businesses that don't want to handle day-to-day charger operations.
- **Caveat:** the specificity of tender requirements affects price — more specific requirements, higher price.

## Implementation and Operations (Gennemførsel og drift)

- **Electrician requirements:** all electrical work for charging boxes/stations is subject to authorization requirements (autorisationspligtigt). An installer experienced with charging infrastructure is advantageous, as EV installation sizing differs from standard electrical installation sizing. Transition resistance to earth must be under 50 ohm to ensure all EV types can charge.
- Even when preparing for 3-phase charging, some EVs only charge on a single phase — recommendation to "rotate" phases between charging outlets so load is evenly distributed across all three phases (some smart charging points handle this automatically and don't need rotation).
- If recommended preparations have been made, adding new charging points is relatively quick and simple.
- **Operations (Drift):** maintenance needs are generally low. If a charge operator installs the business's chargers, this responsibility typically falls to the operator. If the business has handled acquisition itself, it needs a fault-handling procedure — ideally via agreement/contract with an electrician — with fast response, ideally a phone number/email posted directly at the chargers for fault reporting.

## Case Study 1: Dansk Miljø- og Energistyring A/S (DME) — "DME has control itself"

- **Company profile:** DME builds automation solutions for the utility sector (water/wastewater, district heating, biogas, industry). Specialists cover electrical design through cabinet-building, hardware/software programming, user interface, server/network, and IT security. Celebrated its **35th anniversary in 2023**; grown steadily especially over the last 5-7 years; **70 employees** as of mid-2023.
- **Context:** In connection with new building/extension work in **2020/21**, DME began work on charging-station installation. A few guests/customers had already asked about charging while visiting. DME wants a green profile aligned with its business field. DME did not yet have EVs in its own fleet at time of writing but was investigating the market for a good fit.
- **Lead:** Co-owner **Kim Villadsen** handled researching options and implementation, despite having no prior market knowledge (professional or private) — though DME's staff being mostly electricians/electrical installers gave an inherent advantage for the electrical aspects.
- Kim had heard vaguely about requirements for charging-station installation tied to construction but wasn't aware of specifics, and wasn't presented with specific requirements during the building case — though installation/preparation for future charging stations was part of the building-permit materials regardless.
- **Preparation for future stations:** DME laid empty ducting (tomrør) for roughly half of parking spaces during construction/renovation of the parking lot; secured space in the main distribution board for future charging-station circuits; secured extra Ampere capacity as part of the new construction.
- **Solution chosen:** Kim personally purchased the charging stations, had them installed by a local electrician, and bought a subscription with a platform operator to handle communication to/between individual stations — after contacting a couple of local electrician firms known to have installed chargers before, plus one of DME's own product suppliers. He also investigated renting from a charge operator but felt it didn't match DME's needs.
- **Key selection criteria:** robust, reliable stations with **4G connectivity** (so they wouldn't need to be on the company Wi-Fi, for IT security reasons); ability to charge at full capacity without tripping breakers — hence chose a solution offering **load management/load balancing**; billing for charging needed to happen without involving DME's bookkeeper.
- **Payment structure:** employees can sign up for the company's charging solution and charge at a fixed price set slightly above what the business pays per kWh; guests charge for free via a charge tag issued at reception.
- **Ongoing plans:** considering making one street-facing charger publicly accessible outside working hours (evenings/nights/weekends) to serve nearby townhouse residents and their visitors — not yet implemented, on the roadmap.
- **Status (mid-2023):** four charging stations installed; one dedicated to guests. Four more ordered, expected installed by end of 2023; new stations will have a fixed/attached cable (earlier stations require the EV driver to bring their own cable).
- **Key lessons/quotes from the process:**
  - "Ladeoperatørmarkedet er ekstremt svært at finde rundt i" (the charge-operator market is extremely hard to navigate) — nearly impossible to see who's in the market and what they offer; most can't be called, only messaged (via a chatbot).
  - The charging-station (hardware) market is somewhat more accessible — easy to find many station types, but harder to determine which type is best / future-proof for the business's needs.

## Case Study 2: Rambøll — "Rambøll has set up charging infrastructure at rented locations"

- **Company profile:** Rambøll is a global engineering/design/consulting company, addressing challenges in urbanization and climate change with a sustainability focus. **12 offices in Denmark**, present in **35 countries**, approximately **4,100 employees in Denmark**.
- **Challenge:** installing charging stations across all 12 Danish locations was demanding, especially regarding preparation and cabling — complicated by the fact that Rambøll **rents** all these buildings rather than owning them. However, landlords were largely understanding and cooperative; early dialogue and planning overcame most challenges, and extra capacity was secured in electrical installations for future expansion.
- **Outsourcing decision:** since Rambøll doesn't normally handle day-to-day operations/facility management in-house (all facility management is handled by subcontractors), it chose to outsource the entire charging-station process — from installation to daily operations — to operators, via a rental/lease agreement rather than ownership.
- **Access and facilities:** charging infrastructure now exists at all Danish offices. **Headquarters in Copenhagen: 18 publicly accessible charging stations.** **Aarhus office: 8 stations.** Employees with company cars get a dedicated charge tag; Rambøll also covers the cost of installing a home charging box for employees with company cars. Office chargers are accessible to all employees. Rambøll also has chargers dedicated to its internal pool cars ("puljebiler"), locked to pool-car-only use, with fines possible for other cars parking there.
- **Technology considerations:** no specific advanced technology chosen yet, but growing internal interest in intelligent charging (e.g., charging when electricity is cheapest) and V2X to help stabilize the grid — not yet implemented.
- **Economic framing:** cost was not the primary driver — Rambøll had already committed to switching to green company cars, making charging infrastructure necessary regardless; also wanted to ensure all employees (company car or not) could charge.
- **Key lessons:**
  - Even as a tenant, it's usually possible to get charging stations installed, given good communication with the landlord.
  - Be clear on whether the business wants to operate the infrastructure itself — otherwise it's clearly better to let an operator handle all practicalities.

## Case Study 3: Grundfos — "Two different charging solutions were right for Grundfos"

- **Company profile:** Grundfos is one of the world's largest pump manufacturers (drinking water, wastewater, service water pumps), for private and business customers. Sustainability-focused. Celebrated **75th anniversary in 2020**. **5 departments in Denmark**, offices in **more than 55 countries**. Approximately **4,000 employees in Denmark**, over **19,000 worldwide**.
- **Context:** Grundfos began developing an EV fleet-transition strategy in **2018**, driven by a combination of employee demand and Grundfos's general desire for a green profile. **Søren Høgh** (Facility Lead Coordinator El Project) led implementation from the start, alongside **Peter Rosen Christensen** (Facility Manager, Danish buildings); Søren had no prior background in the area.
- First step: a global mapping of what fleet-wide EV adoption would require of Grundfos globally in terms of charging infrastructure. Quote: *"Laderen skal jo gerne være der, den dag elbilen kommer"* (The charger should ideally be there the day the EV arrives) — Søren Høgh.
- **Strategy target:** **all Grundfos vehicles to be 100% electric by 2025.** Initially, trucks were excluded from the strategy, but **by 2023** Grundfos had begun exploring options for truck electrification too.
- **Two separate charging models chosen** — one for employee/guest chargers, one for fleet-vehicle chargers — driven by differences in payment/billing/tax handling and by differences in power supply arrangements.

### Fleet-vehicle chargers
- All located behind the fencing surrounding the company premises — **not publicly accessible**.
- Chosen from the same supplier used for many of Grundfos's other facility/production equipment (enabling integration with an existing monitoring platform).
- Power supply directly connected to the company's own electricity — a tax-advantageous arrangement, since these are the company's own operating vehicles.

### Employee/guest chargers
- Located mostly on parking areas **outside** the company fencing — publicly accessible 24/7.
- Grundfos uses a **charge operator** to run these stations, keeping billing, operations, and maintenance off Grundfos's own workload, while retaining a data-sharing agreement with the operator to monitor usage/capacity needs.
- Power comes from the **public grid**; required **3 new transformer stations** at Grundfos's headquarters in **Bjerringbro**.
- Company agreement with the charge operator gives all employees a discount on charging; employees with company cars get a charge tag for that operator alongside the vehicle.
- **Parking-lot setup:** two chargers serve four parking spaces (two for charging, two as waiting/queue positions), with a **4-hour charging time restriction**. EV owners don't need to move their car — they can simply disconnect, allowing the next EV owner to start charging. Grundfos observes that the time restriction isn't always followed, but also observes that chargers are consistently available. Quote: *"Faktisk kan vi også se at færre lader end de gjorde i starten. Ladebehovet er ikke steget, selvom der er kommet flere elbiler"* (We can actually see that fewer charge now than at the start — charging demand hasn't grown even though there are more EVs) — Peter Rosen Christensen.
- Parking spaces marked on the asphalt for visibility. Standard setup: **eight 22 kW charging stations** per parking area, using load balancing with **63A shared across 8 chargers** (full simultaneous capacity for all chargers would be far too costly). No charging-capacity issues so far.

### Future plans
- Strategy originally excluded fast/rapid chargers, but Grundfos has received inquiries about this; now in early dialogue with its charge operator about adding a fast charger at one suitable parking location, to serve employees, guests, and the public with faster charging.
- At some rented Danish facilities, Grundfos has paid the charge operator to install chargers on the landlord's land; at two current leased sites, Grundfos is exploring an alternative arrangement where the landlord installs the chargers and Grundfos pays slightly higher rent instead.

### Key lessons
- Avoid having employee/guest chargers draw on company electricity — creates extra bookkeeping work due to tax rules (see Payment Structure / Skat section above).
- It would have been beneficial if the chosen charge operator allowed roaming for other charge-operator customers — some employees with a different operator's subscription were frustrated they couldn't use it at Grundfos's chargers.

## Named Bodies, Standards, Legislation

- **Region Hovedstaden / Copenhagen Electric** — publisher.
- **Rambøll** — author/consultancy.
- **DTU Wind** (Technical University of Denmark, Wind Energy department) — source of reused figures/content, credited to Peter Bach Andersen.
- **Ladestanderbekendtgørelsen** — Danish Charging Station Executive Order (in force 10 March 2020).
- **Byggeloven** — Danish Building Act.
- **Bygningsdirektivet** — EU Energy Performance of Buildings Directive.
- **Skat** — Danish Tax Agency (employee-benefit taxation rules for charging).
- **Elbilviden.dk** — companion knowledge portal, cross-referenced for the fleet-owner guide and the Smartladning/V2X report.
- Case company bodies: **Dansk Miljø- og Energistyring A/S (DME)**, **Rambøll**, **Grundfos** — noted here as companies with embedded case examples in this document; not separately covered by a dedicated case-study file among the other project documents in this batch (though "Casehistorier_Fagfolk_templafy.pdf" and other case-study PDFs exist elsewhere in the project and may cover some of these companies — not verified in this task).

## Notes on Data Completeness

- The document is marked "Confidential" throughout in the extracted text; this classification is reproduced factually here as it appears in the source header/footer on every page.
- Figures 1, 2, 3, 4, 5, 6, and several case-study photos (Figures 7-13) are referenced in the text (mostly credited to Rambøll or DTU Wind) but could not be transcribed with their exact visual/graphic content from the extracted text — only the surrounding explanatory text and any embedded example numbers are captured above.
- No specific CO2/emissions methodology or figures are given in this document — unlike some other guides in this batch, this document is infrastructure/process-focused rather than climate-impact-focused.
