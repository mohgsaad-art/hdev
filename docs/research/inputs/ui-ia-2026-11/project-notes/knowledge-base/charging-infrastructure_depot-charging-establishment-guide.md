# Guide to Establishing Depot Charging (Fleet Depot Charging Infrastructure)

**Source file:** `Guide til etablering af depotladning.pdf`
**Category:** Charging infrastructure — guide (fleet/depot charging, grid-capacity mitigation)
**Original language:** Danish (translated/summarized to English below; proper nouns kept in Danish)
**One-line summary:** A Region Hovedstaden / Copenhagen Electric guide aimed specifically at fleet owners ("flådeejere"), covering how the Danish electrical grid/tariff system works and presenting four detailed "mitigating measures" (charging strategy & smart charging, battery storage, collective charge parks, and energy hubs) to enable depot EV/HD-truck charging when grid capacity is constrained — directly the most relevant single document in this batch for the HDEV sizing tool.

## Administrative / Issuing Body
- **Publisher:** Region Hovedstaden, Center for Regional Udvikling; program Copenhagen Electric, Kongens Vænge 2, 3400 Hillerød. Phone +45 38 66 55 05. Email cph-electric@regionh.dk.
- Target audience: **flådeejere** (fleet owners) — this is the first document in the batch explicitly aimed at commercial/logistics fleet operators rather than residential/municipal contexts.
- Cross-references another Copenhagen Electric report: **"Renovationskørsel på el – 2023 opdatering"** (Refuse/waste-collection driving on electricity – 2023 update), URL: regionh.dk/til-fagfolk/trafik/Groenne-koeretoejer/Documents/Renovationskørsel på el – 2023 opdatering.pdf — this corresponds to another file in this project's document list (`Renovationskoersel-paa-el-–-2023-opdatering.pdf`), flagged as a cross-reference, not independently verified in this pass.

## Introduction and Main Conclusions (Section: Indledning og hovedkonklusioner)
- Purpose: overview of depot charging for electric vehicles and considerations involved, specifically for fleet owners.
- Core problem statement: installing charge points for vehicle fleets requires **a lot of power**, sometimes more than can be accessed in the short term. **Waiting time for grid capacity expansion can be long, sometimes more than 3 years**, and the cost of extra capacity can be high.
- Guide structure: (1) key characteristics of electrical infrastructure — grid company vs. energy supplier distinction, infrastructure buildup (cables, transformer stations, voltage levels), connection payment/annual tariffs, need for larger connections, grid capacity constraints, cooperation between companies, long grid-reinforcement lead times; (2) **ladestrategi og intelligent opladning** (charging strategy and smart charging); (3) **batteri** (battery) for energy storage/fast charging; (4) **kollektive ladeparker** (collective charge parks) — sharing charge points between companies; (5) **energihubs** (energy hubs) — companies jointly adjusting energy demand as a unit.
- **Scope note (explicit definitional restriction stated in source):** the guide uses a **strict definition of "mitigating measures"** — it assumes **battery-electric vehicles** only (hydrogen vehicles and plug-in hybrids are **not** covered). A measure only counts as "mitigating" if it actually results in reduced grid-capacity requirements **and** can achieve high reliability for the business. Example given: solar panels can be profitable and reduce CO2 emissions but are **not** always available when charging is needed (sun shines by day, trucks charge at night) — so solar panels alone are **not** considered a mitigating measure in this guide's framework, though they can be combined with a mitigating measure like batteries.

### Table 1 — Summary of Measures, Benefits and Challenges (verbatim, reproduced as a table)
| Measure | Benefits | Challenges |
|---|---|---|
| **Ladestrategi (Charging strategy)** | Creates overview of needs; Planning; Future-proofing | Resources required to develop it |
| **Intelligent opladning (Smart/intelligent charging)** | Reduces size of grid connection needed; Shifts consumption from expensive to cheap times | Requires planning of charging times; Combined need can exceed grid connection capacity; Costs for power-distribution equipment |
| **Batterilager (Battery storage)** | Reduces size of grid connection needed; Creates increased capacity; Charging when power is cheap | Expensive to acquire; Requires storage space |
| **Kollektive ladeparker (Collective charge parks)** | Increases total capacity and power access; Reduces connection/establishment costs; Provides more flexibility | Must enter agreements with other companies; Coordination of charging needs between companies; Must secure agreements on cost distribution |
| **Energihubs (Energy hubs)** | Reduces installation/operating costs for charging; Better utilization of e.g. solar panels; More flexibility in charging access | Large coordination need; Regulation not yet in place (esp. for virtual grid connections); Must secure agreements on cost distribution |

## Key Characteristics of the Electrical Infrastructure

