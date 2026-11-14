# Clarification of the Concept of "Netvenlighed" (Grid-Friendliness)

## Source document metadata

- **Original title (Danish):** "Begrebsafklaring af begrebet 'netvenlighed'" (lit. "Conceptual clarification of the term 'netvenlighed' [grid-friendliness]")
- **Publisher(s):** Cerius A/S (CVR-nr. 2811 3285) and Radius Elnet A/S (CVR-nr. 2991 5458) — both Danish electricity **distribution system operators (DSOs)**, sharing the address Teknikerbyen 25, 2830 Virum, with head office ("Hovedkontor") at Hovedgaden 36, 4520 Svinninge. These are DSOs in the Danish grid group commonly known as Cerius/Radius (part of the former Ørsted/Radius distribution grid, now under the Andel/Eurogrid ownership structure — ownership not stated in the document; [unclear from source]).
- **Date:** 23 April 2026
- **Document type:** A short technical/regulatory position note ("notat"), 4 pages, addressed implicitly to the regulator (Energistyrelsen — the Danish Energy Agency) as input to ongoing grid-connection prioritization regulation.
- **Length extracted:** Full document (all content returned inline via `project_read`; no page-by-page PDF extraction was needed as the complete text was provided).

## Why this document matters for the HDEV sizing & modelling tool

**This note is directly relevant to depot/fleet charging design.** It argues that Danish grid-connection **prioritization** of new connection requests (nettilslutningsanmodninger) — which will determine how easily and how favorably a depot or fleet charging site can get connected/upgraded — should NOT be judged by a single vague "netvenlighed" (grid-friendliness) score. Instead, the DSOs propose splitting the concept into two clearly separate technical categories:

1. **Kapacitetsvenlighed** (capacity-friendliness) — relevant to local/distribution grid capacity (cables, transformers, voltage), i.e., exactly the constraint that governs how large a depot charging installation can be and when it can charge.
2. **Systemvenlighed** (system-friendliness) — relevant to whole-system balancing services (frequency reserves, aFRR/mFRR, spot-price responsiveness), which is a *different* value stream that flexible EV/HDEV charging or V2X could also provide, but which does **not** automatically relieve local grid congestion — and can even worsen it.

For HDEV depot design, this means: **being "smart"/flexible in a way that earns system-service revenue (e.g., FCR, aFRR/mFRR, spot-price response) is not the same as being favorable for local grid connection approval**, and depot charging strategies optimized for one may actively conflict with the other (see "coincidence/simultaneity" discussion below). Any sizing tool should model these as two distinct axes, not conflate them.

## Context and purpose of the note

The note states that the term "netvenlighed" has recently acquired a **central role in the prioritization of grid connection requests** (nettilslutningsanmodninger), due to:

1. **Energistyrelsen's guidance** (vejledning), cited via footnote as: `https://ens.dk/media/7862/download` — referred to only as "Energistyrelsens vejledning" (Danish Energy Agency's guidance); exact title/number not given in the note text itself [unclear from source — only the URL and generic description are provided].
2. **The European Commission's "Grid Packages"**, cited via footnote as: "Meddelelse fra Kommissionen — Vejledning om effektiv og rettidig nettilslutning" (Communication from the Commission — Guidance on efficient and timely grid connection).

The DSOs' concern: the term "netvenlighed" is currently used in a **broad and partly imprecise sense**, blending together different technical properties. This creates a risk that regulation will not adequately reflect the underlying physical and system-technical realities of the electricity system. The note's stated purpose is to argue that Energistyrelsen should, in its regulation, **clearly separate** the two categories below to enable **targeted criteria** reflecting the distinct technical considerations.

## The two categories

### 1. Kapacitetsvenlighed (Capacity-friendliness)

**Concerns:** A facility's ("anlægs") impact on the **physical grid infrastructure** — cables and transformers — i.e., the grid's ability to transport power without overload.

