# Outputs and facts to carry into EV Scope (from earlier chats, shared by Bob 28 Oct 2026)

Saved as Bob shared it. Prices and rules are as stated in that chat with its sources; re-check before use.

## 1. New outputs we need now

These are the outputs the three NOW products need that the engine or mock-up doesn't produce yet. Everything here came out of the documents and research in this chat.

**Every report**
- **Receipt block:** engine version, a fingerprint of the inputs, and every default value with its source.
- **A label on every number:** measured, standard value, or assumption.
- **A status line per result:** validated, in testing, or not built.

**Second Opinion pack**
- **Energy split** (air, rolling, hills, brakes, drivetrain, heating, PTO) and a **monthly table**, like PVsyst's.
- **A normal day vs a bad day** (P50/P90 across weather years).
- **Usable vs nominal battery.** Tenders specify usable capacity, and the EEA data gives a usable figure per vehicle.
- **The year-8 check:** does the hardest day still fit with the battery at its guaranteed capacity (e.g. 80%)?
- **Charging:**
  - kW per truck and for the whole depot;
  - whether the truck can charge at ≥150 kW between 10% and 75% (the crane-truck tender demands this);
  - how much spare time there is before 06:00.
- **Grid:**
  - connection size in **amperes and kW**;
  - the customer category (C, B-lav, B-høj, A-lav, A-høj);
  - the **connection fee from the price list**;
  - full vs limited access (FNA vs BNA) side by side;
  - a lead-time band;
  - the capacity charge (average of the 10 busiest hours) with and without smart charging.
- **Cost:**
  - the Danish km-toll by CO₂ class (it extends to trucks ≥3.5 t from 1 Jan 2027);
  - diesel under ETS2 from 2028;
  - NPV using Vejdirektoratet's rule, where year 1 is discounted one full period.
- **Grant-ready numbers:** budget lines, how many trucks charge each day, and the number and power of chargers.

**Tender help**
- **Minimum usable kWh at year 8 in winter for these routes,** shown on the tender's own score curve (e.g. 250→450 kWh scoring 1→10 points).
- **Crane and compactor running at the same time:** the energy and the peak power.
- **Battery vs payload trade-off.** Both are scored, and a heavier battery means less load.
- **An offer sheet:** several bids run on the same routes, scored with the buyer's weights.
- **Spare-truck count** for a cold week.

**Crane/compactor energy sheet**
- kWh per lift or compaction cycle, kWh per shift, and peak kW, exported as a profile in VECTO's PTO file format.

**Hold back:** don't give a firm winter verdict until cold-weather cabin heating is modelled and tested. Until then, show winter only as a labelled conservative scenario.

## 2. FNA vs BNA, plainly

**FNA (full access):** you pay a one-off connection fee. Your power is guaranteed at all times, even when grid equipment fails or is being repaired.

**BNA (limited access):** you pay only for your own connection, not for capacity further up the grid. In return, the grid company can cut your power when the grid is busy.