### Grid Company vs. Energy Supplier
- Danish electricity sector = three key company types: **commercial energy producers**, **commercial energy suppliers**, and **public grid companies (netselskaber)**.
- **Grid companies own the electrical network** and are responsible for reliable grid connection.
- **One national grid company: Energinet.** Various **regional grid companies** responsible for networks in specific areas — **named examples: Nord Energi, Elnet Midt, N1, Vores Elnet, Cerius, and Radius**, plus a number of companies responsible for smaller areas.
- Grid-company info for a given area can be found on utility bills or by contacting one's energy supplier.
- **Energy supplier/elselskab** = the company delivering the electricity through the grid; can supply electricity anywhere in the country through the various grid companies.

### Structure of the Electrical Infrastructure
- Consists of cables and transformer stations across three voltage levels: **højspænding (HS, high voltage)**, **mellemspænding (MS, medium voltage)**, **lavspænding (LS, low voltage)**. A transformer station connects two different voltage levels.
- **Key components (verbatim structure):**
  - **Large-scale overhead cables** transport electricity over long distances at high voltage (HS), **up to 132 kV**, **owned by Energinet**.
  - **Transformer stations** between the large national cables and local cables, lowering voltage. Those between HS cables and the regional grid companies' MS networks are called **koblestationer** (switching/coupling stations), also up to **132 kV**, **owned by Energinet**.
  - **Thinner underground cables** distribute electricity locally at medium- or low-voltage level, **up to 50 kV**, **owned by the local grid company**.
  - **Mellemspændingsrum (MSR)** — medium-voltage rooms/local substations in the grid. MS and LS cables run from MSR into neighborhoods. **Medium-sized companies connect directly to an MSR or have their own MSR on-site.** Smaller companies connect to an MS or LS cable. **10 kV**, **owned by the grid company**.
- A schematic of the grid is shown in **Figur 1**, credited to **Radius** (grid connections on the supply network) — image content not extractable as text; described structurally above based on surrounding text.

### Connection Payment and Annual Grid Tariff
- Applying for a new or larger grid connection incurs **one-time connection costs**; tariffs vary by grid company and are published on grid companies' websites.
- **Annual fee for grid use**, composed of:
  - A **fixed annual cost component**, dependent on connection type.
  - **Three variable cost items:**
    1. **Annual costs based on maximum capacity of the connection (DKK per MW per year)**
    2. **Monthly costs based on maximum power drawn in that month (DKK per MW per month)**
    3. **Costs per unit of energy delivered (DKK per kWh)**

### Extra Charging May Require a Larger Connection
- A grid connection has a maximum capacity — the max electricity that can be drawn per hour, depending on connection type. Charging an electric van or truck via a grid-connected charge station requires **extra capacity**.
- If more capacity than the current maximum is needed, the connection must be enlarged — requested from the grid company, which will assess whether sufficient network capacity exists to realize the larger connection.
- **Sidebar "Arbejd sammen med virksomheder på din industri- eller erhvervspark" (Work together with companies on your industrial/business park):** companies on a shared industrial/business park often face the same challenges. Recommend contacting colleagues, business associations, or the park administrator when seeking electric logistics solutions/mitigating measures. Cooperation enables knowledge/experience sharing, pooling of information, waste-heat exchange, or joint mitigating measures.

### Grid Increasingly "Full" — Overload Already a Limiting Factor for EV Transition
- Due to the energy transition, electricity use keeps rising; the grid increasingly has insufficient capacity in more areas — **especially at the low-voltage level, and in some cases at the medium-voltage level too**.
- Grid operator determines needed capacity by measuring current consumption plus new connection requests; if this exceeds cable/transformer-station capacity, the grid is **"full" (overloaded/"overbelastet")**.
- Grid situation can change quickly due to new requests from other companies or grid-company expansions. Contacting the grid company gives the exact current situation. If a local grid is full, a new/larger connection currently cannot be granted — the operator queues new requests and expands the network ("tilslutningsforstærkning" — connection reinforcement). Once expanded, queued connections are realized. **One is only queued after formally signing an application and paying network costs**, after which the operator processes the application.

### Grid Reinforcement Can Take a Very Long Time
- If capacity is available in the area, realizing a new connection takes **approx. half a year or more** from application.
- If insufficient capacity exists, the grid company must expand ("forstærke" — reinforce) the grid — **this can, in some cases, take longer than a year.**
- **Longer reinforcement timelines (explicit tiers):**
  - If the **regional grid company's MS network** is locally overloaded: total lead time **2 to 5 years**.
  - If there's no more capacity in the **high-voltage network**: lead time **5 to 7 years, sometimes even 10 years**.
