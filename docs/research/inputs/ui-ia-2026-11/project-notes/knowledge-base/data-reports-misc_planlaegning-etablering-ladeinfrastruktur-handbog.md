# Planning and Establishment of EV Charging Infrastructure — Handbook

**Source file:** `ac359ff9cfba478b8f60cae21d0030dc.pdf` (opaque hash/ID filename — original document title recovered from content: "Planlægning og etablering af ladeinfrastruktur til elbiler")
**Category:** Technical handbook / municipal planning guidance
**Original language:** Danish (translated to English below; proper nouns kept in Danish)
**One-line summary:** A September 2022 Vejdirektoratet handbook giving Danish municipalities comprehensive technical, legal, and planning guidance for calculating demand, siting, tendering, and physically laying out publicly accessible EV charging infrastructure for passenger cars.

## Publication Details
- **Publisher:** **Vejdirektoratet** (Danish Road Directorate), "Vejudstyr" (Road Equipment) series.
- **Document type:** "Håndbog" (Handbook), explicitly labeled in source metadata.
- **Published:** 14 September 2022. **Status:** "Historiske" (Historical/archived), "Ophørsdato" (expiry date) 17 September 2024.
- **Authorship:** Prepared by the same ad hoc group under vejregelgrupperne **Vejudstyr** and **Byernes Trafikarealer** as the companion tender-template package (see membership list in the companion "Vejledning" document, `claude/knowledge-base/data-reports-misc/ladestandere-vejledning-udbudsforskrifter.md`), with an ad hoc group additionally including Søren Madsen and Frants Torp Madsen (Vejdirektoratet), Line Engell Nørby (Rambøll consultant).
- **Additional consulted parties:** **Dansk e-Mobilitet**, **Drivkraft Danmark**, **Forenede Danske Elbilister (FDEL)**, **FDM** (Danish Motorists' Association), **Danmarks Tekniske Universitet (DTU)**.
- **Scope:** Limited to planning/establishment of charging infrastructure for **passenger cars on public land**; explicitly excludes home charging and charging infrastructure for e-bikes, buses, and trucks, and excludes charging infrastructure on the **state road network** (handled elsewhere).

## Purpose
To give municipalities and other market actors concrete guidance on planning sufficient charging infrastructure rollout and on considerations for tendering and installing charging stations for passenger cars. Written in H2 2021–H1 2022; explicitly notes the EV market's rapid development means conditions may have changed by the time of reading.

**Target audience:** primarily municipal employees working in traffic, roads, environment, operations, or elsewhere in the municipality; also useful for employees in regions, utility companies, housing organizations, retail, etc.

## Legislative References (Section 1.1.1)
- Bekendtgørelse om forberedelse til og etablering af ladestandere i forbindelse med bygninger (Ladestanderbekendtgørelsen)
- Lov om infrastruktur for alternative drivmidler til transport (AFI-loven)
- Bekendtgørelse om kommuners og regioners ydelse af betaling til operatører af offentligt tilgængelige ladepunkter
- Bekendtgørelse af lov om private fællesveje
- Lov om offentlige veje m.v.
- Bekendtgørelse om anvendelse af vejafmærkning
- Bekendtgørelse af færdselsloven
- Bygningsreglementet (BR18)
- Direktiv 2014/23/EU om tildeling af koncessionskontrakter
- Bekendtgørelse om sikkerhed for udførelse og drift af elektriske installationer
- Bekendtgørelse om krav til offentligt tilgængelig infrastruktur for fossile brændstoffer og alternative drivmidler m.v.
- Bekendtgørelse af lov om registrering af ledningsejere
- Bekendtgørelse af lov om elforsyning
- Netselskabers bestemmelser for tilslutning til og brug af distributionsnettet
- Fællesregulativet

## Terminology (Section 1.2)
Similar to the companion Vejledning document's terminology table, with these additional/distinct entries:
- **Hybridbil (HEV)** — has a battery charged via the combustion engine; cannot be charged via cable; self-charges when the engine runs and during braking
- **Mild hybrid (MHEV)** — cannot run on pure electric power; assisted by an electric motor at specific moments (e.g., acceleration, start/stop) where the combustion engine would otherwise use a lot of fuel
- **V2G / Vehicle to Grid** — technology letting an EV function as a grid battery, delivering electricity back to the grid (for payment) during peak-load situations, reducing grid overload risk

## Section 2: Legal Basis (Grundlag)

### 2.1 Ladestanderbekendtgørelsen
- Full citation: **BEK nr. 181 af 05/03/2020**, "Bekendtgørelse om forberedelse til og etablering af ladestandere i forbindelse med bygninger."
- Took effect **10 March 2020**. Implements parts of an EU directive on buildings' energy performance (**Directive 2018/844/EU**, amending 2010/31/EU and 2012/27/EU).
- Issued under the **Byggeloven** (Building Act); requires building owners (regions, municipalities, companies, housing organizations, others) to prepare for and/or install charging stations at buildings in specific cases.
- **SMEs (Små og Mellemstore Virksomheder) are exempt** for existing buildings. SME definition (per source, citing "Vejledning til ladestanderbekendtgørelsen," 1 January 2021): fewer than 250 employees and annual turnover under €50 million, or total annual balance sheet under €43 million.
- Structured by: residential vs. non-residential, then further by new construction, buildings undergoing major renovation, and existing buildings.
- For renovation, the requirement applies to "major rebuilding," defined by all of the following being met: more than 10 parking spaces attached to the building post-renovation; construction work is underway on the building; the parking facility or the building's electrical infrastructure is being rebuilt; the cost of establishing/preparing for charging stations is under 7% of total renovation costs.
- **No requirement** that charging stations be publicly accessible and/or operated by a charging operator.
- Charging stations must be located on parking spaces associated with the building — not necessarily consolidated on a single parking area or the same cadastral lot.
- Many existing public buildings fall under the non-residential category (administration buildings, halls, schools, daycare institutions, equipment yards, clubhouses etc.); some public buildings (e.g., care centers, residential institutions) are managed under the residential category; **BBR** (Building and Dwelling Register) is used to determine category where multiple functions share a building complex.

### 2.2 AFI-loven (Lov om infrastruktur for alternative drivmidler til transport)
- Took effect **6 April 2022**. Sets requirements for establishing and operating publicly accessible EV charging stations on land under municipal/regional control. Carries forward the previous AFI law's implementation of international conventions and EU rules (including parts of the **AFI-direktivet**, EU 2014/94/EU).
- Combined with **bekendtgørelse nr. 414 af 4. april 2022** (see section 2.3), municipalities/regions may co-finance charging infrastructure on their own land.
- **AFI-lovens § 5** — conditions under which municipalities/regions may co-finance charging station installation, quoted in full (as reproduced in the source):
  1. Establishing charging stations or delivering charging services fulfills the municipality's/region's obligations under other legislation
  2. Funds were received from the state, EU, or private parties specifically to establish charging stations on the municipality's/region's land
  3. Funds derive from income the municipality/region previously received from agreements under § 4
  4. The charging station is primarily used to charge the municipality's/region's own electric vehicles
  5. The right to make payment follows rules set by the Transport Minister per stk. 2
  - **Stk. 2:** the Transport Minister can set rules allowing municipal/regional councils to make payments to charging-point operators beyond the cases in stk. 1, nos. 1–4, within certain limits, in connection with agreements under § 4
- AFI-loven gives municipalities legal authority to establish publicly accessible charging stations on **public road land**, including both formally designated road land and road land not yet designated but managed under the Vejloven; **Vejlovens § 80 can no longer be used** for this purpose (per AFI-lovens § 19).
- Municipal co-financing rules are set in **bek. nr. 414 af 4. april 2022** (see 2.3).
- Public authorities must ensure charging-station prices are comparable and transparent. **AFI-lovens §§ 7–9** set requirements for new charging stations (after the law took effect) regarding card-payment capability and roaming:
  - Payment card acceptance required at charging stations on public land or established with public co-financing, **except** stations under 50 kW if usable via a charging-services provider (roaming)
  - Publicly accessible charging points must display, on an electronic screen, a list price per kWh and the total purchase price
  - Existing charging stations will be subject to the same payment/roaming/display rules from **2026**
- **Transitional provisions (§ 20):** if permission was already granted for a publicly accessible charging station on public land, the station only needs to meet payment-solution requirements if established after **1 July 2022**, or otherwise only when the permit expires, at latest **1 January 2026**.
- Charging stations on municipal road land remain regulated under **Vejlovens § 88** (tank facilities, per § 88 stk. 5); parking decisions are generally expected to follow **Færdselslovens § 92, stk. 1, nr. 1** (reserving the parking space/bay for EVs, possibly only charging EVs). Establishing a charging station will often require the municipal council to grant an excavation permit per **Vejlovens § 73**, setting conditions for groundworks and cable/cabinet placement in/on the road area.

### 2.3 Bekendtgørelse om kommuners og regioners ydelse af betaling til operatører af offentligt tilgængelige ladepunkter
Issued under AFI-lovens § 5, stk. 2, contains two provisions (quoted in full per source):
- **§ 1:** A municipal council, regional council, or municipal partnership may, when concluding an agreement on the right to operate publicly accessible charging points under the law's § 4, pay the operator per the law's § 5, stk. 1, nr. 5, provided the municipality/region/partnership does not disclose in advance details of the intended payment that formed the basis for the decision to tender the agreement — unless other legislation requires the information be publicly available.
- **§ 2:** The executive order took effect **1 April 2022** and automatically lapses **31 December 2024**, unless otherwise decided before that date.

### 2.4 Bekendtgørelse af lov om private fælles veje
- Private shared roads are administered under **LBK nr. 1234 af 01/11/2015** (as amended). Municipalities are the road authority for private shared roads but generally do not own them — typically owned by the private landowners who, along with other entitled parties ("vejberettigede"), have a right of way.
- Municipalities have **no obligation** to ensure charging infrastructure on private shared roads, but as planning authority may have an interest where extensive street parking exists and would otherwise create a gap in overall charging coverage — can support installation via dialogue with owners/homeowners' associations and entitled parties.
- Because a municipality doesn't own a private shared road, it has **no AFI-loven authority** to tender the right to act as a charging operator on that land. The road owner, entitled parties, or a homeowners' association may, **with road authority permission**, install charging infrastructure per **kapitel 10, § 66** of the private-roads law:
  - **§ 66** (quoted in full per source): on private shared road land, municipal council approval is required to: (1) permanently or temporarily place waste, equipment, materials, movable items, unregistered vehicles, sheds, site trailers, containers, stalls, vending machines, signs, fencing etc.; (2) place vehicles for sale or rental without a driver; and (3) as part of business activity, place vehicles for repair, refueling, cleaning etc. — Stk. 2: the Transport Minister can exempt certain uses from the approval requirement and authorize the road authority to set detailed rules, which must be published. Stk. 3: before approving stk. 2 cases, the municipal council must consult police. Stk. 4: the municipal council can remove unauthorized items at the responsible party's expense if a removal order isn't followed. Stk. 5: if the placement obstructs traffic, the municipal council or, in urgent cases, police may remove it at the responsible party's expense without prior order.
- Such approval is a **public-law permit** (per privatvejslovens § 56) — the municipality won't oppose the permitted use, but whether the recipient can actually exercise it is a private-law matter (interpretation of the road-right agreement).
- If a homeowners' association/road owner/entitled parties request private charging infrastructure on a private shared road, the municipality **can refuse** if general public-law considerations weigh against it. Municipalities that own many private shared roads **can** tender charging infrastructure areas under AFI-loven authority on those roads, subject to whether entitled parties must consent per the road-right agreement.
- Municipalities **cannot expropriate** private shared roads/parking spaces to provide for charging infrastructure (doesn't fall under expropriation provisions in Vejlovens kapitel 10). If a municipality wants charging infrastructure on private shared roads, it can choose to **reclassify** them as municipal roads per **Vejlovens § 15**.
- Other relevant private-roads-law provisions: **§ 57, stk. 1** (parking restrictions near a charging station, requiring police consent) and **§ 60** (referencing Vejlovens § 88); also **§§ 67–68** regarding excavation permits for laying cables and accessories.

## Section 3: Technical Specifications for Charging Infrastructure

### About EV Energy Consumption
A home carport charge box typically delivers **11 kW**, charging 11 kWh per hour — comparable to running 11 washing-machine loads within a single hour (source: Norlys, via elpristavlen.dk).

### 3.1 Types of Charging Plugs
Most widespread in Europe (de facto standard, the only two required types per this handbook): **Type 2** and **CCS-Combo**.
- **Type 2:** most common/widespread plug for EVs in Europe, can draw up to **55 kW**, though few EV batteries can accept this; many current EVs accept **11 kW AC**; higher AC acceptance speeds expected in future EVs.
- **CCS-Combo (Combo Charging System):** fastest-charging plug type, an evolution of Type 2; similarity between the two means an EV can typically accept both; developed to streamline/simplify charging and is the European standard; **all fast and rapid chargers use this plug**.

### 3.2 Types of Charging Stations

#### 3.2.1 Normalladere (≤22 kW)
AC chargers; conversion from AC to DC happens inside the EV's internal charger, limiting charging speed relative to DC chargers. Many chargers/boxes can deliver 22 kW, but the vehicle's internal charger determines actual uptake. Normal chargers charge at **3.7–22 kW**; charge time **4–6 hours** for a full charge. Typically installed at homes or workplaces (longer-duration parking locations); dwell time defines charge time.
- **Cheapest charging station type to install.** A 22 kW station with two outlets costs on average **65,000–75,000 DKK** (including groundworks and connection fee), **2020 price** (source: "Guide til kommunal strategi for etablering af ladeinfrastruktur," COWI and Energi på Tværs, https://elbilviden.dk/wp-content/uploads/2020/10/Kommunal-strategi-for-ladeinfrastruktur.pdf). Large price variation depending on specific site conditions.
- Photo examples given: EON charger in Aalborg; Clever charger in Aalborg (Rambøll photos).

#### 3.2.2 Højeffektladere (>22 kW)
DC chargers ("højeffektladere"); conversion happens in the charging station rather than the vehicle, giving more efficient charging independent of the vehicle battery's conversion quality.

**Hurtigladere (Fast chargers):** charge at **50–75 kW** (typically 50 kW), giving a typical charge time of **40–60 minutes**. Typically installed at publicly accessible parking near retail (charge time suits a longer shopping trip); dwell time partly determines charge time, since customers may extend their shopping trip to get extra charge. Can help retailers attract customers and can reduce the need for other publicly accessible charging infrastructure nearby.
- Cost: a fast charger (possibly 2 outlets) at 50–75 kW costs **350,000–450,000 DKK** (including groundworks and connection fee), **2020 price**, same source as above.
- Photo example: fast charger at Føtex, Esbjerg (photo: Torben Meyer, Esbjerg Kommune).

**Lynladere (Rapid chargers):** charge at **150 kW or more**, giving charge time of **10–20 minutes** — here, charge time itself defines dwell time. Typically installed along the primary road network and other locations where minimizing charge time is desired. The most expensive charging station type; consumers must often accept a higher price per kWh. Because many EVs cannot yet accept the fastest charging speeds, it's often desirable to site a rapid-charging station near activities making the charging time pleasant (a shop, kiosk, seating area), since actual charge time may exceed the theoretical 10–20 minutes and be more comparable to fast-charger durations.
- Cost: a rapid charger (possibly 2 outlets) at max 150 kW costs **650,000–750,000 DKK** (including groundworks and connection fee), **2020 price**, same source.
- Photo examples: rapid charger at Q8, Viborg (photos: Q8 Danmark A/S); rapid-charging station from Clever (Clever Denmark & Cobe press photo).
- A rapid-charging station can generate traffic that otherwise wouldn't visit the area — should be sited with care where extra traffic is acceptable from an urban-planning perspective. A municipality might choose to site a rapid charger in a dense city center to support local trade (shoppers choose to charge downtown instead of along an arterial road); the short charge time limits waiting time downtown, suiting shorter visits, whereas 30–60-minute visits are better served by a fast charger.

**Figure 3.6 (referenced):** overview comparing charger types by typical charge time, siting location, and price — described as a rough categorization for expected 2030 charge times; notes that as of 2022, few EVs can charge from 20% to 80% in just 10–20 minutes on a rapid charger.

### 3.3 Private/Publicly Accessible Charging Infrastructure
Per **AFI-lovens § 2, pkt. 9**, a publicly accessible charging point or filling station is defined as: "A charging point or filling station supplying an alternative fuel that provides non-discriminatory access for users. Non-discriminatory access may include different terms for approval, use, and payment."

Not all charging infrastructure is publicly accessible, yet still helps meet charging needs; conversely, publicly accessible infrastructure isn't necessarily installed by public bodies. Charging needs can be met by:
- Private charging stations at private residential parking (private-initiative regulated)
- Publicly accessible charging stations on public land at existing administration buildings, hospitals, schools, sports/culture facilities, care homes, along public urban roads etc. (partly regulated by Ladestanderbekendtgørelsen and a public initiative)
- Publicly accessible charging stations on private parking at existing multi-story residential buildings, shopping centers, larger companies etc. (partly regulated by Ladestanderbekendtgørelsen and a private initiative)
- Publicly accessible charging stations at private (commercial) charging stations along the road network, e.g., at filling/energy stations and rest areas along the primary road network (regulated by the private market)

Publicly accessible charging infrastructure is broadly recognized as a precondition for the EV transition — consumers must be able to confidently invest in an EV without risk of being unable to get around (all of) Denmark. Given the small EV share of the fleet in 2022, charging demand doesn't yet support broad infrastructure rollout without public support (planning, tendering municipal land, and possibly financial support).

**Home charging statistics:** per the **Transportvaneundersøgelsen** (Danish National Travel Survey), **68%** of Danish households can park on their own land, often meaning they can install a home charge box. Since most people can drive between work and leisure activities on one charge (**250–500 km**), **2/3 of Danes** are not expected to need publicly accessible charging infrastructure in daily life (source: Transportvaneundersøgelsen, cited in "Sådan skaber Danmark grøn infrastruktur til én million elbiler," DEA and DTU, November 2019). Large variation between municipalities (see section 5.3).

### 3.4 Ladedestinationer (Charging Destinations)
Society has an interest in ensuring an even grid load across the day/night cycle, avoiding peak loads. With current technology, it's easiest/cheapest to handle if as many as possible charge on normal chargers (low power) at varying times, reducing simultaneity.

If many charge on fast/rapid chargers typically on the way home from work, charging infrastructure's peak grid load would coincide with households' rising electricity use for cooking, laundry etc. between **17:00–20:00** (the so-called "kogespidsen"/cooking peak). Illustrated in **Figur 3.7** (source: Dansk Energi, 2019, "Elbilerne kommer – gør elnettet klart til elbilerne," p. 7) — a principle illustration of expected 2030 grid load. To avoid too many citizens waiting long for a free charger, extra chargers would be needed, which would then sit largely unused the rest of the day/night. There's thus a societal interest in as many citizens as possible charging at home, and where not possible, at the workplace — in both cases outside the "kogespidsen."

Not everyone will be able to charge on normal chargers in future — some without home charging options won't have access to a normal charger near home or work either; some EV users may prefer a fast charger while shopping or a rapid charger on the commute. A combination of normal, fast, and rapid chargers is needed to meet varying needs/preferences while minimizing necessary grid investment.

#### 3.4.1 Ladning hjemme (Home Charging)
Usually normal chargers, since dwell time at home is typically long (e.g., overnight); also the cheapest charger type to install. Large geographic variation between and within municipalities in home-charging options (see section 5.3).
- For those parking on their own land, installing a home charge box is usually not a major problem; they'll rarely need publicly accessible charging, mainly on long trips (leisure or long-distance commuting). No special municipal action needed for this group beyond supporting grid expansion; possibly information/campaign measures.
- For those parking on shared parking (e.g., housing organizations), more challenges arise, since individuals can't unilaterally decide what's installed on shared land; often too few parking spaces exist, making it hard to convert a parking space into a charging space via tenant democracy. Municipalities can play a facilitating role, supporting work within housing organizations already underway elsewhere, sharing experience to address skepticism.
- In urban areas with many residences and significant street parking (typically city centers), normal chargers on publicly accessible parking can help meet resident charging needs — used by commuters, tourists, and shoppers with other reasons to be in the area during the day, and by residents at night.

#### 3.4.2 Destinationsladning (Destination Charging)
Best placed at the destination so the EV driver doesn't experience wasted waiting time. "Destination" is broadly understood — any daily stop can in principle be a destination.
- **Workplace/study:** average parking duration **6:51 hours** (source: Transportvaneundersøgelsen), allowing a long charge. Companies are important to a coherent charging infrastructure buildout — many are covered by Ladestanderbekendtgørelsen and must install at least 1 charging station; beneficial if companies install multiple chargers to spread charging load across low-grid-pressure daytime hours; municipalities can facilitate dialogue/cooperation with companies (see sections 6, 8.1.4).
- **Retail/shopping:** average shopping trip is **38 minutes** (source: Transportvaneundersøgelsen). Charger type should suit the destination's character — an hour-long shopping trip with a café visit suits a normal charger; a quick discount-store trip (20–30 min) better suits a fast charger.
- **Leisure activities** (sports, evening classes, scouts, cinema, café, restaurant, church etc.): relatively long parking duration, averaging **2:09–2:43 hours** across categories per Transportvaneundersøgelsen — may also justify installing chargers, depending on typical duration.

#### 3.4.3 Ladning på farten (On-the-Go Charging)
Needed for long trips (over ~200 km/day) — weekends, holidays, family visits, conferences, meetings etc. Most relevant along the motorway network and primary road network; a small number of commuters and traveling salespeople also need this. Primarily **range-extending rapid chargers**.
- Many business users may need on-the-go charging (e.g., a craftsman needing to charge during the workday, choosing a rapid charger to minimize wasted time; taxi companies similarly need to avoid lost earnings). A trend of taxi-company associations jointly financing a shared private rapid-charging station dedicated to taxis, avoiding queuing (source: FDEL 2021, https://fdel.dk/taxi-selskaberne-tager-sagen-i-egen-haand/). With zero-emission requirements in larger cities, business demand for fast/rapid charging can rise sharply (source: agreement between the government, Socialistisk Folkeparti, Radikale Venstre and Enhedslisten on "Miljøinitiativer i grønne byer og en hovedstad i udvikling," 14 September 2021).

### 3.5 Charging Speeds and Charging Profiles
Only briefly and under optimal conditions can an EV battery accept power at the charger's rated speed. Actual charge speed depends on:
- **Battery size and BMS (Battery Management System)** — larger battery = longer charge time, but also longer range/potentially less frequent charging
- **State of Charge (SOC)** — many (including new) EVs in 2021–2022 can accept **max 50 kW**, meaning they can't benefit from higher-power chargers like rapid chargers, occupying a rapid charger for relatively long — risking long waits for business vehicles needing fast charging
- **Battery/ambient temperature**
- **Number of charging outlets in simultaneous use**

**Battery State of Charge and charging profile:** charging profiles vary significantly by make/model and can change over time. **Figur 3.8** (source: "P3 Charging Index: Comparison of the fast charging capability of various electric vehicles," M. Hackmann, C. Gehring, C. Daake) compares mid-class EV rapid-charging profiles — e.g., a **Tesla Model 3** starts at **250 kW** but drops to around **50 kW at 80% charge**, while a **Mercedes-Benz EQA250** doesn't drop much through the charging period. Charging power is typically highest between **20–80% SOC**, then drops sharply — the last 20% is time-consuming to fill. Charging operators therefore have an interest in ending sessions at 80%; **in Norway**, operators combine kWh price with per-minute pricing while the EV occupies the charger, to incentivize quicker vehicle removal.

Lithium batteries are best kept between 20–80% (neither fully charged nor fully depleted), which is expected to normalize "sjatladning" (partial/top-up charging) at publicly accessible stations — drivers charge only as long as their parking stop naturally allows, then continue to the next natural stop for another top-up. Future charging patterns are expected to significantly affect how many charging stations are needed where.

**Temperature effects:** EV batteries work optimally at internal temperatures of **25–40°C**; higher/lower temperatures reduce range (battery can't efficiently discharge to the motor) and extend charge time (battery can't efficiently accept charge). Most newer EVs can pre-heat/cool the battery to address this. High-power charging challenges are greatest; not much difference observed for home normal charging. High-power charging is best done with a battery already warm from driving; cold/hot weather doesn't immediately damage the battery, but the BMS software reduces charging power to protect it — potentially causing longer waits at high-power chargers especially in Danish winters, and at rapid chargers in urban settings where the vehicle typically hasn't driven far/warmed up before charging (motorway-network charging is not expected to face this issue as much).

**Simultaneous outlet use:** affects charging power/time via **load management** — sharing available power (kW) among outlets, reducing the extra-ampere requirement and thus grid-connection investment cost. Useful e.g. for residential load management where cars park for long overnight periods without needing to charge within a few hours and can accept shared power (see section 12.4). Conversely, at high-power charging locations, it's undesirable for the EV driver not to be able to count on the rated power — e.g., if 300 kW is expected to be shared across 6 outlets all in simultaneous use, each EV gets only 50 kW, extending a 10–20-minute charge to potentially an hour — unsustainable for the EV driver and causing significant wasted time. Municipalities can address this on municipal land by requiring, in a tender, that EV drivers can expect to receive the stated power rating at high-power chargers (see section 10).

## Section 4: Overall Approach to Planning and Establishing Charging Infrastructure
A 7-step process (Figur 4.1), summarized/expanded in sections 5–11:
1. **(Section 5)** Strategic level: review municipal goals/plans/visions to set the right ambition level; consider municipal-specific conditions and how many citizens may depend on publicly accessible infrastructure (affects commercial attractiveness for operators)
2. **(Section 6)** Track how much charging infrastructure other actors are expected to install; early dialogue can support/accelerate their rollout; input can feed into demand calculations
3. **(Section 7)** Calculate total demand for publicly accessible charging infrastructure, based on total EV electricity need, then calculate the required number of each charger type
4. **(Section 8)** Map existing/planned charging infrastructure to identify unmet ("gap") demand and where the municipality may need a role — subtract existing/planned stations, mandatory Ladestanderbekendtgørelsen stations (if made public), and stations expected from other actors (housing organizations, companies/workplaces, retail, filling/energy stations, state, regions)
5. **(Section 9)** With municipal land identified, build a phased rollout plan, divided into pools/bundles for competition and consumer choice; consider the upcoming tender design in parallel
6. **(Section 10)** Prepare tender material — overall design, covered locations, contract timeframe requirements, groundworks, signage, layout/aesthetics, maintenance, consumer pricing, usage-monitoring data, and technical specifications
7. **(Section 11)** At the specific location, consider precise charger placement to avoid inconvenience or traffic-safety risk; decide parking restrictions and signage

## Section 5: Municipal Conditions Affecting Rollout Terms

### 5.1 Municipal Plans, Visions, and Goals
Recommended to review the municipality's planning strategy, kommuneplan, climate plans (including **DK2020**), and traffic/mobility plans for relevant targets (green mobility, CO2 reduction etc.), ensuring coherence across plans. A charging-infrastructure strategy supporting already-adopted plans can help secure broad political backing. Other planning/regulation (e.g., municipal parking strategy, parking executive orders) can affect charging-infrastructure design. The grid must expand drastically in coming years to keep pace with broader electrification (not just transport) — private and business (including fleets and heavy transport) EV charging must be integrated into the municipality's overall energy planning. A municipal street-furniture design manual may affect tendered infrastructure design (e.g., color, municipal crest).

### 5.2 The Municipality's Different Functions (Figur 5.1 — reproduced in full)

| Function | Scope of action |
|---|---|
| **Bygherre og bygningsejer** (Developer and building owner) — when building new or renovating existing buildings, or owning buildings covered by Ladestanderbekendtgørelsen | Obliged to follow Ladestanderbekendtgørelsen's requirements (section 2.1) — install charging stations at required municipal buildings |
| **Myndighed** (Authority) — developing kommuneplan/lokalplan; issuing building permits; granting the right to be a charging operator on municipal land; administering parking rules | Must provide the planning basis for (rapid) charging stations requiring a lokalplan; can designate areas in the kommuneplan suited to (rapid) charging stations. As building authority, must ensure Ladestanderbekendtgørelsen compliance for new construction/major renovation. When tendering municipal land, must award the operator right on market terms. Administers parking rules and can install signage restricting parking to EVs, with time limits |
| **Driver af den grønne omstilling** (Driver of the green transition) — ensuring sufficient charging infrastructure in areas of limited commercial interest; ensuring equal EV access regardless of housing type; other supportive measures | Can map commercial interest and allocate co-financing funds. Can map areas where many citizens lack home-charging options and engage housing organizations/companies about installing chargers on their parking. Can facilitate e.g. taxi companies jointly financing a dedicated (non-public) rapid-charging station; can favor zero-emission vehicles physically (dedicated parking, green lanes etc.) |
| **Arbejdsgiver** (Employer) — enabling employee EV charging at the workplace | Can ensure publicly accessible charging stations at municipal workplaces not covered by Ladestanderbekendtgørelsen requirements — requires an agreement with a charging operator |
| **Flådeejer** (Fleet owner) — transitioning the municipal vehicle fleet from petrol/diesel to electric | Can initiate replacement of the municipality's own fossil vehicles with electric alternatives |
| **Indkøber/bestiller** (Purchaser/orderer) — public-transport tenders; supplier requirements (e.g. emission-free vehicles) | Can require future public-transport suppliers to use zero-emission buses (e.g. electric buses), possibly jointly with other municipalities via purchasing partnerships. Can adopt procurement-policy weighting favoring suppliers using zero-emission vehicles for deliveries, cleaning contracts, taxi services; municipalities are often part of waste-collection company boards and can influence future collection vehicles' emission-free fuel choice |

### 5.3 Municipal Geography and Structure
Large geographic/urban-structure differences between municipalities affect rollout conditions. How many EV drivers need publicly accessible charging is partly determined by how many can install a charger on their own land.

**Figur 5.2** (Table: Rambøll, based on "Sådan skaber Danmark grøn infrastruktur til én million elbiler," DEA and DTU; source data: Transportvaneundersøgelsen) — average distribution across parking conditions in Denmark and in two illustrative municipalities:

| | Parking on own land | Parking on shared lot near property | Street parking |
|---|---|---|---|
| **Denmark (average)** | 68% | 20% | 12% |
| **Frederiksberg Kommune** | 11% | 39% | 50% |
| **Jammerbugt Kommune** | 95% | 2% | 3% |

Frederiksberg and Jammerbugt are cited as two municipalities with respectively the fewest and most residents able to park on their own land. The Transportvaneundersøgelsen can be used at a rough municipal level, but more detailed (zone-level) analysis is recommended to pinpoint areas of greater need — data is structured per the **Landstrafikmodellens** zone structure, noting individual zones may have limited respondent counts, so multi-year data extraction may be needed (housing form/parking conditions are assessed to change only slowly over ~10 years, though local knowledge can flag zones with major change e.g. from urban renewal). Footnote reference: DTU 2020, "Bilejerskab og -brug, belyst gennem TU-data."

### 5.4 Commercial Interest for the Municipality
Commercial interest in installing charging stations varies by municipality, materially affecting the municipality's scope for action. **As of January 2022, approximately 5%** of the Danish vehicle fleet was electric (BEV + PHEV) — a limited market for operators in many areas, where usage of publicly accessible chargers is expected to remain limited over the next 2–5 years, though the market is growing fast. Key commercial factor: expected utilization rate (share of the day/night a charging station is used) — e.g., a downtown station usable by residents at night and company employees by day can be in use much of the day/night, improving profitability; visibility and branding value can also matter.

Currently (2022), Danish charging infrastructure is concentrated in larger cities and along the primary road network, where operating a charging station is most viable commercially; in outlying areas there's limited commercial interest given the often non-viable market — though seasonal tourism can substantially increase summer demand in these municipalities. AFI-loven allows municipal co-financing where the market alone is insufficient (section 2.2), but this requires demonstrating co-financing need (a negative price in the tender/market dialogue); funds cannot be earmarked to specific tenders in advance.

## Section 6: Municipalities' Role in Charging Infrastructure Rollout

### 6.1 Summary of the Municipality's Role
Given the many actors involved, a coordinating party is needed — municipalities are well-suited to this role, which becomes broader than merely installing chargers on municipal land (Figur 6.1, reproduced):
- Create an overview, plan, coordinate, and ensure charging infrastructure quantity matches demand (requires demand calculation plus ongoing monitoring — sections 7 and 10.5.8)
- Support installation where gaps or insufficient infrastructure exist (co-finance installation on municipal land lacking commercial interest; seek state pool co-financing)
- Guide/help companies and housing associations that often need and request assistance (facilitate cooperation between them, possibly joint tenders)
- Create dialogue/cooperation with the grid company on grid-expansion prioritization/planning

### 6.2 Actors Installing Charging Infrastructure
**Figur 6.2 (reproduced in full)** — typical charger type, location, and actor ensuring installation:

| Charger type | Location | Actor ensuring installation |
|---|---|---|
| Normalladere (≤22 kWh) | Residences with own-land parking | Landowner |
| | Residences with shared private parking | Housing organization/department; homeowners' association |
| | Private company parking (incl. those under Ladestanderbekendtgørelsen) | The company |
| | Municipal land and road land, e.g. at buildings required under Ladestanderbekendtgørelsen, or typical longer-duration parking with public charging need | The municipality |
| | Regional land, e.g. required locations and longer-duration parking | The region |
| | State land and road land, similar cases | The state |
| Hurtigladere (50–100 kWh) | Retail parking | The retailer |
| | Municipal land/road land, e.g. downtown to support trade | The municipality |
| | Regional land, e.g. at regional buildings for varied target groups | The region |
| | State land/road land, e.g. at state buildings and rest areas for varied target groups | The state |
| Lynladere (≥150 kWh) | Filling stations | The filling station |
| | Private land, e.g. fast-food restaurants near the primary road network | Other charging operators |
| | Municipal land/road land, typically along the primary road network | The municipality |
| | State land/road land, e.g. state rest areas where stopping drivers need to move on quickly | The state |

**Case: Roskilde's facilitation of partnerships and joint tenders (Figur 6.3).** In collaboration with private company **ParkPrivate**, Roskilde mapped in **2021** which downtown businesses were interested in joining shared charging infrastructure. ParkPrivate approached businesses offering to solicit quotes from a number of charging operators, on terms that chargers would be reserved for employees during work hours and publicly accessible afterward. **15 businesses** were interested; ParkPrivate ran a joint tender for installation/operation, with participation optional after the quote round. Tender required the landowner to pay for groundworks/connection fee, chargers of at least 22 kW, public accessibility after work hours, and a shared platform. ParkPrivate has since extended the service to housing organizations.

**Case: Albertslund Kommune's cooperation with housing/homeowners' associations (Figur 6.4).** An ad hoc group of representatives from housing/homeowners' associations, together with the municipal administration, developed a charging-station plan, a background note on future charging need, and guidance/guidelines for installation and administration of charging infrastructure — focused primarily on shared-parking residential areas. Several ad hoc group members came from Albertslund's **Brugergruppen**, a body of representatives from around **75** residential areas that has met quarterly since the 1980s, covering utility areas (water, wastewater, waste, outdoor lighting, and charging infrastructure), with the ability to submit proposals to municipal politicians. Typical association considerations: charger placement, public accessibility, choice of operator, and other usage regulation (queue systems, time-limited parking). Albertslund has particularly encountered difficulty reaching consensus on shared cost contributions in landowner/homeowner associations, and has experience establishing "carport- eller ladestander-laug" (carport/charging cooperatives) to limit costs to actual users. Example: **Ejerforeningen Lange Eng** (~100 owner-occupied homes) established a charging cooperative and installed **4 charging stations** via operator **Sperto**, securing a lower price for members. The general housing association **Hedemarken** is pursuing a different approach — combining charging stations in a hybrid installation with new solar panels and batteries, so residents can also cover much of their private electricity use.

Currently (2019–2022) particularly strong growth is seen in **rapid chargers**, mostly along the primary road network including the state road network; several filling-station chains have announced plans to add rapid chargers at many existing sites, expected to meet much of the on-the-go charging need (e.g., for commuters and business vehicles). In many cases, municipalities won't need to tender municipal land for high-power charging, since the private market largely ensures sufficient rapid chargers on private land — though some areas of Denmark likely won't have enough EV drivers needing publicly accessible charging to support a commercially viable rapid-charging station.

### 6.3 Cooperation with Electricity Grid Companies
Grid companies (elnetselskaber) are, per the **Elforsyningsloven**, obliged to operate, maintain, and as needed expand the distribution grid within their monopoly concession area, and are subject to connection obligations for new consumption and new production.

The **Energistyrelsen's** projections indicate rising electricity consumption for years to come, with already-increasing demand from transport, home heating, and industry. Society's rising power needs from increased electrification (including EV charging infrastructure) will, over time, increase demand nationally, regionally, and locally to the point of exceeding existing regional/local grid capacity, requiring grid expansion. Grid expansion (transmission and distribution level) should occur where most societally cost-effective, at the right place and time — requiring good visibility into future activities.

**Figur 6.5** describes Denmark's grid structure: the **transmission grid** (100 kV and above, "the electricity motorways") is operated by **Energinet**; the **distribution grid** (below 100 kV, "the local/access roads for electricity") is handled by the grid companies.

Currently (per the handbook, 2022) no overall national capacity challenges exist for the 0–2-year horizon, though local challenges can arise now or soon; medium/longer term (3–5, 6–10 years and beyond) ongoing grid expansion at all voltage levels will be needed.

**Connecting charging stations to the grid (Figur 6.6, source: Fællesregulativet, Green Power Denmark):** local grid companies must connect customers within their supply area (against a connection fee), regardless of customer type. A single ampere costs approximately **1,000–1,500 DKK incl. VAT (2022 price)**. A 22 kW charging station requires **32 amperes**; if not already available, a new grid connection is needed. The electrical installer must follow the grid company's registration procedures before installation work begins; the customer indicates its power need/consumption pattern, receives feedback on connection options, and only once the contractor submits a formal connection request does the grid company issue an offer and timeline.

#### 6.3.1 Power Need and Flexibility
Power need is determined by charger type(s), number of chargers, and expected simultaneity of use (risk that several/all EVs need charging at once). Higher simultaneity means a much larger, but often narrowly time-windowed, power need — raising grid connection cost and reducing 24-hour utilization of that connection. To address simultaneity challenges, more flexible/controlled charging (e.g., via a **Load Management System, LMS/lastbalancering** — see section 12.4) can shift charging away from the "kogespid" (17:00–20:00) to late evening/night when grid capacity is more available, deferring or avoiding capacity-expansion investment (a societal-economic advantage). Flexible charging isn't always possible/desirable, requiring planning for full power need in those cases.

#### 6.3.2 Recommendations for Cooperation and Dialogue with Grid Companies
Municipalities and grid companies need ongoing dialogue on expectations for local electrical infrastructure's future role. Grid companies can't expand capacity everywhere at once (material and labor constraints, and it may not be societally optimal since demand may not materialize everywhere despite projections) — they must prioritize which substations/areas to upgrade first. This prioritization becomes easier with ongoing dialogue and insight into municipal transport-sector plans (EV charging infrastructure, electric public transport, electric ferries etc.) and other sectors' needs.

In dense city centers, limited space often means hard prioritization; more EV chargers may require new local transformer stations, which take up physical space, sometimes requiring removal of parking spaces — transformer stations are a precondition for local charging-station establishment. More extensive grid expansion may also require the grid company to work/install new equipment further from the charging facility, if the connection requires larger upstream grid expansion. Detailed dialogue with the grid company can yield special agreements on integrating transformer stations into the streetscape (final placement, visual appearance, access roads, screening planting etc.).

Recommended: the municipality designate one or more fixed internal contact persons for grid-company liaison, to create a clear communication channel and build mutual understanding of needs/workflows. **Figur 6.6** photo: transformer station in Aalborg (Rambøll photo).

## Section 7: Calculating Charging Infrastructure Demand

### 7.1 Factors Affecting the Speed of Fleet Transition
Drivers/barriers (Figur 7.1, examples of factors affecting consumer vehicle choice, reproduced): which EVs are on the market; purchase price and financing options; spare-parts prices; fuel/energy prices; range, size, towing, and power needs; charging speed vs. refueling speed; individual preference for appearance/model/brand; climate/environmental impact; trust, experience, and habits.

#### 7.1.1 EU Legislation and Danish Taxes
EU-wide CO2 requirements on car manufacturers' average new-car emissions push manufacturer sales toward roughly **2/3 green vehicles** to meet the average-emissions target (source: FDM 2020), driving rapid EV market growth. EU directives led to Denmark's Ladestanderbekendtgørelsen. The **"Grøn omstilling af vejtransporten"** agreement (December 2020) restructured tax rules and extended a reduced electricity-tax scheme for EVs, lowering consumer EV prices alongside falling technology costs and rising demand.

#### 7.1.2 Charging Infrastructure Buildout
Lack of charging infrastructure is a major transition barrier (range anxiety); current battery technology gives EVs a typical range of **250–500 km**, underscoring the importance of well-functioning, relatively fine-grained, publicly accessible charging infrastructure, especially given conventional vehicles' longer range and fast, widespread refueling network.

#### 7.1.3 Consumer Psychology
Range anxiety is a psychological barrier even though most people's daily driving fits comfortably within EV range; the few long trips are the actual source of worry. "Sjatladning" (topping up opportunistically) means dwell time, not battery emptiness, typically defines charging behavior. As range anxiety decreases (e.g., with more rapid-charging stations along motorways) and as friends/acquaintances' good EV experiences spread ("naboeffekten"/neighbor effect), charging behavior and adoption are expected to accelerate.

### 7.2 Projecting Charging Infrastructure Demand — 6-Step Calculation Method (Figur 7.2)
A worked example ("Kommunen," a fictional municipality) runs through all six steps:

**STEP 1 — Current and future vehicle count in the municipality.** Uses Danmarks Statistik (statistikbanken, table BIL710) for municipal-level vehicle counts by household/business, fuel, and year. Since 2000, the Danish vehicle fleet has grown **46%** (Skatteministeriet 2021). Expected to grow from **2.72 million vehicles (2020)** to **3.26 million vehicles (2030)** — a **24%** increase (Energistyrelsens Klimafremskrivning 2021). As of **17 February 2022**, total chargeable vehicles (BEV + PHEV) nationally: **150,557** (FDM), ~5–6% of the fleet (70,550 BEV, 80,007 PHEV).
- *Worked example:* "Kommunen" currently has 10,000 household/business vehicles; assumed to grow 24% to 12,400 by 2030, mirroring the national trend, absent specific local measures expected to change this.

**STEP 2 — National EV scenarios for the future.** Three illustrative scenarios (Figur 7.4, reproduced) for 2030, with EV share of a 2.7M and a 3.35M-vehicle fleet:

| Scenario source | EVs in 2030 | Share of 2.7M fleet | Share of 3.35M fleet |
|---|---|---|---|
| "Grøn omstilling af vejtransporten" agreement (gov't, Radikale Venstre, SF, Enhedslisten), published 4 December 2020 | 775,000 | 29% | 23% |
| Prior government statement, developed in Dansk Elbilalliance/DTU's "Sådan skaber Danmark grøn infrastruktur til én million elbiler," November 2019 | 1,000,000 | 37% | 30% |
| Klimarådet's recommendations, "Kendte veje og nye spor til 70 procents reduktion," March 2020 | 1,500,000 | 55% | 45% |

*Worked example:* Kommunen works with all three scenarios for 2030.

**STEP 3 — Number of EVs in the municipality under each scenario.** Applies each scenario's national EV share to the municipality's projected fleet.
*Worked example:* 12,400 × 0.23 = 2,852 EVs (775k scenario); 12,400 × 0.30 = 3,720 EVs (1M scenario); 12,400 × 0.45 = 5,580 EVs (1.5M scenario). Kommunen chooses to plan for the **1.5M scenario (5,580 EVs)**, aligning with its 2030 CO2-neutrality ambition.

**STEP 4 — Electricity needed to charge the municipality's EVs.** Formula: (average km driven per day / km driven per kWh) × number of EVs. Per Transportvaneundersøgelsen, a privately owned car drives **45.5 km/day** national average (range: **21.5 km (Ærø)** to **56.5 km (Holbæk Kommune)**). Average EV efficiency assumed **5 km/kWh** (based on DEA/DTU's report, supported by an FDM test/analysis).
*Worked example:* Kommunen assumes 50 km/day average and 5 km/kWh: 50/5 × 5,580 = **55,800 kWh** total daily EV energy need.

**STEP 5 — Share of electricity needed from publicly accessible infrastructure.** Excludes those expected to charge at home (most who can, will, being cheapest/most convenient) — these are assumed to rarely need publicly accessible charging except on long trips (usually via rapid chargers, excluded from this calculation).
*Worked example:* Kommunen: 60% park on own land, 25% on shared lots, 15% on the street — 40% cannot simply install a home charge box. Public charging need: 55,800 kWh × 40% = **22,320 kWh/day**.

**STEP 6 — Number of each charger type needed.** Assumes charging stations aren't in use 100% of the time; per DEA/DTU's report, a charging station is assumed in use **30% of the day/night** on average. Assumed deliverable power per outlet: normal charger **11 kW** (some places 15 kW), fast charger **50 kW**, rapid charger **150 kW** (though up to 350 kW rapid chargers exist, few current EVs can accept that much). Daily kWh deliverable per outlet:
- Normal charger: 24h × 30% × 11 kW = **79.2 kWh/day**
- Fast charger: 24h × 30% × 50 kW = **360 kWh/day**
- Rapid charger: 24h × 30% × 150 kW = **1,080 kWh/day**

**Distribution across charger types:** to best spread grid load, multiple sources (Dansk Energi, DTU) recommend normal chargers deliver most needed power. National average per DEA/DTU's "Sådan skaber Danmark grøn infrastruktur til én million elbiler" (scenario 2): **85% normal, 10% fast, 5% rapid** — a national average including power for EV owners with own-land parking, and described as an expression that most power should ideally come from normal chargers rather than an exact calculation. Given 2021–2022 market trends toward more rapid than fast chargers (fast chargers seen mainly at retail), the handbook suggests an adjustment: **85% normal, 5% fast, 10% rapid**.

*Worked example continued:* Kommunen has fewer own-land parkers than the national average (60% vs. 68% national), so 25% more of Kommunen's EV owners lack own-land parking than nationally ((40−32)/40 = 25%) — Kommunen assumes 25% more power should come from fast/rapid chargers, adjusting: **normalladere 81%** (1 − 0.06 − 0.13), **hurtigladere 6%** (0.05 × 1.25), **lynladere 13%** (0.10 × 1.25).

Further adjustment: subtract power going to private normal chargers installed by own-land owners (60% of Kommunen's EVs), since these are assumed to charge almost exclusively at home. Recalculated distribution for the remaining (non-own-land) population: **normalladere 53%** ((81−60)/(21+6+13) = 21/40), **hurtigladere 16%** (6/40), **lynladere 31%** (13/40).

**Final calculation:** kWh needed per charger type for Kommunen's EV owners without own-land parking (2030): normalladere 53% × 22,320 = **11,830 kWh**; hurtigladere 16% × 22,320 = **3,571 kWh**; lynladere 31% × 22,320 = **6,919 kWh**. Number of outlets needed: normalladere 11,830/79.2 = **149**; hurtigladere 3,571/360 = **10**; lynladere 6,919/1,080 = **7**.

Explicitly noted this is **not a mandate to install exactly this many stations**, but an indication of the order of magnitude of demand — part may be covered by mandatory Ladestanderbekendtgørelsen stations at municipal buildings (depending on siting), and forms a basis for subsequent dialogue with housing organizations, companies, and operators/filling stations (sections 6.2, 8.1.3–8.1.5).

### 7.3 Commuters' Charging Infrastructure Need
Not recommended for municipalities to broadly install charging infrastructure specifically targeting commuters — if neighboring municipalities each count in-commuters' needs, demand gets double-counted (in both home and work municipality), overestimating need in both. Few need to charge en route to/from work given typical commute distances; alternatives if home charging isn't possible: normal chargers in the city center (usable at night by residents lacking own parking, and by day by commuters, raising utilization from e.g. 30% to 60%, improving profitability); company-installed normal chargers; fast/rapid chargers on primary roads (e.g., at filling stations); charging infrastructure in the commuter's home municipality. For these reasons, the handbook does not recommend explicitly calculating for commuter demand or over-installing urban infrastructure to meet it.

### 7.4 Tourists' Charging Infrastructure Need
Many long trips are leisure trips (family/friend visits) and tourism (including day-trippers). Municipalities with heavy tourism can face particular charging-infrastructure challenges since demand is highly seasonal and often insufficient to ensure a viable business for the operator — potentially requiring municipal co-financing (sections 2.2, 5.4) or state pool support.

**Tourists in larger urban areas** can often be served by existing infrastructure similar to commuters, since tourist charging timing differs from locals' typical patterns (different daily rhythm on holiday) — via downtown normal chargers, fast/rapid chargers along arterial/primary roads (e.g. filling stations), charging at holiday accommodation (if installed by the owner), charging in a neighboring municipality (if the holiday area borders one with nearby infrastructure), charging at tourist attractions, or charging while grocery shopping. Dialogue with tourism organizations/attractions can identify specific locations warranting extra charging stations.

**Tourists in coastal/nature areas:** particular challenges given local grid capacity in holiday-home areas often not dimensioned for EV charging load — argues for prioritizing more rapid-charging stations along primary roads in these areas instead, potentially reducing (or at least delaying) individual holiday-home owners' incentive to install a home charge box until the grid can handle the load. Given the seasonal usage pattern, commercial interest in such rapid chargers may not be large. Municipalities can benefit from partnerships with grid companies and local tourism businesses to build shared understanding of opportunities/challenges.

## Section 8: Siting Charging Infrastructure at Municipal and Area Level

**Summary (Figur 8.1):**
1. Map existing and planned charging stations
2. Map where charging stations must go at municipal buildings per Ladestanderbekendtgørelsen
3. Estimate how much charging infrastructure housing organizations/companies are expected to install by the projection year, possibly via dialogue/mapping
4. Map retail and filling/energy-station locations expected to install fast/rapid chargers
5. Map local-area unmet demand and designate suitable municipal land within those areas
6. Designate any other locations where the municipality wants additional charging stations (branding, visitor/tourist needs)
7. As part of initial location screening, map existing supply lines/utility ducting to reduce relocation needs

Recommended to think as long-term as possible when designating locations, to avoid costly future relocations.

### 8.1 Mapping Other Actors' Charging Infrastructure

#### 8.1.1 Existing and Planned Charging Stations
Portals like **plugshare.com** (user-reported chargers) and **elbilviden.dk** (operator-submitted data) give an overview, with filters (e.g., showing only high-power chargers). Also map any planned/permitted charging stations, often issued by the road authority for municipal parking lots (e.g., per Vejlovens § 80) — permits under this section had to be issued **before 6 April 2022**, when the legal basis for this permit type lapsed. Recommends factoring in bus, truck, and van charging infrastructure and possibly e-bikes; recommends sharing all existing/expected transport-sector charging infrastructure information with the local grid company as early as possible. **Figur 8.2**: screenshot from plugshare.com showing Odense's publicly accessible chargers filtered to Type 2/CCS.

#### 8.1.2 Charging Stations at Municipal Buildings per Ladestanderbekendtgørelsen
Assess whether these (mainly normal chargers) can be made publicly accessible, reducing overall municipal demand count — though they'll be scattered across the municipality's geography and not necessarily near concentrations of citizens dependent on public charging.

#### 8.1.3 Housing Organizations' Charging Stations
Assess/estimate how many housing organizations will have installed chargers by the projection year (mainly normal chargers); mapping housing-organization concentrations can reveal where this type of housing clusters; can be assessed via dialogue meetings or a simple survey. Some organizations treat charging as a competitive amenity to attract tenants and are further along; smaller organizations often find this resource-intensive and less advanced — municipalities can guide/facilitate.

#### 8.1.4 Companies' Charging Stations
Companies covered by Ladestanderbekendtgørelsen (non-residential buildings with >20 parking spaces) must install at least 1 charging station per building (SMEs exempt). CVR.dk gives an overview of company counts/addresses for mapping; surveys or direct contact can gather planning information. Some larger companies (and SMEs) are expected to install chargers as an employee service, reducing publicly accessible demand — mainly normal chargers for employees/visitors; company fleets may instead need fast/rapid charging. Can be cross-referenced with areas of high street-parking share — if company chargers become publicly accessible (even only after work hours), they can help meet area demand.

#### 8.1.5 Retail and Filling-Station Chargers
Many retail chains have begun installing chargers, expected to grow; fast chargers particularly suit retail given typical shopping-trip duration alignment. Some retail buildings fall under Ladestanderbekendtgørelsen (>20 spaces as non-residential property), requiring at least one station by 2025, not necessarily publicly accessible; publicly accessible retail chargers can help meet overall demand — many individual retail outlets qualify as SMEs depending on ownership/franchise structure. **Lidl** is cited as an example of a chain that announced (December 2020) plans to install chargers at all its stores. Filling-station chains are transitioning at varying paces, typically installing rapid chargers given their siting along the primary road network/major intersections with good access. **Figur 8.3**: **Q8** announced (December 2020) plans to install rapid chargers at all staffed filling stations through 2026, plus offering charging at other locations (photo: rapid chargers in Esbjerg, Q8 Danmark A/S). Note: current grid-connection rules do not permit businesses to share their delivery capacity (leveringsomfang) with others (see Tilslutningsbestemmelserne pkt. 3.4.6).

### 8.2 Differentiated Charging Infrastructure Need Across Urban Areas
With a combined overview of municipal and other actors' installations, gaps can be identified where the municipality might tender its own land or co-finance installation. GIS overlap analysis between municipal land and underserved areas can identify candidate parcels; precise stall-level designation is generally not recommended given operator/connection-distance considerations.

City centers often need publicly accessible infrastructure on municipally owned parking, given multi-story buildings without parking (residents park on the street) — often in older urban quarters with townhouses lacking own-land parking. Tourist-targeted infrastructure may also be needed (charging islands in holiday-home areas, fast chargers at retail/town centers, or rapid chargers along the primary road network, depending on local conditions). Not every area with unmet need has suitable municipal land — charging stations should be easily/conveniently reached without major detours, so dialogue with external parties/property owners (often businesses in commercial areas) may be needed.

**Rule of thumb table (Figur 8.4, explicitly NOT based on empirical usage data, since only a small EV fleet share exists as of 2022)** — based on a 1 million EV scenario (~30% of the projected 3.35M-vehicle 2030 fleet), assuming: **20%** of parked EVs will need to charge at the parking lot in smaller towns/suburbs with much own-land parking; **30%** in central larger towns/city centers with little own-land parking:

| Number of parking stalls | Smaller town/suburb — normal chargers (dual outlet) | Central larger town/city center — normal chargers (dual outlet) |
|---|---|---|
| 21–50 | 1–2 | 2–3 |
| 51–75 | 2–3 | 4–5 |
| 76–100 | 3 | 5–6 |
| 101–125 | 4 | 7–8 |
| >126 | ≥4 | ≥8 |

Adjustments: parking lots with typically short dwell times: **-20%**; parking lots with a large catchment area: **+20%**; parking lots serving many tourists: **+20%**.

Handicap-accessible parking charging needs should be factored in, per the handbook "Færdselsarealer for Alle – Universelt design og tilgængelighed," section 3.6. In city centers/short-dwell-time areas (e.g. a pedestrian street), a fast charger may be suitable to support local retail, weighed against relatively high installation cost and whether nearby fast chargers already exist/are planned (e.g. at supermarkets).

#### 8.2.1 Charging Stations for Tourism and Branding
Municipalities/tourism organizations may want additional charging stations to support other functions — e.g., near attractions to encourage extra visits/longer stays, or on prominent, visible municipal parking to brand the municipality as green, even if demand is otherwise met.

#### 8.2.2 Monitoring Development and Usage of Charging Stations
Given rapid 2021–2022 development, it's recommended to roll out infrastructure in phases, periodically reassessing whether the existing plan's scope remains current, to reduce risk of mis-investment (recognizing converting parking to charging spaces reduces spaces available to non-charging fossil and EV drivers alike). Demand can shift as charging patterns evolve — ongoing monitoring is recommended, and preparing for future stations (e.g., laying extra ducting during current groundworks) can avoid later extra costs if additional demand emerges.

### 8.3 Mapping Existing Supply Lines
Recommended to map existing supply/utility lines via **LER** (see Figur 8.5) in areas planned for charging infrastructure — while need should primarily drive siting, mapping utility lines can help find placements within the same area that reduce or avoid the need for line relocation.

**About LER (Ledningsejerregistret):** a nationwide register of Danish utility-line owners and their interest areas, aiming to reduce excavation damage to buried/seabed utility lines. Regulated by **Bekendtgørelse af lov om registrering af ledningsejere**, which sets out who must use LER; specific rules on releasing line information are set by other laws and voluntary standards.

## Section 9: Rollout of Charging Infrastructure

### 9.1 Ladestanderbekendtgørelsen as the Rollout Plan's Foundation
Municipalities must ensure a rollout meeting Ladestanderbekendtgørelsen's requirement of one charging station per existing non-residential building with more than 20 parking spaces by **1 January 2025** — this must be part of the rollout plan, alongside other locations the municipality wants to support (e.g., for geographic coverage).

The rollout plan's timeframe can be set to meet the Ladestanderbekendtgørelsen deadline, or to the demand-projection year (e.g. 2030, per section 7.2). Sufficient (possibly time-overdimensioned) infrastructure can encourage more EV purchases — arguing for setting the rollout plan's timeframe to 2025 while pre-emptively sizing infrastructure for expected 2030 demand.

Since municipalities cannot co-finance charging infrastructure after 2024 under AFI-loven (as of the 2022 legal status), locations planned after 2024 must be sufficiently commercially attractive that operators will bear all installation costs themselves.

Phased rollout can spread cost and installation work over a longer period, given the significant workload of installing 80–100 charging stations many municipalities face. Rollout order can weigh several factors:
1. Starting with the highest-demand locations makes sense for supporting fleet transition fastest; tender proceeds from the right-to-operate award can also help co-finance chargers at lower-value locations
2. If significant fast/rapid charging need exists due to seasonal tourism, the municipality may want to tender this relatively early to support tourism, possibly also generating rental income to co-finance chargers elsewhere
3. Ladestanderbekendtgørelsen-mandated stations often sit at locations meeting neither high charging demand nor operator attractiveness, but must still roll out by 1 January 2025
4. Chargers meeting other interests (visitor destinations, branding locations) should generally have the lowest rollout priority — but note the co-financing window closes in 2024 under current law

Timing/location can also be a political prioritization, where geographic balance may also matter.

**Figur 9.1** illustrates a rollout plan table format: property, address, property type, whether covered by Ladestanderbekendtgørelsen, number of dual-outlet normal chargers, and phased year (2023/2024/2026/2028) — example rows include Marienlyst Skole, Dagbjerg Børnehave, Bjergby Hal (all Ladestanderbekendtgørelsen-covered), and non-mandatory tourist-attraction locations (Skulpturpark, Slotsruin). Sample total: **63 stations** across phases of 27/18/10/7; construction sum per phase at **75,000 DKK per station (2020 price)**: 2.025M / 1.35M / 0.75M / 0.525M DKK.

### 9.2 The Rollout Plan's Relationship to the Tender
The municipality should think about the upcoming operator-right tender design in parallel with developing the rollout plan, if the installed stations are to be publicly accessible — recommended to consider tender design already during rollout-plan development.

Location attractiveness for operators is relevant — typically high expected utilization rate matters most, but visibility/branding value also matters; some operators may accept less-profitable locations for broader network coverage benefit. Where exactly on the parcel the station sits and local conditions there also matter greatly to operators (elaborated further in section 11.1.5). A prior market dialogue can help clarify how operators view the municipality's various areas.

**Two possible pooling approaches for the rollout plan:**
1. Pool commercially attractive locations with less-attractive ones, to secure a better price/terms on the combined pool
2. Pool only the attractive locations for best possible pricing, using the resulting surplus to fund installation at less-attractive locations — advantage: faster infrastructure rollout where demand is highest

Recommended to consider pool sizing to bring in more operators, broadening consumer choice and competition — a single rollout phase can consist of multiple pools; limits can be placed on how many pools a single operator can win, to ensure operator diversity. Pools should also mix across geography so local areas get a variety of operators, benefiting consumers and competition. Municipalities bear a responsibility for competition in the charging sector when supporting installation directly or indirectly, especially when tendering land beyond the strict Ladestanderbekendtgørelsen requirements (i.e., acting beyond its building-owner obligations).

## Section 10: Tendering Charging Infrastructure Locations

Since the rollout plan and tender are closely linked, it's recommended to develop them in parallel, possibly with prior market dialogue with charging operators, and to consider incorporating bus, truck, van, and e-bike charging infrastructure into the combined tender where possible.

### 10.1 Overall Tender Design
In some municipalities, property administration is split across departments (e.g., Health and Care administers care-center parking, School Department administers school parking) — may require authorizing a single department (e.g., Roads and Parks) to run a combined tender covering all municipal land needing/wanting charging stations. Centralizing in one department is recommended given the resource intensity of building expertise, a rollout plan, and tender materials — likely to achieve better terms/pricing if one department handles everything centrally.

Attractive locations are often not at municipal buildings (unless downtown) but on road land administered by the road authority — worth looking across Ladestanderbekendtgørelsen-mandated and demand-driven (non-mandatory) locations together, relevant to phase/pool sizing and composition (section 9).

**Joint tenders across municipalities** are also possible — the benefit of cross-municipal cooperation is combining one municipality's attractive locations with another's less-attractive ones in a joint pool; purchasing partnerships (indkøbsfællesskaber) offer a platform for knowledge/experience exchange, easing workload and freeing resources (footnote: Konkurrence- og Forbrugerstyrelsen 2017). Requires cross-municipal agreement on tender requirements/criteria, including political alignment on desired infrastructure quantity/type — can be time-consuming to achieve.

#### 10.1.1 Market Dialogue with Charging Operators
Prior dialogue on location interest can ease pool design for operator attractiveness. Experience shows such dialogue typically yields better tenders and lower transaction costs, but requires more time and willingness to accommodate operator input on tender design. The municipality should survey the operator market broadly at the time, as new operators with varying offerings/specialties continually enter.

### 10.2 Existing Municipal and Local Planning
Must check whether charging-infrastructure installation fits within existing kommuneplan/lokalplan, or requires dispensation or a new location. Normal chargers usually install without major issues, though a lokalplan might set color requirements etc. that should feed into the tender.

Fast/rapid chargers often involve larger installations that may not fit existing plans — requires assessing:
- Charger type (kW) and number of outlets
- Expected station traffic volume
- Access conditions from road/pedestrian areas (accessibility, traffic safety, reachability)
- Expected noise and any noise-sensitive neighboring use
- Whether the installation will be sufficiently lit without causing light nuisance
- Need for mitigation measures (e.g., noise barriers)
- Whether the installation needs covering/shelter
- Whether a kiosk, toilets, or similar amenities are needed
- Need for parking restrictions
- How EV drivers will find the station (signage/wayfinding)

### 10.3 Charging Stations at New Construction Between Tender Rounds
Municipalities are often developers of new non-residential buildings with more than 10 parking spaces, requiring at least one charging station and preparation for at least 20% of remaining spaces under Ladestanderbekendtgørelsen (section 2.1). The building cannot be occupied before the station is installed, potentially requiring agreements with operators between tender rounds. Similarly, monitoring or citizen requests might prompt requests for extra stations before the next tender.

Recommended to align all tenders to the same time horizon where possible, avoiding many small separate tenders — instead grouping tenders into a "rolling" cycle. Two approaches (Figur 10.1):
1. Include in the tender text that the operator may be required to install stations at additional locations after the tender, with the operating right expiring at the next major tender, aligning future locations into the rolling cycle
2. Tender individual locations separately with a shorter term, so they synchronize into the rolling cycle with other locations

### 10.4 Selection and Award Criteria
Possible criteria the municipality can weight differently based on priorities (some as requirements, others as award parameters):
- Price for the municipality
- Charging station functionality
- Fair and transparent kWh prices and equal access for all
- Climate-friendly/green electricity
- User-friendliness, accessibility, and service
- Aesthetics
- Operator's experience/references
- Operator's financial solidity

The municipality should consider both relative weighting and how each criterion is assessed. The market is generally still developing, with many new operators that may struggle to show multiple years of financial statements — the municipality must weigh its risk appetite for newer companies to broaden operator-market participation.

### 10.5 Suggested Tender Material Content
- Locations covered by the tender
- The agreement's timeframe
- Groundworks and grid connection
- Signage
- Design and aesthetics
- Maintenance
- Consumer prices
- Usage-monitoring data
- Technical specifications
Tender material can form the basis for the subsequent contract with the operators awarded the right to operate on municipal land/road land.

#### 10.5.1 Locations Covered by the Tender
Operators must see which pools/locations are covered, but it's also recommended to publish and reference the municipality's broader charging-infrastructure plans, giving operators visibility into future business opportunities to inform major investment decisions — fair practice given significant investment stakes for operators. Transparent charging-infrastructure planning also helps current/prospective EV owners assess long-term area sufficiency, and lets citizens/prospective operators flag additional locations they judge as needing chargers.

The municipality should decide whether to specify precise charger placement within each designated location. Different considerations favor proximity to an entrance (visibility/promotion) versus distance from it (longer-duration stays/charging). Usually, cable-routing cost drives placement decisions (minimal groundworks = cheapest), though some locations may warrant a more precisely fixed placement.

#### 10.5.2 The Agreement's Timeframe
Relevant considerations: contract period; establishment period; option to extend; reinstatement after agreement ends; option for termination during the period, including a deadline for commissioning.

**Kontraktperiode (Contract Period):** **AFI-lovens § 3, stk. 2** sets an upper limit — quoted in full per source:
- **AFI-lovens § 3:** agreements between a public contracting authority and a charging-point operator for the right to operate publicly accessible charging points, and for the right to operate charging points for private vehicles of the contracting authority's employees/guests, must be entered on market terms.
- Stk. 2: such agreements can be entered for a **maximum of 10 years**, extendable to **15 years** if warranted by extraordinary infrastructure investment considerations.
- Stk. 3: the public contracting authority must ensure the operator's prices to users are reasonable and non-discriminatory.
- Stk. 4: the Transport Minister sets rules on entering such agreements, including announcement, tendering, standard terms, and standard reasonable/non-discriminatory pricing terms.

If the tender falls under the **Koncessionsdirektivet**, the contract generally must not exceed **5 years** unless justified by the scale of the operator's investment and its opportunity for a reasonable return.

Market dialogue can clarify how long a contract term is needed — less-attractive pools may require longer terms for a viable business case; the municipality may need to co-finance infrastructure at various municipal buildings; price is affected by contract length. The municipality-as-developer must weigh how long a term it's willing to grant to lower the price — noting current tender terms could look unfavorable later given fast-changing technology, equipment, and price levels.

**Etableringsperiode (Establishment Period):** may set a timeframe to better control when tendered locations become functional; should check whether sufficient power can be delivered to the chargers within the given period, so grid-company delays aren't held against the operator (see section 6.3). The tender can allow the operator to set its own installation pace within a pool, as long as all stations are installed within an overall fixed establishment period. If multiple pools are tendered simultaneously, the municipality can control installation pacing across pools — spreading workload (e.g., site visits) and possibly aligning with when co-financing becomes available. Operator and municipality interests can diverge here: the municipality typically wants enough capacity installed quickly to minimize wait times/charging-seeking traffic, while the operator typically prefers installing additional stations only once existing capacity is fully utilized.

**Mulighed for forlængelse (Extension Option):** the municipality should decide whether to include an extension option without a new tender, and whether this is the municipality's unilateral decision or requires mutual agreement at a defined point. An extension option can increase a pool's attractiveness if the base contract period is shorter than the operator would prefer — but reduces tender transparency, risking bids based on differing interpretations of the tender material.

**Reetablering efter endt aftale (Reinstatement After the Agreement Ends):** should specify how physical conditions are reinstated if the location won't be re-tendered, covering both above- and below-ground equipment. Consideration of whether the connection's residual value (underground) should factor into a re-tender — the first operator bears large groundworks/connection-fee costs a subsequent operator won't incur; can be addressed by having the new operator pay the previous operator a share of the connection fee (ampere cost), one of the largest initial-establishment expenses.

**Opsigelse/ophævelse (Termination/Cancellation):** distinguishes termination (opsigelse — ending the contract, typically with notice, without needing special grounds) from cancellation (ophævelse — ending the contract for material breach, e.g., prolonged failure to meet maintenance obligations). The tender should specify grounds for cancellation and notice periods for both parties, and it's recommended to specify a timeframe within which the permit must be put to use, after which it lapses and can be given to another operator. In contracts involving large investments, a termination clause increases operator risk, which can be a cost-inflating factor or reduce a pool's attractiveness.

#### 10.5.3 Groundworks and Grid Connection
Excavation permits are typically required from the road authority per **Vejlovens § 73** when installing charging stations, and the applicant must obtain LER data per **LER-lovens § 9** — coordinating excavation to avoid repeatedly digging up the same road in short succession. **Figur 10.2**: screenshot from virk.dk, where excavation work must be reported.

Before groundworks, carefully consider whether to prepare simultaneously for expected future expansion — long-term planning required, since ducting/cable trays are relatively cheap to lay now versus a costly (potentially unnecessary) extra expense if re-excavation is needed shortly after to lay thicker cables; groundworks are usually disruptive to residents/traffic.

Not all operators have identical underground setups (ducting layouts differ) — information should be obtained from the winning operator on how cables were laid, easing future work for e.g. new operators (see also section 10.5.9). Cables and their locations must subsequently be registered in LER; the municipality should decide whether this is specified in the tender or the subsequent permit/agreement.

The municipality must decide whether it will itself establish technical installations and/or bear associated costs, or whether the operator will — and similarly whether the municipality or operator is responsible for securing grid connection and paying the connection fee (ampere purchase). If the operator bears underground installation and grid-connection costs, the tender contract can specify the municipality will pay part/all of the operator's not-yet-depreciated investment cost if the tender ends; should also address transfer of grid connection and/or cables to the municipality or a new operator after contract end.

Space must be allocated for electrical installations, including **10/0.4 kV substations**, cable installations, and cable cabinets, at or near locations wanting charging infrastructure — placement should be decided in close dialogue with the local grid company, ideally ensuring these installations can remain at the given location long-term (the installation can potentially be registered via a servitude/tinglysning), since later relocation is very costly.

#### 10.5.4 Signage, Marking, and Parking Restrictions
Charging stations should be signposted at installation; the municipality decides which signs to use (section 11.2), and the tender material should describe signage/marking requirements, linked to parking restrictions on the lot.

Signage as marketing matters to operators and can affect bid interest/pricing. The municipality should decide who bears signage costs, and this should be stated in the tender — if the operator, specify which signs to use; Danish road regulations ("vejreglerne") must be followed, and a signage plan submitted for road-authority approval.

Examples exist of municipalities signposting charging spaces well after the charger itself is installed — a disadvantage for the operator; signage should therefore be installed synchronously with the charging station's grid connection. It benefits both operator and users if the operator ensures the EV driver is notified in good time that the vehicle is sufficiently charged or the parking time limit is reached, for more efficient charging-infrastructure utilization.

#### 10.5.5 Design and Aesthetics
Should decide whether aesthetic requirements apply to installation/charging stations in the tender. If multiple tenders bring in different winning operators, charging stations of varying colors/light colors could end up adjacent — a special paint/color code requirement not a standard product could affect price and potentially deter some operators from bidding.

Beyond a special color, consider whether the operator's name/logo may/must appear (in large letters, a defined typeface). Advantageous for operators — helps subscribers/loyal customers identify the right station. For operational reasons, phone number, website, and/or other contact information should also appear on the station; the municipality should also consider whether advertising is otherwise permitted.

Per **AFI-lovens § 7**, publicly accessible high-power chargers must accept payment cards if located on public land or having received public subsidy — quoted in full per source (paraphrased here for length; see the corresponding provision quoted in full in the companion draft-contract document's Section 6.3 discussion, and the excerpt reproduced verbatim in this handbook covers: payment-card acceptance requirement for public/subsidized chargers with an exception for sub-50kW chargers operating under a mobility-service provider's name, a requirement that operators using that exception contract with a charging-services provider or digital-platform provider per §§ 8–9, allowance for long-term customer agreements, and a guarantee that all publicly accessible charging points must allow ad hoc charging without requiring a contract with the specific electricity supplier/operator).

Publicly accessible charging stations must display a list price per kWh and the total purchase price on an electronic display, per **Bekendtgørelse om krav til offentligt tilgængelig infrastruktur for fossile brændstoffer og alternative drivmidler m.v.** (BEK nr 1037 af 28/05/2021).

If curbside charging is used, consider requirements ensuring sufficient sidewalk space and cable management to avoid obstructing pedestrians or operations like snow clearing (elaborated in section 11). Charging stations must also meet **Bygningsreglementets** (BR18) requirements for user-operated installations.

For rapid-charging stations, further consider size, covering/shelter (which can obstruct views, be unsightly, or cast shadows), and light/noise conditions that could disturb surroundings/neighbors — and clarify whether it's the operator's, municipality's, or landowner's responsibility to meet municipal requirements for e.g. seating/shelter and waste bins at the station(s). Access conditions should also be considered. The municipality should ensure it retains final approval rights over charging-station design and site-layout drawings for rapid-charging stations.

#### 10.5.6 Maintenance
Before tendering, consider how the area will be operated/maintained, including snow clearing. Consider whether operators may set special maintenance requirements if the municipality takes on part of the operations.

The municipality should decide the deadline for an operator to remove graffiti and repair vandalism/collision damage — e.g., one week. Contact information for reporting operational problems/vandalism should appear on the station; consider whether periodic inspection requirements should be introduced.

Consider requiring the operator to maintain a fault-reporting system (web/mobile-based) allowing 24-hour fault reporting, usable by both customers and the municipality. It may be beneficial to require the operator to establish its own local service organization, or a service agreement with an external local service provider — with fault reports received directly by the service organization managing operations. If the municipality wants to monitor service work, it can require logging of registered faults so the municipality/user can subsequently track how a report was handled. Generally, the operator should describe in the tender phase how customer inquiries/complaints are generally handled, and the municipality should weight this as an award parameter.

Consider the deadline for the operator to remedy an outage — e.g., remediation must begin within 24 hours of the operator being notified; if the municipality wants to be informed of this, it must be written as a tender/contract requirement.

If maintenance or other work requires groundworks, consider who reinstates surface coverings — for certain surface types, the municipality may want the right to require reinstatement by the municipality, billed to the permit holder. Consider what penalty applies for missed deadlines — proportionate to the breach.

#### 10.5.7 Prices
Per **AFI-lovens § 3, stk. 5**, the Transport Minister can set standard terms for agreements, including standard terms on reasonable/non-discriminatory pricing (footnote: the Konkurrence- og Forbrugerstyrelsen was preparing a competition analysis of the EV charging market, expected complete early 2022). Until such standard terms exist, the municipality can itself include pricing terms in the tender material.

Must ensure all can charge at a non-discriminatory price, and define what constitutes fair/non-discriminatory pricing if used as a competitive parameter — at minimum, ask whether the operator uses differentiated customer pricing and what the kWh price is for each customer type.

**Roaming** — the ability to charge at most operators' stations regardless of subscription — is a requirement for being granted the right to operate on municipal land. Prices and ease of access still vary, including for normal chargers — the tender should therefore require ease of use for any EV driver regardless of subscriber status with that particular operator. Bidders should disclose payment solutions offered to charging customers (fixed-price subscription, subscription, ad hoc charging; via app, charging tag, payment card, or other).

Prices shouldn't diverge unreasonably between customer types, since in principle users don't experience the station as "publicly accessible" if prices are too high — bidders should disclose kWh prices for each customer type (and any other fees) in their bid.

To ensure best possible utilization, the municipality can consider requiring the user be notified when charging is complete (e.g., SMS or app notification); consider how the operator can further encourage EV drivers to move their vehicle once charging is complete — possibly via rising prices after 80% charge, combined time+kWh pricing (as in Norway), or "fines" for multi-hour overstays during daytime hours. Prior market dialogue can clarify what systems operators have available to support this.

#### 10.5.8 Data for Usage Monitoring
The municipality should consider requiring the operator to make charging history/data available, to monitor usage over time, ensure infrastructure supports desired charging patterns, and address problems. If wanted, decide how often the operator must be obliged to deliver this data — perhaps quarterly or every six months.

There's a national interest in collecting data from the entire national charging infrastructure into a data hub alongside other electricity consumption, for grid monitoring/planning — beneficial if municipalities already write into the tender material that operators must submit data to a future national data hub once developed.

**Example data operators should deliver to the municipality/national data hub (Figur 10.3, reproduced):**
- Charging station model number/type and take-off number
- When charging occurs
- How much electricity is used per session
- Charge duration per session
- What share of the day/night the station is on average in use
- The station's uptime
- Which fuel form is chosen, if the operator offers other charging forms (e.g., green electricity or equivalent)
- Which payment form customers (possibly by segment) choose, e.g. subscription, mobile payment, or cash
- What the customer/customer segments pay to charge

#### 10.5.9 Technical Specifications
The municipality should focus on the possibility of taking over charging equipment at agreement end and/or with a new operator at re-tender, built into the tender and subsequent contract basis, ensuring a new operator can take over without replacing all equipment and/or underground cables. The tender and subsequent contract basis should therefore require information on:
- Installation requirements, electrical (e.g., conductor cross-section, conduit, meters, protective equipment) as well as communication (GSM, WiFi, data cable etc.)
- Make, any approval, and technical data on charging stations/boxes, including built-in protective equipment, meters, enclosure class, protocols, data communication etc.
- Whether/how load sharing/load balancing is possible/prepared
- Efficiency
- Which plug type(s) (minimum requirement, multiple types per station/group)
- Roaming conditions, wait time, uptime, and physical accessibility
**Tenders must not contain product requirements, including requirements for specific makes/brands.**

## Section 11: Layout of Charging Infrastructure Sites

### 11.1 Overall Considerations for Charger Placement

#### 11.1.1 Overall Guidelines (recommended municipal guidelines)
- **Cluster (publicly accessible) chargers into "ladeøer"** (charging islands), to avoid charging-seeking traffic inconveniencing both the individual EV driver and other traffic
- **Don't install more charging infrastructure than needed** — ongoing usage/demand monitoring should keep placement/quantity at an acceptable level
- **Accessibility, reachability, and traffic safety** for other road-user groups must not be compromised by charging-infrastructure installation; vejreglerne (road regulations) should always be followed
- For new urban areas/redevelopment areas: describe how/whether EVs will charge locally (home normal chargers, fast, or rapid chargers), and prepare ducting etc. so all vehicles in the area could potentially be electric

#### 11.1.2 Cost-Conscious Charging-Space Designation (Tips for Lower Cost)
1. Place charging stations as close as possible to the electrical panel/connection point
2. Wall-mounted chargers are cheapest — check feasibility
3. Excavate where there's no surface covering, if possible
4. Check for available (spare) amperes already at the site
5. Lay ducting for possible future expansion; cabling to normal chargers can be sized larger up front, avoiding cable replacement if later upgrading to a fast charger — though more expensive upfront, oversized cables also reduce line loss (wasted electricity)

#### 11.1.3 Consideration for Other Traffic Groups
Other reasons may justify a location beyond lowest-cost placement — traffic safety, accessibility, and reachability for other traffic groups, plus visibility (see sections 11.3, 11.4). Placement must consider pedestrians and cyclists, and good bicycle parking shouldn't be sacrificed for charging-station placement near building entrances.

#### 11.1.4 Maintenance Considerations
Must ensure easy access to charging stations and any associated lighting, and ease of sweeping/snow-clearing/salting around the charger — to be considered at the placement stage. Maintenance should also be factored into the operator contract (section 10.5.6).

#### 11.1.5 Attractive Normal-Charger Placements
Worth understanding what operators view as attractive locations, to achieve good tender pricing/terms:
- Good customer base — generally areas where few residents have own parking and many park on the street; good for locations with typically longer dwell times, using the normal charger's longer charge time well; these types of locations should overlap with those designated per section 8
- **Angled or perpendicular parking is more attractive than parallel parking** — parallel parking often sees more collision damage to chargers from reversing vehicles, and creates longer distances between chargers, requiring more excavation (more expensive)
- Many operators prefer **at least 3 dual-outlet normal chargers clustered per location**, allowing up to 6 simultaneous charging vehicles, improving groundworks economics and increasing the likelihood a charger is free, reducing charging-seeking traffic; space for future expansion (ducting) is welcome; an even number of stalls is preferred, easing dual-outlet coverage — an extra single-stall charger is comparatively more expensive than one covering two stalls
- Operators prefer the charger on the **same side of the road as the supply cable**, reducing excavation distance; the charger area should ideally be free of obstructions with good sidewalk clearance for access behind the charger
- Good signage matters for flow and preventing non-charging vehicles from occupying charging spaces
- Operators generally prefer a **3-hour daytime time limit, lifted at night (e.g., after 22:00)** — see section 11.2

### 11.2 Signage and Marking
The municipality should ensure consistent traffic-sign regulation for EV parking municipality-wide, benefiting users. Signage categories:
- Stopping and parking for EVs marked with under-sign **UE 33,4**, with no charging requirement
- Stopping and parking for EVs marked with a text under-sign, e.g., "only applies to charging of electric vehicles"
- Combination of EV parking with and without a charging requirement, needing separate time specifications per category

References the "Håndbog om Færdselstavler, Oplysningstavler" for guidance/examples, with the E 33 Parkering sign topped by relevant under-signs. **Police consent is required before signage is installed.**

Municipalities have authority under **Færdselslovens § 92, stk. 1, nr. 1** to independently decide where EV parking spaces are established.

Time-limiting the parking area can help ensure more available chargers throughout the day and more efficient infrastructure use. **The charging industry generally recommends a 3-hour daytime time limit** under current technological conditions; the limit can be changed/lifted after normal work/opening hours, or after **19:00–22:00**, depending on placement — helping ensure EV drivers don't effectively get "private" dedicated parking spaces. There's legal basis under the Færdselsloven and vejafmærkningsbekendtgørelsen to impose municipal parking fines for illegal parking in EV-designated spaces.

Some cities are working to remove parking restrictions/paid parking for EVs to boost EV-purchase incentives — but this could worsen urban-environment benefits if fossil vehicles are simply replaced 1:1 by EVs, which share many of the same drawbacks (congestion, barrier effects etc.). Municipalities should consider whether to phase out EV parking advantages as EV adoption grows.

Vans/tradesperson vehicles that need to charge while stationary (e.g., loading/unloading) pose a particular challenge — hard to ensure a free charger nearby where the vehicle is stopped. **Oslo** has reserved, via signage, areas for electric vans in the city center.

### 11.3 Normal and Fast Chargers on Parking Areas
Following the AFI-loven amendment (section 2.2), municipalities can tender the right to operate on municipal land/road land; this right cannot simply be granted to an operator without a tender, and **Vejlovens § 80 can no longer be used**.

Charging stations on sidewalks adjacent to a parking area follow the same recommendations as curbside placements (section 11.4). Charging infrastructure requires extra space on a parking area — relevant when designating which stalls convert to charging spaces, given minimum dimensions for stalls, sidewalks, and maneuvering area can make fitting sufficient space challenging.

Placing a charger within a stall requires a longer stall to accommodate the charging vehicle and operating access around it, factoring in maneuvering space behind the vehicle; space is also needed for bollards to prevent the charger being struck. Narrow stalls can make it difficult to exit the vehicle and move between parked/charging vehicles if the charging plug sits on the side, requiring cable to extend along the vehicle's side — favoring wider stalls at charging spaces; for perpendicular parking, stalls **~15 cm wider than normal** are recommended, referencing the handbook "Anlæg for parkering og standsning i byer" for dimension guidance.

Handicap-accessible parking with a charger requires level, accessible access to the charger and necessary maneuvering room within the space, per "Færdselsarealer for Alle" section 3.6.

**Figur 11.1** (photos): illustrates charging-plug location variability across vehicle models (source: Rambøll Norge) and the resulting challenges in narrow stalls, particularly when two facing vehicles both need to charge with outlets on opposing sides.

### 11.4 Normal Charging at Curbsides in Streets
Charging stations on sidewalk areas should only be used if no other way exists to ensure sufficient charging infrastructure, given several downsides:
- More charging-seeking traffic searching for a free charger, versus chargers clustered in a parking-lot "ladeø"
- Longer groundworks, hence higher costs
- Often greater inconvenience and traffic-safety risk to other traffic than parking-lot placements
- Often requires taking sidewalk area at the expense of pedestrian traffic space
- Often harder to aesthetically integrate at curbside/sidewalk than on a parking lot

Curbside installation requires a wide sidewalk for accessibility/reachability, and adequate distance requirements from the carriageway edge:
- **Loose cables on the sidewalk are not permitted** per **installationsbekendtgørelsen** (short term for **bekendtgørelse nr. 1082 af 12. juli 2016** om sikkerhed for udførelse og drift af elektriske installationer) — must be vandal-secured, and for accessibility/traffic-safety reasons
- Good sidewalk accessibility must be maintained; the charger should not sit in the walking path; good distance from fixed objects to the tactile guide-line is recommended (references the handbook "Færdselsarealer for alle – Universel design og tilgængelighed," section 3.1 for walkway-width recommendations)
- The charger should be placed **0.5 m from the front edge of the sidewalk**, per the handbook "Grundlag for udformning af trafikarealer," section 6.3.2
- Any change to or new parking restrictions must be approved by police

The road authority must, for every project, assess and ensure good accessibility and traffic safety so all pedestrians, including those with reduced mobility, can pass unhindered on the sidewalk.

For chargers on sidewalks near handicap-accessible parking, accessible/level access (e.g., an asphalt ramp) should be ensured between the parking area and the charging station, plus necessary maneuvering space (e.g., for wheelchair users) within the parking spaces and where the charger is operated from, per "Færdselsarealer for Alle" section 3.6.

**Covering the cable on top of the surface is not considered an accessibility solution**, since this creates a kink/obstruction that could be kicked/pushed loose, exposing the cable and creating an accessibility/traffic-safety risk — requires a special buried-cable-in-sidewalk solution, affecting future sidewalk operation/maintenance.

#### 11.4.1 Charge Box on Private Land with Parking on the Road
Many citizens without own-land parking (typically older townhouses) park on road land instead — often eligible to install a home charger on their own land and charge outside their property.

**Figur 11.2** illustrates: when citizens install a charge box on their own parcel and want to run the cable across the sidewalk, this requires road-authority approval — associated with problems, since simply running a cable across the sidewalk (as illustrated) can create dangerous situations and is contrary to installationsbekendtgørelsen.

**It is generally not recommended to grant citizens permission to run a charging cable across road land/sidewalk** for charging purposes — the same problems as described in section 11.4 arise. For this solution to be used, the road authority must approve it via a permit for special use of road land, per **§ 80 of the vejloven** or **§§ 66–68** of the privatvejsloven. Installing charge boxes on house facades facing a public road requires road-authority permission per **vejlovens § 86** if the charge box projects into the public road's area.

**Considerations for the road authority when assessing requests to use road land for charging cables:**
- If the EV owner has reasonable parking/charging options on their own land, the request can be refused, since roads are primarily for traffic, not parking, when other options exist
- Requests can be refused if the road authority judges it would cause reachability, traffic-safety, and/or accessibility problems
- For traffic-safety reasons, private curbside charging is **not permitted** where a separate cycle path/lane exists or is planned
- Loose sidewalk cables are prohibited per installationsbekendtgørelsen
- The EV owner/applicant must submit a proposal for the cable/line routing solution on the sidewalk for road-authority approval

If none of the above trigger a refusal, private curbside charging permission can be granted — but the curbside parking spot **cannot be reserved** for that individual EV owner/vehicle; the EV driver cannot be guaranteed to park directly outside their charger. If granted, an agreement with the individual EV owner should cover payment for installation/reinstatement of any device meeting reachability, traffic-safety, and accessibility conditions.

**Figur 11.3 — Example requirements in a permit for special use of road land** (source: Rambøll, based on Helsingør Kommune's standard permit): applicant pays for installing and later reinstating the sidewalk device; applicant is responsible for operation/maintenance of the device and sidewalk surface up to it; applicant must register the device on the property title (tinglyse), so responsibility follows "whoever is the property's owner at any given time," submitting a proposed declaration for the road authority's approval and bearing all drafting/registration costs; the cable must run the shortest direct line from the property to the curb; the cable must not lie loose on the sidewalk/road area during or after charging; the applicant bears liability for the device, including any injury claims (e.g., a trip-and-fall); the applicant is encouraged to register the device in **LER.dk** to prevent excavation damage; the municipality may terminate the agreement at any time with **1 month's notice** if the agreement is breached or other circumstances arise (e.g., sidewalk renovation or other road works) and remove the device, with no compensation owed to the EV owner; removal and reinstatement of road land applies if the charger is permanently taken out of use.

New technical charging possibilities are expected to keep emerging, and the above example requirements should be adapted accordingly over time.

### 11.5 Charging Stations in Parking Garages and Basements
Generally the same recommendations apply as for general charging-site layout (section 11.1) and for normal/fast chargers on parking areas (section 11.3). Fire-safety considerations must additionally be assessed for garage/basement placements.

As of the handbook's writing (2022), **no special rules exist for EVs in parking garages/basements** — parking-building design rules are based on experience with conventional-fuel vehicles. Electricity as a fuel has different fire/explosion characteristics than conventional fossil fuels; compared to conventional-vehicle fire risk in parking buildings, EVs present these challenges:
- Potentially long extinguishing time and high water use
- Risk of re-ignition after extinguishing

Based on recommendations from **Oslo Brann- og redningsetat** (Oslo Fire and Rescue Service), it's recommended parking garages/basements have accessible systems for cooling a fire to prevent structural collapse. Until more is known about extinguishing time and rescue response for EV fires in parking basements, **sprinkler/water-mist systems should be a minimum requirement** to permit EV charging.

**Recommendations from Oslo's Fire and Rescue Service (Figur 11.4, reproduced in full)** to better facilitate rescue/extinguishing response in EV garage facilities:
- Install a common cut-off switch to de-energize all charging stations in the system, placed accessibly, visibly, and clearly marked, ideally near the fire panel
- Install an automatic fire alarm system — early warning can support early extinguishing response, limiting fire scale
- Increase distance between parked vehicles — can reduce fire-spread risk and ease extinguishing response
- Establish an orientation plan per applicable building regulations, placed on the wall at entry/exit ramps and all access routes, containing necessary information about fire-separating building elements, escape/access routes, extinguishing equipment, and fire-technical installations (alarm/extinguishing systems) for the parking basement; should use easily decoded symbols and be available for use outside in a smoke-free environment
- Place chargers level with the entry/exit and, if possible, at a facade with natural ventilation, so emergency responders can more easily pull the vehicle out of the building — ideally chargers placed at ground level so removal can use a standard sweeping blade or winch

### 11.6 Layout of Rapid-Charging Stations
Rapid-charging stations emphasize efficiency — users should be able to enter, charge, and leave quickly; especially important on the primary road network, and increasingly important as future charging times shorten (stations should be designed future-proof where possible).

Based on experience from detail projects laying out rapid-charging stations along the motorway network (transferable to varying degrees to other primary roads). Dimensions cited from Vejdirektoratet's rest-area drawings, where charging stations were established following an April 2022 tender:

- **Efficient charging:** from a traffic-safety perspective, reversing should be avoided — drivers should be able to drive in, charge, and drive out forward. This requires more space/cost than a reverse-in/out layout. A no-reverse solution can use charging spaces **3 m wide and 5 m long**, parked parallel to a median strip with rapid chargers; if the spaces are to be covered, the median should be **1.5 m wide** to allow for support columns, also accommodating chargers of varying dimensions.
- **Accessible vehicles/buses and EVs with caravans/trailers:** separate, larger charging spaces recommended, **4–4.5 m wide and 14 m long**, ideally designed to avoid reversing; must ensure accessible, level access to charger controls for those with mobility impairments/wheelchair users; no curbs should impede charger use; the charging area should have a firm, even surface.
- **Circulation:** for larger traffic volumes, consider one-way flow design, and whether to allow circulation so a driver can return/wait if no charger was free upon arrival; regardless of scale, a queuing/waiting area should exist where EV drivers can wait for a free charger.
- **Bus and truck parking:** consider whether bus/truck parking and heavy-vehicle charging should be included at the rapid-charging station, since both electricity and hydrogen are expected to play roles in heavy-transport fuel, and it may be wise to design this in from the start.
- **Transformer stations:** rapid charging is highly energy-intensive, usually requiring a transformer station (typically **3m × 3m**) at the site; larger installations may need both a transformer station and smaller distribution units — space-intensive elements requiring placement planning.
- **Other facilities:** consider whether other amenities are needed (covering/shelter, toilets, kiosk, fast-food restaurant, playground etc.) — charging times can still be long enough that a stay of up to an hour would not be unusual even with rapid charging (see section 3.5).

**Figur 11.5:** example layout of a "ladepark" as an extension of an existing Vejdirektoratet motorway rest area (Vejdirektoratet/Rambøll figure).

**Experience from Norway:** at rest areas, private operators typically establish a commercial charging offer for EV owners, or public bodies tender the right to operate charging services to a private actor. These private operators generally want to offer more space around the vehicle for charging users than a standard parking space — so a charging space is often **3 m wide and 5 m long** in Norway. Charging stations are usually placed on a **1 m wide median** alongside or in front of the vehicles.
- **Figur 11.6:** rest-area example in Norway with chargers placed in front of vehicles (photo: Kempower)
- **Figur 11.7:** rest-area example in Norway with chargers placed alongside vehicles (photo: Shell)

## Section 12: Future Charging Forms

### 12.1 Better Batteries and Shorter Charging Times
Trend toward longer-range EVs as batteries grow larger and vehicles drive further per kWh; simultaneously, batteries able to accept charge faster are being developed. This means future EVs may charge less often (assuming no increase in driving) and, when charging, spend less time doing so — potentially reducing future occupancy pressure on publicly accessible chargers.

### 12.2 Booking Charging Stations
A challenge with current infrastructure is EV drivers not being able to guarantee finding a free charger, risking wasted charging-seeking traffic and time loss. Booking systems for charging stations already exist and could address this; broader adoption/user familiarity would be needed. Under current road legislation, spaces on public roads cannot be reserved, but significant potential exists for booking chargers at companies, housing organizations, and other private-parking sites. Cross-operator booking systems (avoiding needing multiple apps) would be advantageous for a unified overview of booking options.

### 12.3 Electrification of Heavy Vehicles
Truck transport demand in Danish supply/logistics chains is growing; truck transport activity is expected to grow by nearly **22% from 2020 to 2035**, driven by expected GDP, demographic, and infrastructure developments (source: Energistyrelsens Klimafremskrivning 2022). Larger batteries increasingly enable longer-distance goods transport by electric truck; the number of electric heavy vehicles is expected to rise markedly in coming years. A conservative estimate from Energistyrelsens 2022 climate projection suggests new electric-truck sales will rise to **15% by 2030**. Introduction of Danish **kilometer-based road charges from 2025**, alongside national CO2-displacement requirements, is expected to significantly increase this figure further; EU's **"Fit for 55"** legislative package initiatives are also expected to substantially increase electric trucks on the road. Sufficient charging infrastructure (and other fuels) must be ensured on European roads to support this transition, ideally jointly planned with charging infrastructure for other transport modes.

### 12.4 Load Balancing (Lastbalancering)
If every charger at a location must deliver full power to all connected EVs throughout the charging period, the connection must be dimensioned for a **simultaneity factor of 1** (all charging points drawing maximum current at once) — otherwise fuses trip when this scenario occurs. This easily leads to costly oversizing, avoidable via load balancing.

*Example:* 5 charging points at 11 kW (16A each), if all used simultaneously (simultaneity factor 1), would nominally require an **80A** supply — but in practice EVs often charge at staggered times and/or park long enough (e.g., overnight) that they don't need the full 11 kW to fully charge in the available window.

**Figur 12.1** illustrates static load balancing: 5 vehicles sharing a fixed **32A (22 kW)** supply instead of 80A. Example sequence: at 17:00 two cars charge at full 11 kW each; at 18:00 a third car joins and load balancing reduces each car to 7.3 kW; at 20:00 two more cars start charging at full power since the original three have finished.

**Static vs. dynamic load balancing:**
- **Static:** a set number of charging points share a **constant** supply allocation (as in the example above, where 32A/22 kW is dedicated purely to charging infrastructure)
- **Dynamic:** no constant supply allocation is available, since the supply is also (or even primarily) used for other purposes — e.g., a residential building where the supply was originally sized for ordinary apartment consumption, with typically high demand and little spare capacity during the "kogespids" (17:00–20:00); load balancing then reduces (or fully stops) charging during that window based on demand/available capacity, then increases charging-point allocation again later in the evening as capacity frees up

Both static and dynamic load balancing can save substantial money on supply sizing; the technique is also used at higher charging levels, e.g. rapid chargers.

**Load Management Systems (LMS)** used for load balancing optimize local-installation use (technical/economic optimization), and can also be leveraged for participation in current/future electricity markets for regulating power (interruptibility), local flexibility, reactive power, and similar.

**Figur 12.2:** photo of the **Sperto ladehub in Ishøj**, featuring a **150 kW rapid charger and 7 normal chargers** sharing a single grid connection via load balancing/load management, contributing to both economic and environmental project sustainability — normal chargers mainly used at night, rapid charging mainly during the day.

### 12.5 New Business Models/Trends
How EV drivers choose to charge depends on many parameters, but convenience/time and price are particularly important. Future business models/trends can't currently be foreseen with certainty, but examples: some retail chains/stores may offer free charging (e.g., on a fast charger) to attract customers, who linger longer (and buy more) to get extra charge. Companies may offer workplace charging to attract labor, potentially as a free/cheap employee benefit. Such new models/trends could affect charging patterns and demand for publicly accessible charging infrastructure.

### 12.6 Inductive Charging and Electric Roads
Inductive charging is cable-free — the vehicle drives over a field integrated into the road surface and charges. Only very few vehicles currently support this. An inductive charging space consists of a "socket" (magnetic field) in the asphalt and a "power module" housed in a shed alongside a main panel; maximum distance between the module cabinet and the magnetic field is about **35 meters**. Current technology limits energy transfer, constrained by the vehicle's own technology, to **50–75 kW**.

**Case: Oslo pilot project** at a taxi rank — inductive charging particularly suits queuing taxis, since no cable needs plugging/unplugging as vehicles move up the queue, allowing "sjatladning" (opportunistic top-up charging) while waiting. **Figur 12.3:** inductive charging plate in an Oslo taxi waiting lane, with the wood-clad power-module shed visible in the background (photo: Rambøll Norge) — the shed is noted as relatively space-consuming in the streetscape.

**Case: Paris** has established a longer test stretch of the technology, aiming to let roads charge vehicles while driving, allowing smaller/lighter batteries and eliminating dedicated charging time.

**Case: Sweden** is one of the countries investing in electric roads — since **2018**, a **2 km** asphalt stretch outside Stockholm has allowed charging EVs and electric trucks while driving. The idea: broad electric-road rollout would enable smaller vehicle batteries, eliminate charging time, and remove range anxiety on electrified roads — though construction costs are very high.

### 12.7 Vehicle to X (V2X) / Vehicle to Grid (V2G)
V2X refers to an EV communicating with entities it can affect or be affected by, including: **V2I** (vehicle-to-infrastructure), **V2N** (vehicle-to-network), **V2V** (vehicle-to-vehicle), **V2P** (vehicle-to-pedestrian), **V2D** (vehicle-to-device), **V2G** (vehicle-to-grid) — relevant to traffic safety, transport-network efficiency, and the electricity grid.

**V2G** uses vehicle batteries as grid batteries — the EV can, for payment, deliver electricity back to the grid during peak-load situations, helping balance demand. Requires individual agreements with each EV driver, an administrative challenge. **V2G is not currently a real option in Denmark**, since it's currently only possible with the **CHAdeMO** plug and not CCS-Combo, which most Danish vehicles use (source: Ingeniøren/Gridtech, https://pro.ing.dk/gridtech/artikel/ekspert-om-v2g-glem-de-private-sats-paa-store-elbilflaader, and Nuvve, https://nuvve.com/denmark/).

**Case: Frederiksberg Forsyning's V2G trial (Figur 12.4).** Frederiksberg Forsyning launched a trial in **2016** with **10 Nissan EVs** fitted with CHAdeMO plugs. The trial showed the EVs support V2G and are ready to deliver power back to the grid; commercializing the technology is possible, but further steps are needed for universal V2G/VGI-service support across all EV brands, standards, and markets. The next step is testing through larger projects to help mature the technology to a level ready and available for private EV owners (source: Energiforskning.dk, "Parker" project final report, 2019, https://energiforskning.dk/sites/energiforskning.dk/files/media/document/final_report_Parker_2019-04.pdf).

## Named Legislation, Standards, and Organizations Referenced (Consolidated)
- **Ladestanderbekendtgørelsen** (BEK nr. 181 af 05/03/2020)
- **AFI-loven** (Lov om infrastruktur for alternative drivmidler til transport, in force 6 April 2022)
- **Bekendtgørelse om kommuners og regioners ydelse af betaling til operatører af offentligt tilgængelige ladepunkter** (in force 1 April 2022, lapses 31 December 2024 absent renewal)
- **Bekendtgørelse af lov om private fælles veje** (LBK nr. 1234 af 01/11/2015)
- **Lov om offentlige veje m.v.** (Vejloven)
- **Bekendtgørelse om anvendelse af vejafmærkning**
- **Bekendtgørelse af færdselsloven**
- **Bygningsreglementet (BR18)**
- **Direktiv 2014/23/EU** om tildeling af koncessionskontrakter (Koncessionsdirektivet)
- **Bekendtgørelse om sikkerhed for udførelse og drift af elektriske installationer** ("installationsbekendtgørelsen," BEK nr. 1082 af 12. juli 2016)
- **Bekendtgørelse om krav til offentligt tilgængelig infrastruktur for fossile brændstoffer og alternative drivmidler m.v.** (BEK nr 1037 af 28/05/2021)
- **Bekendtgørelse af lov om registrering af ledningsejere** (LER-loven)
- **Bekendtgørelse af lov om elforsyning** (Elforsyningsloven)
- **Netselskabers bestemmelser for tilslutning til og brug af distributionsnettet / Fællesregulativet** (Green Power Denmark)
- **Direktiv 2018/844/EU** (amending 2010/31/EU and 2012/27/EU on buildings' energy performance)
- **AFI-direktivet** (EU 2014/94/EU)
- **Energistyrelsen, Energinet, Radius** — Danish energy/grid authorities and companies
- **Danmarks Statistik (statistikbanken)**, **Transportvaneundersøgelsen**, **Landstrafikmodellen** — Danish national statistics/travel-survey/traffic-model sources
- **LER (Ledningsejerregistret)**
- **Konkurrence- og Forbrugerstyrelsen** — Danish Competition and Consumer Authority
- **Dansk e-Mobilitet, Drivkraft Danmark, Forenede Danske Elbilister (FDEL), FDM, DTU** — consulted expert/industry bodies
- **plugshare.com, elbilviden.dk, virk.dk** — referenced online tools/portals

## Notes on Extraction Limitations
- This handbook contains numerous figures (Figur 1.1 through Figur 12.4) combining diagrams, photographs, and tables. Where a figure's content is primarily textual/tabular (e.g., Figur 5.1, 5.2, 6.2, 7.4, 8.4, 10.3), the content has been reproduced in full above. Where a figure is a photograph or diagram whose visual content could not be described beyond its caption (e.g., Figur 3.2–3.5, 6.6, 8.2–8.3, 11.1–11.7, 12.2–12.3), only the caption/photo-credit text captured in the extraction is reproduced, and the underlying image content itself is **not further describable from the available text extraction**.
- Figur 3.7 (Dansk Energi grid-load principle illustration) and Figur 3.8 (P3 Charging Index rapid-charging profile comparison chart) are referenced with their source citations and the specific data points discussed in the surrounding prose (e.g., Tesla Model 3 vs. Mercedes-Benz EQA250 charging curves) reproduced above; the charts' full axis/legend detail beyond what is narrated in text could not be independently verified from the extraction.
- Two footnoted analyses of EV-purchase barriers (Rambøll's autumn 2020 survey) and CO2-requirement mechanics (FDM 2020) are referenced by URL in the source but their full content was not part of this document's extracted text.
