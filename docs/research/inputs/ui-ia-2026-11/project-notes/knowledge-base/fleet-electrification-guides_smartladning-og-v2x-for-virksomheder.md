# Smart Charging and V2X for Businesses

**Source file:** `Rapport om Smartladning og V2X for virksomheder.pdf`
**Category:** Fleet electrification guide / policy report
**Original language:** Danish (translated to English below; proper nouns kept in Danish)
**One-line summary:** An autumn-2023 Region Hovedstaden / Copenhagen Electric report (by Rambøll) mapping the potential of smart charging and V2X (Vehicle-to-Everything) for businesses — covering definitions, benefits/drawbacks, market and technology readiness (with a detailed vehicle/charger V2X-compatibility table), EU/Danish regulation, communication standards, and three real-world case studies (PostNord/Monta, ViggoEnergy/Spirii, Utrecht/We Drive Solar).

## Publisher, Year, Audience

- **Publisher:** Region Hovedstaden, **Center for Regional Udvikling**, branded as "Københavns Electric" in the imprint (elsewhere in the project referred to as Copenhagen Electric). Contact: Kongens Vænge 2, 3400 Hillerød; Tel +45 38 66 55 05; Email cph-electric@regionh.dk; Web www.regionh.dk.
- **Authors:** **Lisa Calearo, Marte Larsen, Maja Sig Vestergaard**, from **Rambøll**.
- **Reviewers/contributors thanked:** Kristian Sevdari (DTU), Matthijs Kok (Gemeente Utrecht) and Robin Berg (We Drive Solar), Rune Schostag Nielsen and Alex Iriondo (Monta), Torben Fog (Spirii).
- **Publication timeframe:** Market status described as of **autumn 2023** ("efteråret 2023").
- **Primary audience:** Businesses interested in how smart charging and V2X can accelerate their green transition and create economic/environmental added value; also relevant to companies wanting to strengthen their sustainability (CSR/ESG) profile.
- **Scope note (explicit in source):** the report primarily discusses EVs as passenger cars, but notes the potential for smart charging/V2X applies to a broader range of electric vehicle types too — "and likely to greater advantage" — including **trucks, buses, and others** (directly relevant to this project's HDEV focus, though the report itself does not develop the HDEV-specific case in detail).

## Terminology / Glossary (Ordforklaring)

| Term | English gloss | Definition (from source) |
|---|---|---|
| AC-lader | AC charger | Also called an alternating-current charger; the most common charger type, typically smaller/cheaper than a DC charger, but lower power (**3.7-22 kW**). |
| DC-lader | DC charger | Also called a direct-current charger; typically larger/more expensive than an AC charger, but offers higher charging speed (**50-400 kW**). |
| Ladeoperatør | Charge operator | A company responsible for operating and administering charging infrastructure. |
| Ladestik | Charging plug | An electrical connection used to charge EV batteries by connecting to charging infrastructure/a charger unit. Common types include **Type 2 (Mennekes), CCS (Combo), and CHAdeMO**. |
| Lastbalancering | Load balancing | English: "load sharing," "load balancing," or "load management." A functionality in chargers to share available power among themselves — if local capacity is fully used and a new EV connects, the system slows other EVs' charging to avoid overloading the local fuse. |
| Ladeleverandør | Charging supplier | The party supplying charging stations/boxes to the business/consumer; may also be a charge operator. |
| Ladestander | Charging station | In this report, a charging facility for an EV, which may be ground-mounted (freestanding) or wall-mounted (e.g., in a parking garage). |
| Smartladning | Smart charging | Also "smart charging," intelligent charging stations, etc. Refers to intelligent, optimized management of the EV charging process — shifting charging to times when power is greenest, cheapest, or when the grid is least loaded. Sometimes called **Vehicle-to-Grid, V1G** (i.e., one-directional smart charging, as distinct from V2G). |
| Vehicle-to-Building (V2B) | Vehicle to Building | Technology letting EVs supply power to buildings, typically during peak load or emergencies, effectively making the EV a mobile energy source for the building. A specific V2X technology. |
| Vehicle-to-Grid (V2G) | Vehicle to Grid | Technology where EVs connect to and exchange energy with the grid, improving efficiency and stability. Enables bidirectional charging — power can flow both ways between EV and grid. |
| Vehicle-to-Everything (V2X) | Vehicle to Everything | Technology where a vehicle connects to and exchanges energy or data with another device/infrastructure. Includes various specific combinations, including V2B and V2G. |
| Renewable Energy Source (RES) | Renewable energy source | Renewable energy sources such as solar panels and wind turbines. |
| State-of-Charge (SoC) | State of charge | The current amount of electrical energy remaining in a rechargeable battery/battery pack, expressed as a percentage of its full capacity. |

## What Is Smart Charging and V2X?

### One-way vs. two-way charging
- **Envejsopladning (one-way charging):** the traditional/most common form — energy flows from the grid to the EV, solely to store power in the EV battery for driving.
- **Tovejsopladning (two-way/bidirectional charging):** allows power to flow both ways between the EV and another device — the EV can send energy back to the grid, a building, or a consumer device (a lamp, computer, etc.). Requires special charging equipment, a bidirectional-capable EV, and a system to safely/efficiently manage the power flow.
- (Source Figure 1 illustrates one-way [top] vs. two-way [bottom] charging flow — described qualitatively here as exact diagram values are not applicable/numeric.)

### Smartladning (Smart Charging) — also called V1G
- Refers to the intelligent, optimized management of the EV charging process — using technology and data to control when/how an EV charges to maximize efficiency and grid stability while minimizing charging costs.
- Smart-charging strategies consider: electricity demand, price per kWh, availability of renewable energy, CO2 production, and user needs, to determine the best time/speed to charge.
- Focuses on optimizing the charging process while the EV remains connected to the charger (as opposed to controlling discharge). The EV owner typically gets an app to set personal preferences (e.g., when the EV should be fully charged).
- (Source Figure 2 illustrates the information flow — electricity price, CO2, renewable production, grid/user input — and the power flow from grid → charger → EV; "VE" in the figure stands for **Vedvarende Energi**, Renewable Energy. Figure is credited as "Inspired by figure in" a cited academic source: Sevdari, K., et al. (2021). *Autonomously Distributed Control of Electric Vehicle Chargers for Grid Services*. In Proceedings of ISGT Europe 2021 IEEE. https://doi.org/10.1109/ISGTEurope52324.2021.9640132.)

### V2X (Vehicle-to-Everything)
- A broad term covering technology enabling EVs to communicate with other devices (other EVs, infrastructure, pedestrians, network services) to improve traffic safety, mobility, and transport-system efficiency.
- In the grid context, V2X specifically covers an EV's ability to supply power to various electricity consumers — the "V" is the EV, and "2" indicates power can flow both ways (grid→EV and EV→X), via communication between the EV and an external device/system (grid, homes, buildings, loads) representing the "X."

#### V2B — Vehicle to Building
- The EV sends power to a building (a home, institution, or business). Idea: use the car battery to store energy for later building use — both for backup capacity during outages and to relieve the grid during peak-load periods.
- Algorithms determine power-flow direction — when to buy grid power to charge the car battery, vs. when to use car-battery power for building consumption — accounting for both the EV driver's needs (e.g., when the car must be charged) and the building's expected consumption patterns.
- Requires both the charger and the EV to have bidirectional capability. (See Market Readiness section below for which chargers/EVs currently support this.)
- (Source Figure 3 illustrates V2B information/power flow.)

#### V2G — Vehicle to Grid
- The EV can also send power from its battery back to the grid — helping balance the grid during peak load and providing backup power during outages. Requires bidirectional charging capability in both charger and EV.
- (Source Figure 4 illustrates V2G information/power flow.)

##### V2G's grid potential (explained in depth)
- Growing renewable-energy sources and growing numbers of less-predictable EV loads have increased supply/demand swings on the grid, making system operation more complex. Ensuring continued high supply security in the Danish grid requires load-distribution measures, which are typically expensive additional investments.
- If EV batteries are managed/integrated effectively into the energy system, their significant energy-storage capacity can increase system flexibility — turning EVs from part of the problem into part of the solution:
  - During peak-load periods (consumption exceeds production), EVs can act as supplementary energy sources by feeding power back to the grid.
  - EVs can help stabilize the grid via **frequency regulation** — production and consumption must stay balanced to avoid grid-component stress and potential outages; EVs can contribute by (1) feeding power back to the grid when consumption exceeds production, or (2) drawing/storing power from the grid when production exceeds consumption, for later use — helping keep grid frequency within acceptable parameters.
  - Using EVs for frequency regulation can limit the need for expensive grid expansions/upgrades. Even though grid companies (netselskaber) often default to the more conservative solution of grid upgrades, leveraging EV battery flexibility is a potential alternative that can limit investment in grid capacity expansion.

#### EVs vs. stationary battery storage systems
- Many of the same benefits as smart charging/V2X can be achieved by installing a stationary battery storage system, sized to match one or more EV batteries' capacity.
- Key difference: how/when they connect to the grid. A battery storage system is stationary, at a fixed location, with known energy capacity. An EV's primary function is transport, so its battery is normally prioritized to have charge for expected driving — meaning EVs can only offer smart-charging/V2X potential while parked and not actively needed for driving. **The longer an EV is parked, the greater its potential for smart-charging/V2X use.**
- Key advantage of EVs over dedicated stationary storage: the investment in the EV/battery is already made for transport purposes, so it can make a separate stationary battery investment unnecessary — increasing utilization of the existing battery asset.

## Benefits and Drawbacks

### From the driver's perspective

**Benefits:**
- **Cost savings:** taking advantage of lower electricity prices at certain times reduces overall EV charging costs and thus TCO.
- **Convenience:** smart charging includes user-friendly mobile apps for scheduling charging sessions, monitoring status, and receiving notifications.
- **Environmental benefits:** aligning charging with high renewable-energy production periods reduces the driver's CO2 footprint and supports a more sustainable grid.
- **Supply security:** smart charging/V2X helps relieve grid overload by evening out electricity demand across the day, leading to a more reliable, stable grid.
- **V2X-specific — Energy sharing:** V2X lets the driver share surplus energy stored in the EV battery with the grid or other devices, potentially generating income.
- **V2X-specific — Backup power:** during an outage, V2X-ready EVs can serve as backup power for buildings with other critical electricity-consuming devices — contributing to local energy security.
- **V2X-specific — Grid support:** V2X can contribute to a more stable, reliable grid.

**Drawbacks:**
- **Initial investment:** drivers must invest in a charger and EV with the necessary technology, more expensive than simpler non-smart, non-V2X-compatible versions.
- **Learning curve:** some drivers may find configuring/programming a smart charger challenging.
- **Infrastructure dependency:** how effectively a driver can use smart charging/V2X depends on whether the necessary supporting infrastructure (chargers with the right software/hardware to properly communicate with the grid) exists where they park.
- **Data protection:** drivers may be concerned about collection/use of their charging-related data — requires transparency about what data is collected, how it's used, and how it's secured.
- **V2X-specific — Technology:** few EVs on the market currently support bidirectional charging, limiting technology spread and driver choice; more V2X-compatible EVs are needed.
- **V2X-specific — Battery degradation:** V2X use increases battery utilization and could mean faster battery degradation (further detail in the Battery section below).

### From the business's perspective

**Benefits:**
- **Grid balancing:** smart charging/V2X helps distribute loads (e.g., from EVs) more evenly, reducing the need for expensive infrastructure upgrades.
- **Optimized energy consumption:** by charging when prices are low and avoiding unnecessary charging when prices are high, businesses can optimize energy consumption and reduce overall electricity costs.
- **Flexibility services revenue:** businesses can earn income by offering flexibility services — e.g., demand response, voltage regulation, and/or capacity management — where charging infrastructure plus EVs serve as grid assets.
- **Environmental sustainability:** implementing smart-charging/V2X-ready infrastructure demonstrates business responsibility in the green transition and sustainability, positively reflected in the company's CSR/ESG profile.
- **Market positioning:** investing in green energy solutions positions the business as a forward-looking industry leader, potentially attracting new partners and collaborations.
- **Supporting EV adoption:** offering practical, cost-effective charging solutions can make EV ownership more attractive to employees and guests choosing a vehicle.
- **V2X-specific — Backup power:** businesses can use their EV fleet as a backup power source during outages, keeping operations/machinery running without needing expensive backup generators.

**Drawbacks:**
- **Initial investment:** implementing smart-charging infrastructure can require significant upfront investment in hardware, software, and integration with the existing grid.
- **Complexity:** system administration can be complex, requiring specialized expertise in grid management, software development, and data analysis.
- **Data protection and security:** robust data-protection/cybersecurity measures are needed to protect user data and grid information from potential breaches.
- **V2X-specific — Expensive technology:** V2X technology involves more expensive hardware/software, a potentially significant initial investment, and greater technical complexity to administer/operate.
- **V2X-specific — Rules and standards:** businesses must navigate still-developing regulations, standards, and liability questions associated with V2X and grid interactions — though as the market matures, these solutions are expected to become more accessible and available as ready-made concepts.

## Charging Station Technical Requirements

- Two ways to charge EVs: with direct current (DC) or alternating current (AC). Batteries can only be charged with DC, while the grid only supplies AC — conversion happens in a converter, either in the charging station (for DC charging) or in the EV itself (for AC charging).
- AC charging is typically associated with **Type 2** plugs (used in Europe). For DC charging, **Combined Charging System (CCS)** is the standard plug, combining AC and DC charging in one connector, mainly used in Europe. **CHAdeMO** is another plug, designed for DC charging, mainly used in Japan.
- Both AC and DC charging can theoretically be used for smart charging and V2X, but **as of 2023, only CHAdeMO is compatible with V2G**. Vehicle and charger manufacturers are actively working to make cars and chargers V2X-compatible generally.

### Pricing — AC vs. DC chargers

**AC charger:**
- Purchase price varies between **1,500 and 10,000 DKK**, depending on charger power (kW), brand, smart features, metering, etc. (Sources cited: footnotes 2, 3 — Calearo, L., Sevdari, K., & Marinelli, M. (2021). *Status e-mobilitet DK*. Danmarks Tekniske Universitet; and "Bidirectional Chargers Explained - V2G Vs V2H Vs V2L.")
- Chargers priced below roughly **3,000 DKK** are easy to operate but offer little beyond basic charging — **not** smart-charging-capable.
- Higher-priced chargers offer greater functionality via dedicated apps — e.g., remote control, charging scheduling, and charging speed. Further functionality may require involving a charge operator or similar.

**DC charger:**
- Due to added complexity, DC charger prices are not expected to fall below **20,000 DKK**, even with mass production. Prices scale with charger power (kW), currently up to **400 kW**.
- Since smart charging/V2X makes most sense when the EV is parked for several hours, the charging power (kW) of bidirectional DC chargers is not expected to exceed that of AC chargers (i.e., around **22 kW**), despite DC chargers' much higher theoretical power ceiling.

## Battery Considerations

- The EV battery's main purpose is powering transport; using it for smart charging/V2X also affects battery performance (km driven per kWh).
- Performance (range, performance) relates to battery size (kWh), State-of-Charge (SoC), and degradation (how much of original performance remains).
- Larger battery size generally means longer range, reducing charging frequency and giving the driver more flexibility.
- **Range anxiety** is a common EV-driver concern, often leading drivers to recharge frequently and keep SoC close to 100% to ensure enough range for unplanned trips — but **high SoC levels over time can accelerate battery degradation**, reducing capacity/performance.
- Overall battery lifespan depends on: usage pattern (frequent driving vs. long parking vs. V2G use), time, temperature, and SoC. Even unused, batteries degrade depending partly on temperature and SoC level.
- Many EVs come with warranties covering a certain degradation level (often down to **70%** of original capacity), reducing the risk of battery replacement during the warranty period (**often 7-8 years**). After the warranty period, replacing a degraded battery can be a significant expense affecting total/long-term ownership costs.

### Effect of smart charging on battery life
- Smart charging changes charging power depending on how charging occurs; compared to non-smart charging, smart charging has a **positive impact on battery life**, since charging power (kW) is reduced during periods when electricity is expensive, the grid is overloaded, or energy is less green. This can reduce battery temperature rise and result in longer battery life, since SoC is kept at a lower level on average.
- Lower charging power (kW) means longer charging time, which may be inconvenient in some circumstances — but drivers can use the smart-charging app to balance battery-life considerations with ensuring the car is sufficiently charged before use.

### Effect of V2X on battery life
- V2X further utilizes the battery pack since it can both charge and discharge — meaning more wear and, in theory, faster degradation over time.
- However, various research findings suggest the extra degradation expected from V2G technology use appears to be **limited to marginal percentage increases** (cited source, footnote 4: Calearo, L. (2022). *Grid integration of electric vehicles: battery degradation and user needs*. DTU Wind and Energy Systems. https://doi.org/10.11581/DTU.00000238). The factors contributing most to battery degradation are **time, battery temperature, and SoC** — which occur regardless of how else the battery is used.

## Market Readiness — Smart Charging

- Smart charging is already a well-integrated, widely used market functionality across both chargers and EVs. Many chargers have built-in smart functions; others require third-party involvement (e.g., charge operators).
- Smart charging adjusts charging power (kW) via equipment **outside** the car (the charger) — so in principle any EV can use smart charging if power stays within standard limits, though EVs respond differently to the same charging strategy (e.g., depending on whether they use single- or three-phase charging).
- Businesses with multiple EVs/chargers typically need third-party involvement to further manage/control charging.
- An overview of smart chargers on the market (autumn 2023) is referenced via footnoted sources: (5) Sevdari, K., Calearo, L., Andersen, P. B., & Marinelli, M. (2022). *Hjælpetjenester og elektriske køretøjer: oversigt fra ladeklynger og opladere teknologiske perspektiver*. Fornyelig og Bæredygtig Energi Anmeldelser, 167, [112666]; (6) "Hvad koster en ladestander til elbil," https://monta.com/dk/blog/hvad-koster-en-ladestander-til-elbil/.

### Choosing the best smart charger for a business — factors to consider
- **Ladeeffekt (Charging power):** how fast should vehicles be able to charge?
- **Stiktype (Plug type):** charger plugs and EVs must match; CHAdeMO is being phased out in Europe but currently offers the best V2G options.
- **Skalerbarhed (Scalability):** how many chargers/EVs are wanted long term? What should the hardware be capable of long-term?
- **Smarte funktioner (Smart features):** what control/management features are required now and in the future?
- **Dataindsamling (Data collection):** what data is needed from charging? How is it collected/delivered? Is data security adequately handled?
- **Brugeroplevelse (User experience):** how easy/intuitive is the app/functionality, considering the user group?

### Keywords to look for in a smart charger
- Intelligent and future-proof
- Remote control or remote management
- Charging speed or charging power
- Time-shifted/delayed/scheduled charging or charging plan
- Load balancing or its aliases: load sharing, load balancing, power sharing, etc.
- Energy efficiency, bidirectional charging, V2G/V2B, etc.

## Market Readiness — V2X

- For V2X, both the car and the charger must be able to send power both ways (charge and discharge). Most current EVs/chargers only support one-way power flow (grid→EV). Intensive work is underway to prepare electrical components for two-way power flow. V2X is still considered new/innovative, with varying market/regulatory maturity.

### Vehicle market readiness

- Compatibility for AC charging depends on the EV's inverter (hardware and software readiness for bidirectional flow). For DC charging, the inverter sits in the charger (outside the EV), but the EV still needs bidirectional-flow readiness mainly at the software/data-exchange level.
- **Currently, CHAdeMO (DC charging) is the only protocol where bidirectional charging functionality is already possible** — but only a few EVs on the market use the CHAdeMO plug. In the EU, most EVs/chargers use Type 2 or CCS plugs due to EU regulation, so most manufacturers selling into Europe are shifting from CHAdeMO to Type 2/CCS. More manufacturers are adding V2X functionality to their EVs in recent years, and most EVs are expected to have this in the future.

### Table 1 — EVs in Denmark, 2022, V2X information (most-imported car brands)

| Manufacturer | Model | V2X Readiness | Charging inlet AC/DC |
|---|---|---|---|
| Nissan | Leaf, MY22 | V2H, V2G | Type 2 / CHAdeMO |
| VW | ID.5 Pro | V2H, V2G* | Type 2 / CCS |
| Tesla | Model X | V2H, V2G* | Type 2 / CCS |
| Skoda | Enyaq 80 | V2H, V2G* | Type 2 / CCS |
| Mercedes-Benz | EQA | None | Type 2 / CCS |
| Audi | Q4 e-tron | V2H, V2G* | Type 2 / CCS |
| BMW | iX | V2H* | Type 2 / CCS |
| Kia | Niro | V2L | Type 2 / CCS |
| Polestar | 2 | V2L | Type 2 / CCS |
| Hyundai | IONIQ 5 | V2L | Type 2 / CCS |
| Volvo | EX90 | V2L, V2H, V2G* | Type 2 / CCS |
| Cupra | (listed as "FØDT" in source — likely a data-extraction artifact for a model name) | V2G, V2H | Type 2 / CCS |
| Ford | Mustang Mach-e | None | Type 2 / CCS |
| Peugeot | E-208 | None | Type 2 / CCS |
| Renault | Megane E-Tech | None | Type 2 / CCS |
| XPENG | G9 | V2L | Type 2 / CCS |
| MG | 4 | V2L | Type 2 / CCS |
| NIO | ET5 | None | Type 2 / CCS |
| BYD | ATTO 3 | V2L | Type 2 / CCS |

*"\*" in source = "annonceret" (announced, not yet delivered/confirmed in production).*
*Source (footnote 7): FDM, "Salgstal går amok for mange bilmærker" (FDM = Forenede Danske Motorejere, the Danish motorists' association).*
*Note: the "NIO / ET5" row appears with an odd formatting artifact in the source (a standalone "NIO" line before the BYD row) — reproduced here as best interpreted; readers should check the original table layout if exact row alignment matters.*

### Charger market readiness

- Most bidirectional-charger progress has occurred with **CHAdeMO**-plug chargers, but since CHAdeMO chargers are being phased out in the EU and very few EVs will use this plug, its relevance is diminishing. **Type 2/CCS plugs will become standard**, and work is underway to make CCS chargers and EVs standard-compatible.

### Table 2 — Overview of charger manufacturer V2X readiness, autumn 2023 (source: manufacturers' own websites, footnote 8 = ev.database.org unless noted)

| Charger manufacturer | Model | Direction | Plug | Status |
|---|---|---|---|---|
| Wallbox | Quasar | V2G, V2H | CHAdeMO | Launched |
| Wallbox | Quasar 2 (announced) | V2G, V2H | CHAdeMO | Launch date unknown |
| Rectifier Technologies | Highbury bidirectional DC charger | V2G, V2H | CHAdeMO and CCS | Launch date unknown |
| Ford | Charge Station Pro | V2H | CCS | Launched |
| SolarEdge Technologies | Bidirectional EV charger | V2G, V2H | CCS | Launching 2024 |
| Enphase Energy | Bidirectional EV charger | V2G, V2H | CHAdeMO and CCS | Launching 2024 |
| Autel Energy | MaxiCharger V2X | V2X | CCS and CHAdeMO | Launch date unknown |
| Delta Electronics | V2H bidirectional charger | V2H | CHAdeMO | Launch date unknown |
| Fermata Energy | Energy FE-15 | V2G, V2H | CHAdeMO | Launching Q1 2023 |
| Indra (footnote 10) | Unknown model | V2H | CHAdeMO | Launch date unknown* |
| Indra (footnote 11) | Unknown model | V2G | CHAdeMO | Launch date unknown* |
| Enel (footnote 12) | Unknown model | V2G | CHAdeMO | Launch date unknown* |
| E-ON (footnote 13) | Unknown model | V2G | Type 2 | Launch date unknown* |

*"\*" = used in V2H or V2G trials/pilots.*
*Footnoted source URLs: (9) cleanenergyreviews.info bidirectional-EV-charging blog; (10) indra.co.uk/v2h/; (11) indra.co.uk/v2g/; (12) company.enelxway.com FAQ; (13) eon.com "Bi.Clever" pilot project page.*

**Summary:** as of the report's writing, V2G with a ready-made off-the-shelf product is only achievable using **CHAdeMO**-compatible cars and chargers. Many charger and car manufacturers are working to make the technology CCS-compatible (both AC and DC), with tests and near-finished products underway, but timing remains uncertain.

### Example — CHAdeMO bidirectional chargers in Denmark: Frederiksberg Forsyning

- A fleet of **10 Nissan EVs**, used by **Frederiksberg Forsyning** in daily operations, connects to the grid via bidirectional chargers in the evening/night, delivering flexibility services to **Energinet** (the Danish TSO).
- **Economic benefit:** offering an average of **118 hours/week** of flexibility services generated revenue of approximately **12,000 DKK per EV per year**, reducing the utility's operating costs.
- The report notes profits would likely be higher today if a similar setup were implemented now, since batteries have grown significantly larger and electricity prices fluctuate more, improving the overall business case.
- (Source footnote 14: "Frederiksberg Forsyning - 7 År af V2G Operation" / "7 Years of V2G Operation.")

## Legislation — EU and Denmark

### Upcoming rules
- A recast of the **EU Bygningsdirektivet** (Energy Performance of Buildings Directive, EPBD) is underway. At time of writing, the new EPBD was expected to enter into force **end of 2023**, with an **18-month deadline** for member states to implement it into national law.
- This affects Denmark, where the current Bygningsdirektiv underlies the **Ladestanderbekendtgørelsen** (Charging Station Executive Order). Once the EPBD recast is adopted, the Danish Ladestanderbekendtgørelse must also be revised, imposing new requirements on building owners regarding the number of charging stations and preparation thereof, for new buildings, buildings undergoing major renovation, and existing buildings with more than 20 parking spaces.
- **New elements proposed in the EPBD:**
  - It must be possible to use the expected number of charging stations simultaneously and efficiently.
  - Charging stations must be capable of intelligent charging (smart charging), especially at buildings where vehicles park for long continuous periods, such as residential buildings and workplaces.
  - Charging stations must be capable of bidirectional charging (V2X) where relevant.
- This paves the way for smart-charging functionality becoming standard, and more chargers becoming V2X-ready.
- **Footnoted legal sources:**
  - Proposed EPBD recast: "Proposal for a DIRECTIVE OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL on the energy performance of buildings (recast)," 15.12.2021.
  - Danish Ladestanderbekendtgørelsen: **BEK nr 181 af 05/03/2020**, "Bekendtgørelse om forberedelse til og etablering af ladestandere i forbindelse med bygninger."

### Main Standards for Smart Charging and V2X

(Source Figure 5 summarizes the key communication standards between grid and EV systems — described qualitatively below.)

- **IEC 61850** — international standard defining communication protocols for intelligent electronic devices at electrical substations; specifies requirements for conductive charging systems including communication protocols and hardware interfaces; used at the interface between the grid and the charging operator; covers physical plugs, communication protocols, safety features, and performance criteria for EV charging equipment; plays a key role in ensuring interoperability and safety.
- **Open Charge Point Protocol (OCPP)** — a communication protocol defining the format of messages, commands, and data structures for communication between charging stations and a central management system. Most smart chargers today are **OCPP 1.6J**-compatible. The newer **OCPP 2.0.1** describes advanced smart-charging and control functions for utilities, charge operators, and EV owners, including support for the **ISO 15118** standard for secure communication between the charge point and the EV.
- **IEC 61851** — international standard setting requirements for EV chargers, covering plugs, communication protocols, safety features, and performance criteria; ensures interoperability and safety in EV charging.
- **ISO 15118** — standard focused specifically on communication between EV and EV charger; defines requirements for wireless communication for both cable-based and wireless charging, plus communication requirements for automatic connection devices and information services on charging/control status. Also defines communication messages and sequence requirements for bidirectional power transfer. **Part 20** of this standard specifically covers V2G communication, so EVs can communicate with the grid and deliver various services. Also includes the **Plug&Charge** feature, where the driver simply plugs in the charging cable and the EV begins charging automatically — beneficial for drivers and for semi-public locations like workplaces.
- **CHAdeMO** — a protocol extended to support V2G, allowing bidirectional power transfer between the EV and the grid.

### Remaining V2G Challenges (as of report writing)
- Rollout of **OCPP 2.0.1**, which most manufacturers/service providers are trying to switch to, is still ongoing and may take time.
- Implementation of **ISO 15118** is the biggest challenge for EV and charger manufacturers. Charge operators are working with EV and charger manufacturers on these standards.
- **CCS**, the dominant charging standard in Denmark and Europe, still lacks V2G compatibility, but V2G technology is expected to be integrated as standard within the next few years — exact timing uncertain.
- If a business wants V2G solutions immediately, the only currently available option is to use **CHAdeMO** for both charger and vehicle — a standard expected to be phased out entirely within a short number of years.

## Opportunities for Smart Charging and V2X — Implementation Roadmap

Source Figure 6 presents a roadmap for establishing charging infrastructure when a business is considering smart charging and V2X — the local electrical system and available site capacity should be investigated first, before considering charging equipment and smart-charging/V2X. Engaging an advisor during the process is recommended. The 8-step roadmap:

1. **Behov og mål (Needs and goals):** Determine the business's goals for EV charging.
2. **Lokalitetsudpegning (Site selection):** Identify charging-station locations; consider accessibility, proximity to building entrances, etc.
3. **Overvejelser ift. gældende og kommende lovgivning (Consider current/upcoming legislation):** Consider EU and Danish rules/standards, e.g., number of chargers required and future-proofing preparations.
4. **Elektrisk system (Electrical system):** Investigate the existing electrical system and how/whether it can be used to install chargers; consider future scalability.
5. **Opladningsudstyr (Charging equipment):** Investigate chargers meeting the business's needs re: charging power, connection options, software, scalability.
6. **Smartladning og V2X (Smart charging and V2X):** Consider the specific smart-charging/V2X opportunities for the business re: renewable energy, grid connection limits.
7. **Yderligere krav til virksomheden (Further business requirements):** Determine requirements for payment method, user experience, sustainability goals.
8. **Løsningsvalg, installation, test, drift (Solution selection, installation, testing, operations):** Determine the solution best meeting the set requirements; begin installation, testing, and monitor operations.

**Note (explicit in source):** this process is **iterative** — the electrical system must be considered when choosing chargers and any smart-charging/V2X use, to find the best placement and electrical-technical solutions.

## Building Owner's Use of Smart Charging on a Parking Lot

- Some smart-charging functions (remote control, charging schedule, charging power) can be used immediately just by buying an intelligent charger; other functions require more advanced setup, sometimes involving a third party (charge operator).

### Power sharing
- A basic smart-charging function where EVs connected to the same charger share charging power — commonly used for **22 kW chargers with two outlets**: when only one EV is connected, it can charge at full power (22 kW); when two EVs are connected, each can charge up to **11 kW** (22 kW total).

### Load balancing (Lastbalancering)
- Distributes available power evenly among multiple chargers/EVs to prevent grid overload. Also used to enable installing additional chargers at a site without increasing available Amperes (or conversely to reduce the Ampere connection needed for a given number of chargers).
- Depending on specific conditions, the load-balancing algorithm can be optimized to best serve the business's needs — e.g., a queue system for a fleet of EVs parked for many hours, charging selected EVs first and others later.

### Worked example — load balancing (source Figure 7)
- Building maximum power: **22 kW**; three chargers available at **11 kW each**.
- **Case 1:** two EVs connected, each charges at max **11 kW**.
- **Case 2:** a third EV connects; charging power is reduced from 11 kW to **7 kW** per EV to keep total power within the building's 22 kW limit. Without load balancing, the third EV would be unable to charge at all, since the first two already use all available power.

### Smart-charging conditions a driver can set
The EV driver can set the charger to charge when one or more of the following conditions are met:
- When the electricity price is low
- When CO2 values are low
- When renewable-energy production on the grid is high
- With grid-friendly rules

### Example — grid-friendly use
- Grid stability is challenged by increasing amounts of unstable energy sources (wind, solar) and growing numbers of unpredictable loads like EVs. EVs can be used to support the grid by adjusting charging power while connected.
- Charge operators offer solutions where a user simply plugs in the EV, and if a grid imbalance is detected, charging power is stopped or reduced. EV owners can, in some such agreements, receive compensation for the inconvenience.

## Smart Charging Combined with Renewable Energy Sources

- Solar and wind energy can be integrated with the EV charging process to reduce CO2 emissions and grid-electricity costs.

### Worked example — integrating renewable production (source Figure 8)
- A building with a solar PV system and a parking lot with three **11 kW** chargers, all grid-connected. If the building uses 10 kW at a given time, the solar panels produce 50 kW, and all EVs charge at 11 kW each (33 kW total), then the solar panels can supply the building's 10 kW, the 33 kW to the chargers, and export the remaining **7 kW to the grid**. (Efficiency losses are not accounted for in this example, per the source.)
- If a business lacks sufficient Amperes but produces local energy (e.g., via solar), a **battery storage system** can be worth considering — also useful when local production exceeds demand, maximizing local renewable-energy consumption while limiting grid load. Combining renewable production with a battery storage system allows storing surplus energy for later use (including potentially for EV charging), ensuring a stable, green power supply even when renewable production is irregular.

## Building Owner's Use of V2X Chargers

V2X chargers offer the same functionality as smart chargers, but additionally allow discharging EVs, with several potential benefits:

- **Emergency backup power:** during outages, V2X chargers can supply power from EV batteries to the building or critical infrastructure (e.g., essential lighting, heating/cooling, electronic devices) until grid power is restored — requires the EVs to be V2X-ready.
- **Renewable energy integration:** surplus renewable production (e.g., from on-site solar) can be stored in EV batteries during periods of grid energy surplus, then used later to power the building — particularly relevant when renewable production is low or prices are high, when power could instead be sold back to the grid at a profit.
- **Grid support:** if a business wants to contribute to grid stability, grid companies can leverage EVs' combined battery capacity. Currently, there is **no regulation of these services**, and their provision can be established through partnerships with various parties. (Footnote 17: a broader treatment of grid-support services is found in Sevdari, K., Calearo, L., Andersen, P. B., & Marinelli, M. (2022). *Ancillary services and electric vehicles: An overview from charging clusters and chargers technology perspectives*. Renewable and Sustainable Energy Reviews, 167, [112666]. https://doi.org/10.1016/j.rser.2022.112666.)

### Example — grid support via frequency regulation (source Figures 9-10)
- One of the services demonstrated to work under market conditions is **frequency regulation**, tested on commercial fleets at **Frederiksberg Forsyning and Bornholm**.
- Production and consumption must stay synchronized for stable, reliable power supply — grid frequency must be maintained at **50 Hz**. Grid-connected EVs can support frequency regulation to keep it constantly at 50 Hz. To deliver frequency regulation on commercial terms, vehicles must meet market requirements regarding how quickly the charger/EV can respond to market signals.
- Figure 9 illustrates the information/power flow for the frequency-regulation example with bidirectional chargers: grid frequency is measured and used to regulate EV charging/discharging power. Figure 10 illustrates charging/discharging power as a function of frequency: when frequency **exceeds 50 Hz**, the EV charges (acts as a load); when frequency is **below 50 Hz**, the EV discharges into the grid (acts as a generator).
- (Footnote 18: Marinelli, M., Thingvad, A., & Calearo, L. (2020). *Across Continents Electric Vehicles Services Project: Final Report*. Danmarks Tekniske Universitet.)

## Case Studies

Descriptions based on publicly available online information plus interviews with charge operators, businesses, and organizations involved.

### Case 1 — Optimizing Grid Capacity for EV Charging: PostNord

- **Context:** **PostNord** is replacing its diesel vehicles with EVs (footnote 19: "PostNord Gør julepakker grønnere: Udvider med 100 nye elbiler" / "PostNord makes Christmas parcels greener: expands with 100 new EVs"). Businesses often want (partly for cost reasons) to limit the number of Amperes purchased for charging-station installation, or maximize use of available grid connection. **Brøndby Hub** is a good example of how many Amperes can be saved via load balancing.
- **Technology:** **Monta** (footnote 20) delivered a solution for Brøndby Hub accounting for two specific characteristics of PostNord's EV fleet: (1) the fleet's EVs can charge on a **maximum of two phases**, meaning a 22 kW charger only delivers ~**14 kW (66%)** to these EVs; (2) EV schedules are well-documented, and most have one shift/day and are parked for many hours. Solutions implemented:
  - **Prioritizing charging points:** users/vehicles are prioritized when connecting to a charging point based on shorter charging periods and energy need.
  - **Phase rotation:** since the EV only charges on 2 phases, EVs are charged using different phase combinations by rotating across the three available phases — increasing capacity and reducing Amperes needed to purchase.
  - **Dynamic queuing:** EVs charge in shifts overnight; the charging-station algorithm queues and starts each vehicle accordingly.
- **Economic value:** phase rotation alone reduces the Amperes needed for installation by **33%**. Adding dynamic queuing (for two vehicle shifts) reduces total Amperes needed by a **further 50%**. With 1 Ampere costing approximately **1,200 DKK**, and an initial calculated need of **1,000 Amperes**, the estimated savings are approximately **800,000 DKK** in establishment costs.
- **Challenges:** despite using identical vehicle models and charger brands, variations occur in how much individual vehicles charge — requiring an initial correction/calibration phase to ensure optimal system performance.

### Case 2 — Demand-Response with DC Charging in Copenhagen: ViggoEnergy / Spirii

- **Context:** Demand-response services in charging infrastructure can help solve grid challenges and support faster transition to climate-friendly cars, vans, trucks, and buses — benefiting both the charge operator and the grid company, supporting a faster EV transition.
- **Example:** **ViggoEnergy's** DC city-hub with **14 charging outlets**, capable of delivering up to **300 kW**, connected to and operated via the **Spirii Connect** platform.
- **Technology:** the hub is heavily used (publicly accessible; used by taxis from many companies, private cars, and commercial vehicles). Taxis mainly charge **10:00-13:00**. The hub delivers **700-1,000 kWh per charging point per day**. Optimal grid operation requires demand to always equal supply (to avoid grid frequency deviating from 50 Hz); charging power is adjusted as part of the demand-response flexibility service, which requires the chosen charging infrastructure to be sufficiently compatible with the latest protocols (e.g., OCPP 1.6 or 2.0.1) and able to respond very quickly to user demand. Requires **Energinet** approval to deliver frequency service on both AC and DC chargers; the e-mobility platform must have a minimum response speed for delivering MW/h on the relevant energy markets (e.g., **DK1 and DK2**, Denmark's two price zones) prior to approval.
- **Economic value:** an average price for a single 300 kW DC charger is around **500,000 DKK**, excluding installation costs. Additional connection fees are payable to the grid company. A 300 kW charging station needs a **500A** connection, at approximately **1,200 DKK per Ampere**. With the demand-response service, ViggoEnergy's business case improves drastically — expected **Return on Investment (ROI) of 15-20%** improvement from adding demand-response revenue versus their usual business model, making it more attractive/feasible to build additional DC charging hubs.
- **Challenges:** the main challenge in such a project is ensuring the charging infrastructure has fast-enough response time and the right data exchange/documentation to meet energy-market requirements.
- (Source Figure 12: photo of 14 Alpitronics HyperCharger units located on Bernstorffsgade in Copenhagen, credited to Spirii.)

### Case 3 — World's First V2X Region: Utrecht

- **Context:** Utrecht aims to become the world's first V2G region. In a large-scale bidirectional-charging test project, **Hyundai, We Drive Solar, and others** collaborate on a large-scale V2X project. V2G chargers are installed across the region, specifically at a large parking lot used by major insurance company **ASR**, equipped with Type-2 chargers and powered by solar panels on car-park canopies. Project goal: use EVs to store power when solar production is high, and use that power when electricity prices are high or demand is high. The project aims to supply electricity to **2,530 households via V2G**.
- Estimated that **7 households** could get their necessary power from one car; in the future, a total of **8,500 cars** delivering power back to the grid will be needed to meet Utrecht's peak demand. Utrecht's public tenders now **require chargers to be V2G-ready**.
- **Technology:** chargers (AC chargers) developed by **We Drive Solar** in collaboration with various car manufacturers/models — mostly **Renault ZOE and Hyundai IONIQ 5**. The EV's inverter has been tested with manufacturers, including software/hardware upgrades to be **ISO 15118**-compatible. Inverter power is between **5 and 11 kW**; chargers are expected to mainly be destination chargers. Purpose: support the green energy-system transition, e.g., storing green energy in the EV battery during high-sun periods, and selling power to the grid during peak-load periods.
- **Economic value:** bidirectional chargers are **10-15% more expensive** than smart chargers of the same power — expected to fall as solutions become more standard. Making tovejsopladning (two-way charging) work requires both chargers and EVs to support the technology; the project has driven collaboration with manufacturers designing EVs for bidirectional charging, with only marginal impact on vehicle price. As the charger technology becomes more standard and demand grows, the price gap between V2X-ready and ordinary chargers is expected to shrink.
- With the ability to sell power back to the grid, it has been observed that at certain times it is more economically advantageous to use the cars to supply energy to the grid than to use them for ride-sharing/carpooling — as a result, cars were taken out of service during those specific hours.
- Expectation: an SoC between **20-80%** is good for battery health, and since discharge happens slowly, it is not expected to harm battery lifespan.
- **Challenges:** the biggest ongoing challenges lie in the technology needing standards approval. With **OCPP 2.0.1**, chargers will gain V2X functionality; within the next few years it's expected to become standard for EVs to support bidirectional charging. Flexibility services remain a challenge for chargers, as they cannot yet respond fast enough.
- (Source Figure 13: photo of a Hyundai Ioniq 5 charging at the solar-canopy parking lot, credited to Hyundai.)

## Named Bodies, Standards, Technologies

- **Region Hovedstaden / Copenhagen Electric** — publisher.
- **Rambøll** — report authors.
- **DTU (Danmarks Tekniske Universitet)** — multiple cited academic sources (Sevdari, Calearo, Marinelli et al.), reviewer Kristian Sevdari.
- **Gemeente Utrecht** (Utrecht municipality) and **We Drive Solar** — Utrecht case partners.
- **Monta** and **Spirii** — named charge-operator/platform companies (also case study partners).
- **Energinet** — Danish transmission system operator (TSO), referenced for flexibility-service approval and frequency-regulation examples.
- **Frederiksberg Forsyning** and **Bornholm** (fleets) — named for frequency-regulation and V2G pilot examples.
- **FDM (Forenede Danske Motorejere)** — Danish motorists' association, cited as source of car-brand sales data.
- Standards: **IEC 61850, IEC 61851, ISO 15118, OCPP (1.6J and 2.0.1), CHAdeMO, CCS, Type 2 (Mennekes)**.
- Legislation: **EU Bygningsdirektivet / EPBD (recast, proposed 15.12.2021)**; **Ladestanderbekendtgørelsen (BEK nr 181 af 05/03/2020)**.

## Notes on Data Completeness

- Table 1's "Cupra" row model name extracted as "FØDT," which is almost certainly a data-extraction artifact rather than an actual model name (possibly a rendering issue with a Cupra model name such as "Born," a homophone/mistranslation risk given "født" means "born" in Danish) — reproduced as extracted and flagged, **not corrected or guessed**, since the actual intended model name could not be verified from the source text.
- Several figures (Figures 1-10, 12, 13) are diagrams/photos whose exact visual content could not be fully transcribed from the extracted text; qualitative descriptions and any embedded example numbers are captured above, but exact diagram layouts should be checked against the original PDF if needed.
- The report explicitly limits its detailed treatment to passenger EVs, while noting (without further elaboration) that smart charging/V2X potential likely applies with even greater advantage to trucks, buses, and other heavy-duty electric vehicles — directly relevant to, but not elaborated for, this project's HDEV focus.