**How much they can cut back** (Cerius's own terms):
- anything from **0 to 100%** of your connection;
- **at any time, without warning**, and usually without telling you why or for how long;
- **with no compensation;**
- if the cut becomes permanent, it lasts indefinitely and can go all the way to zero;
- if you ignore their signals, they disconnect you.

Only sites big enough for **10 kV or above** qualify. You can't convert an existing full connection to limited access, and you can't buy limited capacity for a future need. You can switch from limited to full later, but you pay the normal fee and may have to wait for the grid to be built out.

**What it costs: Cerius connection fees from 1 Jan 2026, incl. VAT**

| Category | Price |
|---|---|
| First 25 A (C, B-lav, B-høj) | DKK 23,500 flat |
| C | DKK 1,812.50 per A |
| B-lav | DKK 1,737.50 per A |
| B-høj | DKK 1,675 per A |
| A-lav | DKK 1,637,500 per MVA |
| A-høj | DKK 900,000 per MVA |

These match the Radius guide's examples:
- adding 35 A on C: 35 × 1,812.50 ≈ DKK 63k;
- 175 A on B-lav: 175 × 1,737.50 ≈ DKK 304k;
- 3 MW on A-lav: 3 × 1,637,500 ≈ DKK 4.9m.

Limited access has **no published price**. You pay your own cable and equipment, plus Cerius's fees for case handling, connection, communication and metering. In Radius's 3 MW example, choosing limited access would have avoided most of the DKK 4.8m. *Not verified:* that Radius's prices are exactly the same as Cerius's. The two operate as Cerius-Radius, and the guide's examples match these prices.

**Pros and cons**

| | Full access (FNA) | Limited access (BNA) |
|---|---|---|
| **Pros** | Power always there, so trucks are ready by 06:00. Simple to plan. | Much cheaper upfront. *Inference:* may connect sooner where the grid is full, because nothing upstream has to be built. Can upgrade later. |
| **Cons** | Big fee (millions at MW scale). May wait years for grid reinforcement. | Cuts of 0–100% at any time, no warning, no compensation. Needs controllable chargers, and often a buffer battery or diesel backup. Only for 10 kV and above. |
| **Suits** | Depots that must deliver every morning (Radius's example customer chose this for that reason). | Depots with long overnight dwell, flexible charging, or a battery on site. |

Cerius-Radius planned to expand limited access in 2026, then pushed the bigger expansion to **2027** (Transportmagasinet, 2 Sep 2026).

**For EV Scope:** the key BNA question is "how big a cut can my depot survive and still be ready by 06:00?". Nobody publishes how often cuts happen, so you'd answer it with labelled what-if cases ("a 50% cut from 22:00 to 02:00"), not a forecast.

## 3. The battery passport

**What's known:**
- **When:** required from **18 Feb 2027** for EV batteries placed on the market, including truck and bus packs. It also covers replacement packs fitted from that date. Trucks delivered earlier don't need one.
- **The standard:** the format is defined by DIN DKE SPEC 99100, published in 2025 with the Battery Pass consortium. It lists the data points and their structure.
- **What it contains:**

| Group | Examples | Changes over time? |
|---|---|---|
| Identity | Pack ID, maker, model, date and place of manufacture | No |
| Materials | Chemistry, critical raw materials, hazardous substances | No |
| Performance and durability | Rated capacity (Ah) and fade rate; power and power fade; internal resistance and its increase; round-trip efficiency; expected lifetime in cycles or years | No (design values) |
| Health and use | State of health (for EVs, a "state of certified energy" estimate, as a %), usage history, pack swaps | **Yes, kept up to date** |
| End of life | Disassembly, recycling route | No |
| Later dates | Carbon footprint (waiting for EU calculation rules), due diligence (18 Aug 2027), recycled content (18 Aug 2028) | |

- **Who sees what:**
  - **Public:** pack ID, capacity, contractual service life, end of life.
  - **Only people with a "legitimate interest":** chemistry, state of health per pack, usage history. The fleet owner should be able to give you access, but the exact rules on who qualifies aren't final.
- **Already true since Aug 2024:** EV battery management systems must store the data needed to judge state of health and expected lifetime, with read-only access for the owner or someone acting for them.

**Still open:** how often the health data must be updated, the exact legitimate-interest rules, and the carbon-footprint method.

**How to prepare early, cheaply:**
1. **Use the passport's field names in your own battery data model** (rated capacity, capacity fade, internal resistance, round-trip efficiency, expected cycles/years, state of health). The EEA data and spec sheets then slot straight in, and so will real passports later.
2. **Have the engine output the same usage quantities the passport tracks,** per route: energy throughput, full equivalent cycles, charging rates, and time at very hot or cold temperatures. Your report then predicts what a truck's passport *should* look like after 8 years.
3. **Add a contract clause now** letting clients share BMS or passport data with you. It feeds the proof record and the later resale-value and used-truck products.
4. **Next step:** read DIN DKE SPEC 99100 itself (VDE/DIN publish it) to get the exact field list before building the data model. I haven't read it yet.

Sources:
- [Cerius: limited access (BNA)](https://cerius.dk/ny-tilslutning/tilslutning/typer-af-tilslutninger/begraenset-netadgang/)
- [Cerius: business connection fees 2026](https://cerius.dk/ny-tilslutning/tilslutning/tilslutningsbidrag-erhverv/)
- [Transportmagasinet: BNA expansion postponed](https://www.transportmagasinet.dk/article/view/1243816/eftertragtet_ordning_kan_afhjaelpe_elnetko_nu_udskydes_nye_tilslutninger)
- [Energy Supply: Cerius-Radius expands BNA](https://www.energy-supply.dk/article/view/1211381/mens_kunder_star_i_ko_til_elnettet_ceriusradius_skruer_op_for_saerlig_ordning)
- [Radius guide](https://radiuselnet.dk/wp-content/uploads/Saet-stroem-til-den-tunge-transport_2025-1.pdf)
- [Arianee: passport for buses and trucks](https://www.arianee.com/en/solutions/batteries/buses-trucks)
- [TWAICE: EU battery passport](https://www.twaice.com/article/eu-battery-passport)
- [VDE: DIN DKE SPEC 99100](https://www.vde.com/en/press/press-releases/din-dke-spec-99100-battery-pass)