**Characterization given in the note:**
- A capacity-friendly facility is one that **reduces or shifts load away from times and/or locations in the grid where relevant grid components already experience high loading**.
- Example given: flexible electricity consumption that adapts so it does not increase loading in parts of the grid that are already capacity-constrained.
- **Precondition:** the facility must be **regulable or interruptible** (regulerbart eller afbrydeligt) — otherwise, a large consumption load in a production-dominated (e.g., wind/solar-heavy) area could itself create capacity problems during hours when there is neither wind nor solar production in that area.
- Directly tied to **classical grid planning / dimensioning criteria**: coincidence/simultaneity (samtidighed), the facility's technical capability, and voltage conditions.

**Proposed definition (the DSOs' own suggested wording, explicitly framed as "a proposal for a definition" — "Et bud på en definition"):**

> "Kapacitetsvenlighed betegner et anlægs evne til at tilpasse sin effektudveksling med elnettet i overensstemmelse med nettets fysiske overførselskapacitet, således at belastningen reduceres eller forskydes væk fra tidspunkter og/eller netområder med høj samtidighed og risiko for overbelastning. Et kapacitetsvenligt anlæg er karakteriseret ved regulerbar eller afbrydelig drift og bidrager til, at dimensioneringskriterier for kabler, transformere og spændingsniveauer overholdes i den fysiske netinfrastruktur."

English (working translation, not an official translation): *"Capacity-friendliness denotes a facility's ability to adapt its power exchange with the electricity grid in accordance with the grid's physical transmission capacity, such that load is reduced or shifted away from times and/or grid areas with high coincidence/simultaneity and risk of overload. A capacity-friendly facility is characterized by regulable or interruptible operation and contributes to compliance with dimensioning criteria for cables, transformers, and voltage levels in the physical grid infrastructure."*

### 2. Systemvenlighed (System-friendliness)

**Concerns:** A facility's contribution to the **overall electricity system's dynamic function, system-supporting properties, and balancing**, e.g. through delivery of system services (systemydelser).

**Characterization given in the note:**
- System-friendly facilities can, for example, deliver **frequency reserves (FCR-N, FCR-D)** or rapid changes in consumption/production in response to system balancing needs (**aFRR/mFRR**).
- These properties are essential for maintaining production/consumption balance in real time, overall security of supply, and agreed exchange with interconnected countries.
- Primarily tied to the facility's ability to **respond to signals from Energinet** (the Danish TSO) and contribute to system-level balance.
- Some system services — notably slower reserves like **mFRR** — may in practice be activated with consideration for transmission-grid bottlenecks (e.g., using **geo tags**), giving them an incidental load-relieving or load-steering effect locally. **However, this does not mean system-friendliness itself addresses distribution-grid capacity conditions**, or conditions at the transmission/distribution interface. Delivering system services is therefore **not synonymous with local netvenlighed** (grid-friendliness), which still depends on the concrete loading conditions of the specific relevant grid components.
- System services can also have **other negative impacts**, notably **fast, unintended voltage changes**. Example given: two facilities located in the same 10 kV grid but at two different addresses could create challenges related to unintended fast voltage changes when delivering fast-reacting system services — **even where transfer capacity (measured in amperes) is otherwise available**. (This illustrates that thermal/ampere capacity being sufficient does not guarantee voltage-quality compliance.)
- Facilities that respond to **spot prices** are also characterized as system-friendly, because they enable further integration of wind and solar, reduce the need for regulable capacity, and have a **price-equalizing effect** for the whole system. Notably, the note states this form of system-friendliness **can be either capacity-friendly or capacity-unfriendly**, depending on the facility's location, the volume of such facilities, and the surrounding load profile in the area.

**Proposed definition:**

> "Systemvenlighed betegner et anlægs evne til at bidrage til elsystemets dynamiske stabilitet og balance gennem hurtig, præcis og styrbar regulering af effekt som respons på systembehov og aktiveringssignaler."

English (working translation): *"System-friendliness denotes a facility's ability to contribute to the electricity system's dynamic stability and balance through fast, precise, and controllable power regulation in response to system needs and activation signals."*

System-friendliness is thus tied to the facility's **regulation properties, regulation signals, and response speed**, and is **independent of local grid-capacity conditions** — deliveries can have a neutral, relieving, or burdening effect on the physical grid infrastructure depending on activation pattern and geographic location.

## Key structural difference between the two categories

The note stresses this is not merely a theoretical distinction but has **concrete consequences for both grid planning and operation**:

- **Capacity-friendly** facilities *reduce* grid loading.
- **System-friendly** facilities, in many cases, require that their **full capacity can be activated quickly and often simultaneously with other facilities** — i.e., they can be system-friendly while simultaneously creating challenges for local grid capacity and/or local grid conditions (e.g., fast voltage changes).

## Coincidence/simultaneity (samtidighed) — the central grid-planning issue

This is presented as the most significant grid-planning challenge posed by system-friendly facilities:

- Traditional distribution-grid dimensioning relies on the assumption that not all consumers are active at full power simultaneously — reflected in **coincidence/simultaneity factors** (samtidighedsfaktorer) that reduce expected maximum load relative to installed capacity.
- System services challenge this assumption because they are assessed/expected to activate **in response to shared system-wide signals** — meaning multiple facilities behind the same connection point can increase or decrease their power **suddenly, unpredictably, and simultaneously**.
- A **high concentration (volume and/or number) of facilities delivering system services through the same grid components** can significantly increase the degree of coincidence. Such facilities, despite their system-level value, may in practice be **less capacity-friendly** than ordinary consumption/production, which is typically more spread out and far less synchronized in behavior.
- Dimensioning the grid for fully coincident maximum load from all connected facilities would require very large, and in practice largely superfluous, investments in electricity infrastructure. Exploiting the fact that not all load (or production) typically peaks simultaneously allows for more efficient, lower-cost grid dimensioning for consumers.

### Worked example given in the note (transformer overload scenario)

> Three facilities of 300 kW each installed behind a single transformer with a capacity of **630 kVA**. Combined installed capacity (3 × 300 kW = 900 kW) exceeds transformer capacity if all three activate simultaneously.
>
> - In a **traditional consumption** scenario, this would not necessarily be problematic, because coincidence is lower — it is unlikely all three would use full power at the same time.
> - For **system services**, however, dimensioning must assume a scenario of **high coincidence and high unpredictability** in the facility's load profile — challenging DSOs' standard dimensioning practice and potentially leading to **overload of existing transformers and/or cables**, and to **breaches of power-quality (elkvalitet) limit values**.

| Parameter | Value |
|---|---|
| Number of facilities behind transformer | 3 |
| Capacity per facility | 300 kW |
| Combined installed capacity | 900 kW |
| Transformer capacity | 630 kVA |
| Traditional-consumption assumption | Low coincidence — not necessarily problematic |
| System-service assumption | High coincidence + high unpredictability — must be dimensioned for worst case |

*(Note: figures as stated in source; 630 kVA is an apparent-power unit while 300 kW facilities are active-power — the note does not reconcile power factor/kVA-vs-kW conversion; treat this as the source's own illustrative simplification, not a precise engineering calculation. [Flagged as a simplification present in the source itself, not one introduced by this summary.])*

## Operational (not just planning) challenges from system-friendly facilities

- **Relay protection (relæbeskyttelse):** Protection systems detect faults based on current/voltage levels and their time evolution. Fast, coordinated power changes across multiple facilities can create transients that are either misinterpreted as faults or that mask real faults — leading to unwanted trip-outs (udkoblinger).
- **Thermal stress:** Thermal loading of cables and transformers can increase; mechanical components can be subjected to extra stress.
- **Worst case:** Cascading trip-outs (kaskadeudkoblinger), increased risk of outages across larger areas, and reduced lifetime of grid components due to steep load changes.
- **Voltage quality (elkvalitet):** Fast-reacting system services can cause local voltage problems that challenge the technical quality standards the DSO is obligated to uphold under the **connection terms/regulations** (tilslutningsbestemmelserne). When a facility suddenly increases feed-in or reduces consumption, voltage at the connection point can change quickly; if multiple facilities do this simultaneously (and/or frequently), the voltage change can become significant and challenge power quality — these dynamic voltage changes can be difficult to manage with traditional regulation methods and can affect power quality for other grid users.

## The DSOs' regulatory recommendation

The note concludes that it is **necessary for Energistyrelsen to clearly separate capacity-friendliness and system-friendliness in its regulation**, to allow targeted criteria reflecting the different technical considerations:

- **For capacity-friendliness**, focus should be on: **local loading** (transfer capability and power quality/elkvalitet), **coincidence/simultaneity**, and **utilization of existing grid capacity**.
- **For system-friendliness**, focus should be on: the facility's **dynamic properties** and its **contribution to electricity-system stability**.

**Stated risk of not separating the concepts:**
- Facilities beneficial to the overall electricity system might be prioritized **without sufficient regard for local grid constraints**.
- Conversely, facilities that effectively reduce local congestion might be **undervalued** if they do not also deliver system services.

The note frames a clear conceptual clarification as **a precondition for regulation that supports both efficient grid utilization and stable overall system operation**.

## Cited legal/regulatory sources (exact references given in the note)

1. **Energistyrelsen's guidance ("vejledning")** — cited only via URL: `https://ens.dk/media/7862/download`. No formal title, executive-order (bekendtgørelse) number, or law number is given in the note text itself. [unclear from source — title/number not stated; would need to retrieve the linked document to identify it precisely]
2. **European Commission — "Meddelelse fra Kommissionen — Vejledning om effektiv og rettidig nettilslutning"** (Communication from the Commission — Guidance on efficient and timely grid connection), referred to in the note's body text as part of the "Europa-Kommissionens Grid Packages" (EU Grid Packages). No CELEX number, publication date, or formal document number is given. [unclear from source]

No other laws, bekendtgørelser, or EU directives are cited by name/number in this document.

## Organizations and stakeholders named

- **Cerius A/S** (DSO, issuer)
- **Radius Elnet A/S** (DSO, issuer)
- **Energistyrelsen** (Danish Energy Agency) — the implicit regulatory addressee; referenced as issuer of the guidance in footnote 1 and as the body that "in its regulation" should separate the two concepts.
- **Europa-Kommissionen** (European Commission) — referenced as issuer of the Grid Packages guidance.
- **Energinet** — referenced as the Danish TSO whose signals system-friendly facilities respond to (for balancing/system services).

No specific examples involving EV charging, HDEV depot charging, or CPOs are given by name in this note — the discussion is generic to "anlæg" (facilities/installations) and "fleksibelt elforbrug" (flexible electricity consumption). The relevance to depot/fleet EV charging drawn out in this summary (see top section) is an **inference by this knowledge-base entry**, not a claim made explicitly in the source document — flagged here explicitly per project instructions.

## Assumptions/simplifications introduced in this extraction

- English definitions of "kapacitetsvenlighed" and "systemvenlighed" are **working translations** by this extraction, not official/authoritative translations — the original Danish wording is preserved verbatim above for precision.
- The kVA vs. kW unit mismatch in the transformer example is present in the source and is flagged, not corrected or reconciled here.
- Ownership structure of Cerius/Radius beyond the address given is not stated in the source and is not asserted here.
- The explicit connection to HDEV/depot charging design (top section) is analytical framing added by this knowledge-base entry to explain relevance to the project's tool — it is not a statement made in the source document.