- Grid companies look ahead and often identify problems before they arise, so reinforcement work may already be underway in congested areas. Grid companies are working to simplify the process, but time remains a challenge where capacity is insufficient. The grid company can provide more detail on the current situation.

- **Sidebar "Overvejer man at skifte sin flåde til elektriske varebiler eller lastbiler?" (Considering switching your fleet to electric vans or trucks?):** because of these long grid-company lead times, it is critical to think early in the internal company process about the future electric fleet, additional power demand, and desired grid connection — and to contact the grid company early, well before a final application. Recommends consulting the **"Renovationskørsel på el – 2023 opdatering"** report (cited above) for a process on planning refuse-fleet electrification — most steps identical to other commercial fleets. **Figur 2**, credited to **4-Leaf Consulting 2023**, illustrates "the overall process for getting a grid connection," with indicative timeframes (image content — the specific step-by-step timeline figure itself was not extractable as text, only its caption/attribution).

## Mitigating Measures for Charging with Limited Grid Capacity

### 1. Ladestrategi og Intelligent Opladning (Charging Strategy and Smart/Intelligent Charging)

**Characteristics table (verbatim):**
| Property | Value |
|---|---|
| Type | Ladestruktur (Charging structure) |
| Tilbagebetalingstid (Payback period) | **3 to 10 years** |
| Omkostninger (Costs) | Developing charging strategy, installing chargers, extra costs for intelligent charge points |
| Fordele (Benefits) | Understanding of total charging demand and planning; flexibility to manage charging demand |
| Gennemførelsestid (Implementation time) | **1 to 2 years** |
| Pladsbehov (Space needed) | No extra space beyond the chargers themselves |
| Status | Mature |
| Sektorer (Sectors) | All sectors |
| Individuel/kollektiv | Individual |

**Description — Opladningsstrategi (Charging Strategy):**
Three key steps to establishing a charging strategy:
1. **Kørselsprofiler (Driving profiles):** map vehicle driving profiles — how many km/day do fleet vehicles drive? Multiple trips? Do vehicles return between trips (e.g., to load/unload at the company's own depot/address)?
2. **Opladningsbehov og ladningskapacitet (Charging demand and charging capacity):** translate driving profiles into required energy (kWh). Depending on battery capacity, one charge may suffice or intermediate charging may be needed. Available charging time and max charging capacity (kW) of the fleet's vehicles determine what power the chargers must deliver.
3. **Brugbarhed og fremtidssikring (Usability and future-proofing):** fleet size may grow; consider extra preparation for future chargers — empty conduit or cable trays for later cable runs, or installing extra charge stations now. Good idea to plan for future needs when applying for grid connection.
- Best developed **before** purchasing the electric vehicles. A specialized company (consultancy or charger/charging-system provider) can help; the company must provide its own logistics planning input.

**Description — Smart Opladning (Smart Charging):**
- A smart charging strategy determines when which vehicles charge, letting the company adapt charging demand to available grid capacity. Reduces grid use and results in lower societal costs.
- "Smart charging" is an overarching term for charging infrastructure and vehicle communicating/exchanging data via software, reducing peak load and preventing/limiting the need to expand the grid connection.
- Example: **load management software** ensures total charging request from multiple vehicles stays within the charge station's capacity. **Dynamic load management** flexibly aligns charge-point capacity with the building's energy consumption — requires connection to the central building energy management system.
- Complexity and extra cost of smart charging are relatively limited; already widely used in public chargers.
- **Figure 3** illustrates charging demand with and without intelligent charging — with intelligent charging, peak load shifts to afternoon and night (image content — described via caption; exact chart values not extractable).

**When is this measure appropriate?**
- Developing a charging strategy is useful for any company electrifying its fleet — one of the first steps. Smart charging implementation is especially suited to companies with flexible energy demand from buildings, production processes, and vehicles.

**Effects:**
- Optimal utilization of maximum available grid capacity; vehicle charging is kept within this capacity via smart charging, better utilizing the existing grid connection so a larger connection is not needed.

**Challenges and opportunities:**
- Requires insight into the company's driving profiles; strategy development can be done with a technical consultancy or a charging-station provider (charging operator).
- Smart charging is **not sufficient** if total daily energy demand exceeds what the grid connection can deliver — additional measures needed then.
- Because energy demand can be flexibly filled, this opens earnings-model opportunities: avoiding a larger/more expensive connection, charging at low-price times, and trading on energy markets.

**Combination with other measures:**
- Charging-strategy development is always required regardless of other available measures. Smart charging can increase the potential of other mitigation measures, since it lets vehicle energy demand be matched to available energy from another measure at a given time (e.g., solar/wind energy or a battery).

**Future outlook (source's own framing):** Vehicle electrification will keep spreading and EV numbers on roads will keep rising; smart charging will be an important factor in managing increased energy-system load and ensuring stable electricity supply.

### 2. Batteri (Battery Storage)

**Characteristics table (verbatim, comparing mobile vs. stationary battery):**
| Property | Mobilt batteri (Mobile battery) | Stationært batteri (Stationary battery) |
|---|---|---|
| Typisk størrelse (Typical size) | **300 kW / 350 kWh** | **1,000 kW / 1,000 kWh** |
| Lejepris (Rental price) | **50,000 – 750,000 DKK/month** | Not relevant (not typically rented) |
| Købspris (Purchase price) | **approx. 1.9 million DKK** | **approx. 3.7 million DKK** |
| Leveringstid (Delivery time) | Few weeks | **6 to 12 months** |
| Pladsbehov (Space needed) | **10 m² (10-foot container)** | **60 – 80 m²** |
| Status | Mature technology | Mature technology |
| Potentiale for energilevering (Energy delivery potential) | As long as the connection allows it | As long as the connection allows it |
| Sektorer (Sectors) | All | All |
| Individuel/kollektiv | Both | Both |

**Description:**
- A battery stores energy for later use; installing one lets a company better utilize its grid connection and charge vehicles faster at power levels higher than the connection normally allows.
- **Figure 4** shows an example charging hub with battery backup (decentrally placed in a container behind the technical cabinets), from **Allego's charging hub in Kaltenkirchen, Germany**.
- A company's grid connection is sized for the maximum expected power draw, but in practice much less power is used most of the time. The battery charges when there's surplus capacity on the connection and discharges during peak-load periods.
- Battery sizing depends on the grid connection, the company's current consumption, and the timing/power levels at which vehicle charging will begin. Battery suppliers can help select the right size.
- Battery can be **purchased, leased, or temporarily rented**. Many rental firms also offer direct purchase or post-rental purchase options. **A purchased battery can become more advantageous around the ~1.5-year mark**, especially for larger batteries (from 1,000 kW) — at this scale it's no longer in a movable container but a stationary installation. Stationary batteries are cheaper than mobile ones because the installation doesn't need to be movable, and there are economies of scale.

**Worked example ("Eksempel på batteri" sidebar):**
> "Et batteri med en kapacitet på 300 kW og en energi på 350 kWh har tilstrækkelig energi til at oplade fem til ti varevogne om natten, en til to lastbiler eller ca. en trækker-trailer."
- A **300 kW / 350 kWh** battery has enough energy to charge **5–10 vans overnight, 1–2 trucks, or approx. one tractor-trailer** overnight. These figures are higher if partial grid energy can also be used overnight.
- For daytime fast charging, the limiting factor is typically **power**, not energy quantity. With 300 kW, one can fast-charge **3–5 vans simultaneously, 2–3 trucks, or 1–2 tractor-trailers**.
- **After a half-hour of fast-charging vehicles, the battery itself needs 1–2 hours to recharge from the grid** before the next group of vehicles can charge.

**When is this measure appropriate?**
Suitable for all sectors/company types meeting these conditions:
- Power demand only exceeds grid-connection capacity at a **few times of day**. Batteries can be supplied at any size, so fleet size isn't decisive as long as the grid connection can deliver sufficient energy overall.
- The grid connection has, on average, sufficient capacity to meet daily charging demand. **Worked example:** connection is 100 kW, delivering max **2,400 kWh/day**; current consumption is 1,500 kWh/day → **up to 900 kWh/day of unused grid capacity available.**
- A rental battery is most attractive for periods up to **approx. 1 year**; for longer periods, a purchased battery can be attractive.

**Effects:**
- A correctly sized battery ensures the company can always charge its vehicles.
- **Rental battery cost:** relatively expensive. Monthly rental price is high and independent of how often the battery is charged/discharged. A battery fully charged/discharged twice daily yields a storage cost of **approx. 1.5 DKK/kWh** on top of the electricity price; costs rise if the battery is used less often.
- **Energy loss:** approx. **10–15%** between charging and discharging — this extra electricity must be purchased. **Combined, battery rental and energy loss add approx. 1.85–3.75 DKK/kWh on top of the electricity purchase price.**
- A **purchased** battery can be more economically advantageous long-term, especially a large battery — enables buying energy when cheap, using more self-produced electricity (e.g., solar), and eventually needing a smaller connection. If the company invests directly in a purchased battery, it may have already recouped much of the investment by the time the larger grid connection is ready — and the battery remains advantageous afterward.

**Challenges and opportunities:**
- No environmental permit required for a battery, but installation must comply with **fire-protection requirements**. Recommend inviting the local fire department to the battery installation so any comments can be addressed immediately.

**Combination with other measures:**
- **Smart charging** reduces peak load, potentially allowing a smaller (and cheaper-to-rent) battery.
- **Own energy production (solar, wind)** can feed the battery for later self-use — cost savings and more energy use within the same grid connection.
- **A generator** can run at constant power alongside a battery solution, operating at its most efficient point (saving fuel, reducing emissions), and potentially allowing a smaller (cheaper) generator.
- **A non-guaranteed connection** can be better utilized with a battery — vehicle-charging timing no longer needs to coincide with when extra grid capacity happens to be available. [Note: source references "se afsnit 0" — a broken internal cross-reference in the source document to a section on non-guaranteed connections that does not appear to be present/extractable in the supplied text; flagged as a source-document artifact, not an extraction gap on our part.]

**Future outlook:** battery-system costs have fallen markedly in recent years and are expected to keep falling; the market is not yet fully mature, so cheaper systems and market maturation could bring further significant cost reductions. In most cases it is **not** profitable to keep renting a battery once a larger grid connection is realized — the high rental price generally can't be offset by energy-purchase savings or more efficient connection use. Different for a **purchased** battery: already paid for, so no extra cost to keep using it, while it continues to provide savings.

### 3. Kollektive Ladeparker (Collective Charge Parks)

**Characteristics table (verbatim):**
| Property | Value |
|---|---|
| Type | Samarbejdsforhold (Cooperation arrangement) |
| Omkostninger (Costs) | Tariff per kWh is higher, but depends on the setup |
| Fordele (Benefits) | More efficient infrastructure utilization; using idle charging infrastructure when a neighbor isn't using it |
| Gennemførselstid (Implementation time) | Several months to establish agreements and installation |
| Pladsbehov (Space needed) | Existing or new parking spaces |
| Status | Feasible, but limited concrete experience |
| Sektorer (Sectors) | All sectors |
| Individuel/kollektiv | Kollektiv (Collective) |

**Description:**
- A collective charge park = a company shares charge points with other companies. Can be established on a project basis or via a commercial company's tender round; can also be established by the on-site companies themselves, the property owner, or authorities (municipality, region, state).
- **Two (three) types of charge parks:** public and semi-public (or fully private, shared only among companies who've agreed to it). Public charge parks are accessible to all; semi-public parks are on private land and are (limited) publicly accessible. [Footnote: fully private charge parks/points that a company chooses to share/establish jointly with other companies are henceforth treated as "semi-public" in this guide.]

**Case study — "Deling af ladeinfrastruktur og energi" (Sharing charging infrastructure and energy):**
> On Avedøre Holme, **Schulstad** and **Anchersen busser** (bus company) establish a shared community for charging their trucks and buses. The companies additionally install a **wind turbine** on-site to supply the charge park with power (cross-referenced to the Energy Hubs section), securing better power access and better utilization of the chargers.
- **Schulstad's trucks drive at night**, while **Anchersen's buses primarily drive during the day** — so the chargers are utilized over a larger portion of the day/night than if each company had established its own chargers separately. Total grid-connection need is reduced by this collective charging solution; there may also be reduced space needs for both vehicle/bus parking and charger installation.
- Photo credit: "Gengivelse venligst tilladt af Nordania Leasing" (Reproduction kindly permitted by Nordania Leasing).
- Collective charge parks can enable charger reservation — often organized so some chargers are always reserved for a specific company, or even placed on a specific company's own land but powered from a shared connection.

**When is this measure appropriate?**
- Suited when multiple companies in an area own or are considering EVs. Requires cooperation between companies; may be advantageous to involve a proactive property manager or an overarching organization to administer it. Mutual agreements needed on investment, benefits, charging costs, and/or operations/maintenance (depending on setup). Requires sufficient space (especially for charge stations and distribution stations) — the operator must use an existing parking area or purchase land. Some hauliers currently park trucks on leased land without the ability to establish their own charging infrastructure there — cooperation with the landlord or neighbors can be an option here.
- Requires upfront investment with some risk; which party is best placed to take the initiative/bear this risk varies by charge park. Risk is lower if future charging demand from different companies has already been identified. Dialogue with e.g. the landowner/landlord is necessary to agree who makes the investment and who actually owns the charge park; clarifying the economics enables agreement on what price the tenant pays the landlord and how investments are distributed.

**Sidebar — "Kollektive ladeparker er på vej langs motorvejene" (Collective charge parks are coming along the motorways):**
- Rising EV demand in Denmark is driving demand for charging stations along motorways. A project is underway to establish **600 charge points across 20 charge parks along Danish motorways**, part of **"Infrastrukturplan 2035"** (Infrastructure Plan 2035), expected to cost **500 million DKK**. Citation: "Nu bliver de første store ladeparker opført," Vejdirektoratet via ritzau.dk.
- For **heavy transport**, the state has also proposed **25 charge parks, valued at 700 million DKK**. Citation: trm.dk/nyheder/2023/25-nye-ladeparker-til-ellastbiler

**Effects — Six/Seven Key Benefits (source numbers these as 1–7, with "six" stated in the intro text but seven items actually listed — reproduced as-is, flagging the numbering discrepancy in the source):**
1. A charge park can be economically attractive because investment is shared with other companies, and the company can earn revenue by offering charge stations to third parties.
2. Grid connection for collective charge parks can be requested early. If grid reinforcement is needed, it will be carried out earlier (and hopefully on time). **Caveat:** charge stations also require grid capacity, which may mean other companies cannot get a grid connection — so the required connection size for a charge park must be carefully investigated.
3. Parties apply together for one larger connection instead of individual smaller ones — the grid company generally doesn't need to account for a lower power level, reducing overload risk.
4. Energy-consumption optimization is possible — with more vehicles connected, smart charging and energy sharing can be applied more effectively, reducing grid load, or allowing some vehicles to charge extra-fast when briefly needed. A company might also be able to charge on more than one charge station at certain times, which might not be possible with a smaller individual connection.
5. Companies unable to charge on their own site due to space constraints, or because they're on leased land and don't control the layout, can use the collective charge park.
6. Because the charge park is larger than individual company charge stations, it may be more cost-effective to book charge stations — advisors can provide more information on this.
7. Establishing a collective charge park between neighboring companies can increase individual charger utilization (smart charging), and energy communities can be formed around e.g. solar panels or wind turbines (energy hubs).

- **Downside noted:** especially publicly accessible charge parks may have potentially **higher electricity prices** than charging on one's own site — especially commercial (fast) charge parks charge higher prices. Per-kWh price is very important to total cost of ownership for EVs, so as low a price as possible, even at collective charge parks, is crucial to making electric logistics attractive. Also important: always having access to a charge station when needed — should be secured in agreements between the charge-park operator and companies, e.g., via reservation/planning systems or charge stations restricted to a specific company (or specific vehicle).
- If companies themselves establish a community for a charge park (e.g., for two companies' vehicles), pricing reflecting actual establishment/operation/electricity costs can be better agreed, since the charge park isn't assumed to be a profit center for either company, but a measure ensuring participating companies' charging access.

**Challenges and opportunities:**
- Challenge: establishing cooperation so costs are manageable and companies have sufficient assurance their charging needs will be met. Another key factor: finding a good location. Publicly accessible charge parks offer an attractive business-model opportunity and increased charging adoption for companies that contract with the charge-park operator. Local cooperation between companies can also have further benefits for energy-area cooperation or business processes.

**Combination with other measures:**
- **Smart charging:** especially exploitable at a charge park with many charge stations.
- A collective charge park **can be part of an energy hub** due to flexible demand.
- A **battery** can be installed at a collective charge park.
- A collective charge park is well-suited to efficient local energy use — whether solar energy can be used locally depends on when during the day the charge stations are primarily used.

**Future outlook:** collective charge parks are a future-proof solution, though charge-park uptake could decline if many parties later realize their own chargers. Important to examine at design stage whether the charge park can meet all future charging needs and whether there's room for expansion. No major developments foreseen that would change the future sustainability/profitability of a charge park.

### 4. Energihubs (Energy Hubs)

**Characteristics table (verbatim, comparing physical vs. virtual hub):**
| Property | Fysisk hub (Physical hub) | Virtuel hub (Virtual hub) |
|---|---|---|
| Type | Ladeinfrastruktur (Charging infrastructure) | (same) |
| Tilbagebetalingstid (Payback period) | **A few years** | Unknown |
| Omkostninger (Costs) | Cabling, coordinating use with other parties | Coordinating use with other parties |
| Fordele (Benefits) | Own operation, reduced grid connection | Reduced grid connection |
| Løbetid (Duration/term) | A few years | Unknown |
| Pladsforbrug (Space use) | Cabling | None |
| Status | Mature phase | **Pilot phase** |
| Sektorer (Sectors) | Companies with uneven/non-uniform energy demand | (same) |
| Individuel/kollektiv | Kollektiv (Collective) | (same) |

**Description — Two Key Configuration Types:**
- **Fysisk hub (Physical hub) — within a private network:** the company, together with others, establishes its own electrical grid. **This requires an exemption from Konkurrence- og Forbrugerstyrelsen** (the Danish Competition and Consumer Authority). A commercial party or organization establishes and administers the network on behalf of participating companies, creating a closed distribution system. This private network has **one** connection to the public grid.
- **Virtuel hub (Virtual hub) — within the public network:** **not yet established in regulation or by network owners; exists only in pilot projects.** Here the company is connected to the public grid and virtually "connected" to other companies via this network. The network owner administratively treats each company as one connection and bills electricity use accordingly. Within an energy hub, companies adjust their energy demand so that, as a unit, they better utilize the grid connection — needing a smaller combined connection than they would individually.
- Within the framework, companies coordinate energy demand with each other — e.g., by reserving or purchasing time slots. Smart energy management guarantees companies their energy needs within the realized connection; a central energy management system then distributes energy at agreed times. It is therefore important that connected companies agree on who may use energy when.

**Worked example ("Eksempel på en energihub" + Figure 5):**
- Theoretical example: Companies A, B, and C each individually have a max capacity of **10 MW per company**, but want to use more energy. With an energy hub, the companies can use **30 MW combined in total**. If they coordinate energy use with each other, they can draw more energy from the network at certain times.
- In the figure: **Company C can use more than 10 MW between 00:00 and 06:00**, and **Company A between 16:00 and 22:00.** The companies thus share a grid connection and can use more electricity through the energy hub.
- Not many concrete energy-hub examples are known; a few comparable cases exist, e.g., **Lemvig station**.

**When is this measure appropriate?**
- Suited to companies approaching the limits of their own connection during peak-load periods, where together companies have sufficient grid capacity. This enables offsetting peak loads by exchanging capacity — requires companies to have **staggered ("forskudt") energy demand**. If all companies peak at the same time, an energy hub cannot mitigate grid-capacity constraints.

**Effects:**
- Because companies can locally exchange capacity with each other within the shared connection, there's less need to do so via the public network. If companies have also established solar panels or a wind turbine for power production, opportunities improve for using power "behind the grid connection," and connection fees / electricity duties are reduced through better balancing of needs.

**How do I start with an energy hub?**
- Requires an initiator ("initiativtager") who engages in dialogue with various local companies to determine whether their load demand is staggered relative to other companies. This could be an initiating company, the relevant municipality, or a technical consultancy. **Coordination with the grid company is also hugely important and must start early in the process.**

**Case study — "Energihub på Lemvig station" (Energy Hub at Lemvig Station):**
> In **2022**, an agreement was reached on cooperation between **Midttrafik** and **Midtjyske Jernbaner** (regional public transport authority and regional railway company) at Lemvig station, enabling simultaneous charging of cars, buses, trains, and e-bikes.
- A **battery storage** system is being established at the station for charging the new battery-powered trains serving the **Lemvigbanen** (Lemvig railway line) and the electric buses running between **Lemvig–Struer** and **Lemvig–Holstebro**. To reduce grid-connection needs, the battery solution is established alongside a single shared transformer station, from which connections are made to trains, buses, and passenger-car chargers. Each of these needs requires its own charging infrastructure setup with its own grid access and varying demand.

**Challenges and opportunities:**
- Challenge: building a shared community among companies with a common vision. A party must take the initiative, with responsibility coordinated among parties; stakeholder interests must be weighed. In periods where energy demand exceeds connection capacity, available capacity must be **fairly distributed** among the off-taking companies.
- For capacity distribution, an **independent party** applying a distribution key ("fordelingsnøgle") should be established — this independence is important for the energy hub's future-proofing, and also applies to price differentiation on the network, ensuring a fair price for all connected parties.

**Combination with other measures:**
- **Renewable energy (solar, wind)** can be used relatively cheaply locally; a company can exchange produced energy directly with other connected companies.
- The combined energy hub's capacity can be **temporarily expanded at favorable times with a non-guaranteed connection**, letting companies temporarily draw or return more energy via the main connection.
- Within an energy hub, **smart charging is required** to adjust energy consumption.
- A **battery** makes the energy hub more efficient and able to use more energy overall; a battery can also help with peak loads caused by simultaneity of connected companies.
- Energy consumption can be supplemented with a **generator** during prolonged peak load.

**Future outlook:** within strict regulatory frameworks, it is already possible to integrate a physical energy hub into the current grid. A virtual energy hub is **currently not possible**, but pilot projects are underway in this area.

## Closing Statement (back cover)
> "Guiden beskriver en række muligheder for at reducere behovet for eltilslutning og for at imødekomme behovet for strøm, hvis der er begrænset netkapacitet." (The guide describes a range of options for reducing the need for grid connection and for meeting power demand where grid capacity is limited.)

## Referenced Organizations, Companies, and Projects
- **Energinet** — Danish national TSO/grid company (owns HS cables/koblestationer up to 132 kV)
- Named regional grid companies (netselskaber): **Nord Energi, Elnet Midt, N1, Vores Elnet, Cerius, Radius**
- **Konkurrence- og Forbrugerstyrelsen** — Danish Competition and Consumer Authority (exemption required for physical energy hub private networks)
- **Radius** — credited for Figure 1 (grid schematic)
- **4-Leaf Consulting** — credited for Figure 2 (grid-connection process timeline), 2023
- **Allego** — cited for the example battery-backed charging hub in **Kaltenkirchen, Germany** (Figure 4)
- **Schulstad** (bakery/logistics company) and **Anchersen busser** (bus operator) — case study, collective charge park + wind turbine at **Avedøre Holme**
- **Nordania Leasing** — photo credit for the Schulstad/Anchersen case
- **Vejdirektoratet** (Danish Road Directorate) — motorway charge-park project (Infrastrukturplan 2035)
- **Midttrafik** and **Midtjyske Jernbaner** — case study, Lemvig station energy hub (2022 agreement)
- Referenced report: Copenhagen Electric, "Renovationskørsel på el – 2023 opdatering"

## Referenced Government Programs / Funding
- **"Infrastrukturplan 2035"** — Danish national infrastructure plan; funds **20 motorway charge parks (600 charge points total), cost 500 million DKK**
- State-proposed **25 heavy-transport charge parks, value 700 million DKK** (per trm.dk 2023 news item)

## Key Numeric Data Table (consolidated quick reference, verbatim from source)
| Metric | Value |
|---|---|
| Typical grid-reinforcement time (capacity available) | ~0.5 year or more |
| Grid-reinforcement time (local MS network overloaded) | 2–5 years |
| Grid-reinforcement time (no HS network capacity) | 5–7 years, sometimes 10 years |
| Charging strategy payback period | 3–10 years |
| Charging strategy implementation time | 1–2 years |
| Mobile battery typical size | 300 kW / 350 kWh |
| Mobile battery rental price | 50,000–750,000 DKK/month |
| Mobile battery purchase price | ~1.9 million DKK |
| Mobile battery delivery time | few weeks |
| Mobile battery space | 10 m² (10-ft container) |
| Stationary battery typical size | 1,000 kW / 1,000 kWh |
| Stationary battery purchase price | ~3.7 million DKK |
| Stationary battery delivery time | 6–12 months |
| Stationary battery space | 60–80 m² |
| 300kW/350kWh battery overnight charging capacity | 5–10 vans, 1–2 trucks, or ~1 tractor-trailer |
| 300kW battery daytime fast-charge capacity | 3–5 vans, 2–3 trucks, or 1–2 tractor-trailers simultaneously |
| Battery recharge time after 30-min fast-charge session | 1–2 hours from grid |
| Battery purchase break-even point (rental vs. buy) | ~1.5 years |
| Rental battery storage cost (2 full cycles/day) | ~1.5 DKK/kWh on top of electricity price |
| Battery round-trip energy loss | ~10–15% |
| Combined rental+loss cost impact | ~1.85–3.75 DKK/kWh on top of electricity purchase price |
| Collective charge park implementation time | several months |
| Motorway charge park program (Infrastrukturplan 2035) | 20 parks / 600 points / 500M DKK |
| Heavy-transport charge park program (state proposal) | 25 parks / 700M DKK |
| Energy hub (physical) payback period | a few years |
| Example energy hub company capacity (illustrative) | 3 companies × 10MW individual = 30MW combined via hub |

## Relevance Notes for HDEV/Depot Tool (Claude's own framing, not from source)
- This is the **most directly relevant document in this batch** to the HDEV sizing/modelling tool's core purpose: it addresses grid-capacity-constrained depot charging for commercial fleets (vans, trucks, tractor-trailers) explicitly, with concrete Danish figures for grid connection tariff structure, grid-reinforcement lead times (0.5–10 years depending on voltage level/local congestion), and battery/collective-charging/energy-hub mitigation strategies.
- The battery sizing/cost table (300kW/350kWh mobile @ ~1.9M DKK purchase, 1000kW/1000kWh stationary @ ~3.7M DKK) and the worked "vans/trucks/tractor-trailers charged per battery" example are directly citable reference data points for depot battery-buffer sizing calculations in the tool — sourced from a named, dated (implicitly ~2023-2024, matching cited "2023" reports elsewhere in the same document) Region Hovedstaden publication.
- The grid connection tariff structure (fixed annual + 3 variable components: DKK/MW/year, DKK/MW/month, DKK/kWh) is a useful template for a depot's utility cost model, though exact DKK figures per grid company are explicitly stated as varying and not given numerically in this document (must be sourced per grid company).
- The energy-hub legal note (physical hub requires a Konkurrence- og Forbrugerstyrelsen exemption; virtual hub not yet regulated, pilot-only) is an important regulatory caveat for any tool feature modeling shared/pooled depot grid connections in Denmark.
