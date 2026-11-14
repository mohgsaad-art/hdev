# Van Data Analysis — Where Vans Park Overnight

**Source file:** `Dataanalyse af varebiler.pdf`
**Category:** Data report / vehicle fleet & charging-infrastructure study
**Original language:** Danish (translated to English below; proper nouns kept in Danish)
**One-line summary:** A December 2023 Region Hovedstaden / COWI report combining three Danish data sources (vehicle register, national travel survey, and Connected Cars telematics) to determine where vans in Denmark are parked overnight and thus where home/depot charging infrastructure is needed.

## Publication Details
- **Publisher:** Region Hovedstaden, Center for Regional Udvikling, **Copenhagen Electric**.
- **Published:** December 2023.
- **Commissioned analysis by:** **COWI** (consulting engineering firm), commissioned by Region Hovedstaden.
- **Contact:** Kongens Vænge 2, 3400 Hillerød; tel. +45 38 66 55 05; email cph-electric@regionh.dk.
- **Geographic scope:** Denmark, with detailed municipal-level data for Sjælland (Zealand) and Region Hovedstaden (Capital Region), and regional-level comparisons across all five Danish regions.

## Purpose
As Danish vans (varebiler) increasingly electrify, charging will mostly need to happen overnight where vehicles are "at home" — but not all vans park at a home address (private driver's home or company address); many are seen parked on public parking areas overnight. No prior analysis existed of van usage patterns or where vans are based when not driving. Region Hovedstaden asked COWI to determine what existing data sources can reveal about vans' access to charging.

## Data Sources (Three, Each Partial)
1. **Det danske bilregister** (Danish Vehicle Register) — special extract by **Danmarks Statistik** (Statistics Denmark), showing registered postal code (postnummer) of owners and users of Danish vans.
2. **Transportvaneundersøgelsen** (Danish National Travel Survey) — survey data on where Danes park their car at their own (private) residence; does not identify which specific vehicles are parked.
3. **Connected Cars** — a company providing vehicle telematics/tracking data at the trip level (start/end point and time); COWI has a data-sharing agreement giving real-time access, filterable to vans only.
No single source alone reveals van charging access; the report combines insights from all three.

## Data Source 1: Danish Vehicle Register

### Registration Categories
Vehicles registered under one of: **Godstransport** (goods transport), **Mandskabs-/Materielkørsel** (personnel/equipment transport), **Privat personkørsel** (private passenger use), **Særlig anvendelse** (special use). Both an owner (ejer) and a user (bruger) are registered — not necessarily the same entity (e.g., owner = leasing company, user = transport company or craftsman); the "user" registered is often a company, not the actual individual driver. Postal code is recorded for both owner and user. The extract did not break down vans by industry/sector (branche) — the report notes this could help refine charging need estimates, since goods-delivery vans typically carry no valuable tools (unlike craftsmen's vans) and could more safely park overnight in unmonitored/unsecured areas.

### Key Registration Statistics
- **Approximately 97%** of vans nationally are registered for goods transport (godstransport).
- Little variation across municipalities; **Hjørring Kommune** has the lowest share at **90%** registered for goods transport.
- It is **not possible to distinguish** between vans used for traditional goods delivery vs. craftsman/tradesman use, since both are typically registered as "godstransport."

### Regional/Municipal Distribution
- Van distribution broadly follows population distribution across regions; most vans registered in **Region Hovedstaden** and **Region Midtjylland**.
- In Region Hovedstaden, **20%** of vans are registered in **Københavns Kommune**.
- Other high-count municipalities in the Copenhagen western suburbs ("vestegn"): **Glostrup** (5,400 vans), **Brøndby** (4,400 vans), **Rødovre** (3,500 vans), **Albertslund** (3,900 vans), **Høje-Taastrup** (~5,000 vans).
- Full municipal-level detail for all Sjælland municipalities given in Bilag 1 (Appendix 1 — reproduced below).

### User vs. Owner Share (Figur 3)
Region Hovedstaden has a high share of "bruger" (user, as distinct from owner) registrations at **49%**. Particularly high in suburban municipalities: **Albertslund (80%)**, **Herlev (74%)**, **Glostrup (71%)** — possibly linked to logistics companies concentrated in these areas, though this cannot be confirmed from data alone.

## Data Source 2: Transportvaneundersøgelsen (National Travel Survey)

### Survey Question Used
"Hvordan er parkeringsmulighederne ved din bolig?" (What are the parking options at your residence?) with response categories spanning: carport/garage on own land; front yard/driveway on own land; various reserved/shared parking-lot conditions (always/normally/rarely available, free or paid, time-limited or not); street-only parking under similarly varied conditions.

### Grouping Methodology (for the "Ladepunktsberegner")
**DTU** (Technical University of Denmark), **Dansk e-Mobilitet**, and **Hybrid Greentech** developed a grouping of these parking categories for the so-called **Ladepunktsberegner** (Charging Point Calculator; reference: https://elbilviden.dk/offentlig/ladeinfrastruktur/ladepunktsberegner-til-kommuner/), into three categories:
- **Egen grund** (Own land): can park in driveway, carport, or garage on own property
- **Ved ejendommen** (At the property): good parking conditions in a lot at/near the property, normally or always with a free spot
- **Andre** (Other): parks on the street or has poor conditions at/near the property

**Assumption stated:** private charging facilities can be established when parking is on own land; may be possible with a reserved numbered parking space (requires involvement of others beyond the vehicle user). Only categories including "på egen grund" (on own land) are counted toward home-charging potential in this analysis.

### National and Municipal-Level Results

**National split:** 78% of car owners have access to parking on own land; 13% have parking access at the property; 9% (remainder) park on the street or elsewhere. (Note: text states both "78%"/"79%" and "9%"/"8%" in different places — see Table 1 below reproduced exactly as given, including this apparent internal inconsistency between the narrative text figures and the table figures for "Hele landet".)

**Table 1 — Parking distribution from Transportvaneundersøgelsen** (light-grey rows in original = municipalities outside Region Hovedstaden; preserved here via note)

| Kommune | Parkering på egen grund | Parkering ved ejendom | Andet |
|---|---|---|---|
| Hele landet (Whole country) | 79% | 13% | 8% |
| Region Hovedstaden | 70% | 19% | 11% |
| Aalborg Kommune *(outside Region H)* | 74% | 16% | 10% |
| Aarhus Kommune *(outside Region H)* | 66% | 19% | 15% |
| Albertslund Kommune | 69% | 23% | 8% |
| Allerød Kommune | 82% | 13% | 5% |
| Ballerup Kommune | 69% | 25% | 6% |
| Brøndby Kommune | 60% | 31% | 9% |
| Dragør Kommune | 78% | 14% | 8% |
| Egedal Kommune | 78% | 16% | 6% |
| Fredensborg Kommune | 84% | 10% | 6% |
| Frederiksberg Kommune | 16% | 24% | 60% |
| Frederikssund Kommune | 86% | 9% | 5% |
| Furesø Kommune | 76% | 17% | 7% |
| Gentofte Kommune | 65% | 11% | 24% |
| Gladsaxe Kommune | 57% | 25% | 18% |
| Glostrup Kommune | 69% | 23% | 8% |
| Greve Kommune | 81% | 15% | 4% |
| Gribskov Kommune | 90% | 6% | 4% |
| Halsnæs Kommune | 84% | 10% | 6% |
| Helsingør Kommune | 72% | 18% | 10% |
| Herlev Kommune | 69% | 23% | 8% |
| Hillerød Kommune | 73% | 20% | 7% |
| Hvidovre Kommune | 60% | 29% | 11% |
| Høje-Taastrup Kommune | 68% | 24% | 8% |
| Hørsholm Kommune | 70% | 22% | 8% |
| Ishøj Kommune | 72% | 21% | 7% |
| Københavns Kommune | 21% | 21% | 56% |
| Lyngby-Taarbæk Kommune | 62% | 22% | 16% |
| Roskilde Kommune | 75% | 18% | 7% |
| Rudersdal Kommune | 72% | 20% | 8% |
| Rødovre Kommune | 57% | 31% | 14% |
| Solrød Kommune | 80% | 14% | 6% |

Notable extremes cited in text: Københavns Kommune 21%, Frederiksberg Kommune 16% (lowest "own land" access); Frederikssund Kommune 86%, Gribskov Kommune 90% (highest).

**Limitation stated:** the Transportvaneundersøgelsen data does not distinguish which type of vehicle the respondent has access to, nor whether the respondent might drive a van owned by their employer that is parked at the company's address.

## Data Source 3: Connected Cars (Telematics)

### Methodology
- COWI has an agreement with Connected Cars for real-time trip data, filterable to vans only.
- Overnight parking identified via: trips inspected over one month (**May 2023**); a "parking" event defined as the last trip of the day ending after **15:00**, with the vehicle stationary for a **minimum of 8 hours** before the next trip starts.
- To maximize observations, parkings across the entire month were included (a single van may appear multiple times); summing over a full month is treated as representative of overnight parking patterns.
- **Total dataset: 80,784 overnight parkings across 6,946 unique vans** — averaging approximately **11.5 observations per van**.
- Using GPS coordinates and **BBR** (Bygnings- og Boligregistret — Danish Building and Dwelling Register) data, each parking location was classified by building/area-use type (e.g., multi-story housing, office building, road area, etc.) with a stated degree of precision.
- **Privacy/GDPR note:** data cannot be presented down to individual address level; because the sample (~7,000 vans) is limited, municipal-level breakdowns were judged too uncertain, so results are aggregated only at national and regional level.
- Figur 4 (map) shows overnight parking locations are roughly evenly spread nationally, with a clear (expected) concentration near larger cities (Copenhagen, Aarhus, Aalborg), consistent with higher van registration counts there.

## Section 3: Home-Charging Potential

- Figur 5 compares, by region, the number of registered van users against the calculated home-charging potential (using the Transportvaneundersøgelsen "own land" access assumption).
- Finding: the challenge of home-charging is **significantly greater in Region Hovedstaden**, and to a lesser extent in **Region Midtjylland** — attributed to these regions being dominated by Copenhagen and Aarhus respectively, where a higher share of residents live in multi-story buildings (etageejendomme) than in other regions.
- Figur 6 (municipal-level) highlights municipalities with large shares of multi-story housing as most affected: **København, Frederiksberg, Gladsaxe, Brøndby, Albertslund, Glostrup, Høje-Taastrup, Hvidovre**. Conversely, small gaps in municipalities dominated by single-family housing: **Vallensbæk, Egedal, Halsnæs, Allerød**.
- Many vans operating in Region Hovedstaden are expected to belong to users residing in **Region Sjælland** — for these, home-charging access matters even more, since vans need to arrive at their Region Hovedstaden workplace/depot already charged at day start. Figur 7 shows the balance is less problematic across remaining Sjælland municipalities generally, though **Greve Kommune** shows a large deficit of private charging access, while **Solrød Kommune** shows a large surplus. Larger Region Sjælland cities with more multi-story housing again stand out as more constrained.
- Figur 8: grouping by geography around Copenhagen as a work area — **up to 15,000 vans in Storkøbenhavn (Greater Copenhagen)** have neither access to charging on own land (for residential purposes) nor via a housing association (boligforening). Some of these may be parked at the owning company's premises (addressed in Section 4). The surrounding commuter belt (oplandet) also shows a notable but smaller number of vans without ready charging access.

## Section 4: Where Vans Are Located at Night (Connected Cars Analysis)

**Table 2 — Share of overnight parking by area/building type, by region** (dark shading in original = clearly private areas; light shading = typically public areas; unshaded = could be either — preserved via labels below)

| Area/building type | Hovedstaden | Sjælland | Syddanmark | Midtjylland | Nordjylland | Total |
|---|---|---|---|---|---|---|
| Buildings for year-round residence (Bygninger til helårsbeboelse) *[private]* | 23% | 41% | 42% | 40% | 35% | 34% |
| Year-round residence — multi-story/multi-family building (Etagebolig-bygning, flerfamiliehus eller tofamiliehus) *[private]* | 13% | 5% | 4% | 2% | 4% | 7% |
| Buildings for transport and parking (Bygninger til transport og parkering) | 6% | 4% | 1% | 6% | 8% | 5% |
| Buildings for office, retail, and warehouse (Bygninger til kontor, handel og lager) | 11% | 16% | 23% | 21% | 25% | 18% |
| Buildings for hotel, restaurant, and service | 1% | 1% | 1% | 1% | 2% | 1% |
| Buildings for education and research | 1% | 1% | 0% | 0% | 0% | 1% |
| Buildings for hospital and health | 0% | 0% | 1% | 0% | 0% | 0% |
| Buildings for institutional purposes | 0% | 0% | 0% | 0% | 0% | 0% |
| Buildings for holiday purposes | 1% | 3% | 1% | 1% | 2% | 1% |
| Buildings for sports and athletics | 0% | 0% | 1% | 0% | 0% | 0% |
| Buildings for leisure purposes | 1% | 1% | 0% | 0% | 0% | 1% |
| Buildings for commercial production — agriculture, horticulture, forestry, fishing | 14% | 10% | 10% | 11% | 8% | 11% |
| Road area (Vejareal) *[public]* | 16% | 9% | 10% | 7% | 9% | 11% |
| Other (parcels with no designated use) | 13% | 9% | 8% | 9% | 6% | 10% |
| **Total** | 100% | 100% | 100% | 100% | 100% | 100% |

### Key Observations from Table 2
- Share of vans parked at private residences (combining year-round residence categories) is **at most 41%** of parkings nationally — notably lower than the Transportvaneundersøgelsen-based estimate — indicating roughly **40%** of vans park at a home address. Uncertainty noted: some parking on road areas or other unspecified areas could still be vans taken home by drivers but parked elsewhere; if included, **up to 60%** of vans could be taken home by drivers.
- Share of vans parked at private residences is **lower in Region Hovedstaden** than other regions: only **23%** parked at a private residence with own land, plus a smaller share at multi-story/row housing. Region Hovedstaden also has a higher share of parking on road areas or areas of unknown purpose.
- A relatively large share of vans appear parked at company addresses. If "buildings for transport and parking" plus "buildings for office, retail, and warehouse" are treated as such areas, **34%** of vans are parked at company-owned premises. Region Hovedstaden shows a somewhat smaller share parked at companies, linked to more companies lacking sufficient on-site parking space.

### Summary Bullets (as stated in source)
- Relatively large number of vans parked in locations where charging cannot be readily established — even if companies wanted to.
- A share of vans are parked in public areas (roads, parking lots, areas with no specific designated use).
- The share of vans on public areas is large in Region Hovedstaden: **29%** of vans overnight on road areas or unspecified areas.
- Approximately **one-third** of vans are parked at a location interpretable as the company the vehicle is associated with; this picture varies only slightly across regions.

## Conclusion (Section 5)
- Many considerations about electrifying commercial transport assume vehicles can start the day with a full charge — for many vans, this means charging where the vehicle is parked overnight.
- Many stakeholders point to van charging as a challenge because vehicles are taken home by users, many of whom do not live somewhere charging can be installed.
- Data confirms this: many vans are registered in municipalities with a relatively high share of multi-story building stock and low access to own-land parking — a particular challenge in Region Hovedstaden, especially its two central municipalities (København og Frederiksberg), and to some extent the Copenhagen western-suburb municipalities.
- Nationally, data suggests a significant share of vans cannot readily access overnight charging. However, more than one-third of vans park at the company/organization registered as owner or user of the vehicle, and nationally about one-third park at the user's own private residence.
- **Combined conclusion:** approximately **one-third of vans** need charging infrastructure established by parties other than the user or the company itself — potentially a housing association (~7% of vans), though a large share park in locations with no direct relationship to the landowner.
- This challenge is **greater in Region Hovedstaden**: substantially fewer vans park on own land at a residence or at a company; roughly **twice as many vans** park at a multi-story building/housing association compared to the national average, and **a quarter of vans** park on the street or another unspecified location.

## Appendix 1 (Bilag 1) — Municipal Data Table, All Sjælland Municipalities

**Table — Vans registered, user share, home parking access, home-charging potential**

| Kommune | Antal varebiler | Andel brugere | Parkering på egen grund | Potentiale for hjemmeladning (antal varebiler) |
|---|---|---|---|---|
| København | 16,457 | 48% | 21% | 1,675 |
| Frederiksberg | 1,989 | 39% | 16% | 123 |
| Glostrup | 5,434 | 71% | 69% | 2,668 |
| Brøndby | 4,354 | 63% | 60% | 1,659 |
| Rødovre | 3,150 | 52% | 57% | 941 |
| Albertslund | 3,897 | 80% | 69% | 2,154 |
| Vallensbæk | 586 | 57% | 78% | 258 |
| Høje-Taastrup | 5,029 | 54% | 68% | 1,832 |
| Ishøj | 1,605 | 54% | 72% | 627 |
| Hvidovre | 3,607 | 55% | 60% | 1,195 |
| Greve | 3,988 | 55% | 81% | 1,778 |
| Solrød | 1,172 | 44% | 80% | 413 |
| Herlev | 2,838 | 74% | 69% | 1,450 |
| Ballerup | 3,539 | 62% | 69% | 1,517 |
| Egedal | 2,473 | 40% | 78% | 768 |
| Tårnby | 3,164 | 42% | 71% | 954 |
| Lyngby-Taarbæk | 1,699 | 33% | 62% | 346 |
| Gentofte | 2,170 | 37% | 65% | 519 |
| Rudersdal | 2,287 | 35% | 72% | 583 |
| Gladsaxe | 3,955 | 64% | 57% | 1,441 |
| Hørsholm | 1,013 | 36% | 70% | 251 |
| Fredensborg | 1,893 | 36% | 84% | 573 |
| Helsingør | 3,183 | 36% | 72% | 827 |
| Gribskov | 3,498 | 34% | 90% | 1,075 |
| Halsnæs | 2,066 | 31% | 84% | 535 |
| Hillerød | 2,881 | 37% | 73% | 779 |
| Allerød | 1,276 | 42% | 82% | 437 |
| Furesø | 1,372 | 43% | 76% | 445 |
| Frederikssund | 3,667 | 35% | 86% | 1,090 |
| Bornholm | 2,926 | 24% | 88% | 626 |
| Roskilde | 5,543 | 42% | 75% | 1,747 |
| Lejre | 1,624 | 31% | 92% | 467 |
| Ringsted | 2,804 | 40% | 79% | 886 |
| Køge | 4,934 | 34% | 81% | 1,360 |
| Næstved | 5,210 | 28% | 84% | 1,241 |
| Sorø | 2,850 | 32% | 91% | 816 |
| Slagelse | 5,369 | 34% | 77% | 1,386 |
| Kalundborg | 3,714 | 27% | 89% | 888 |
| Holbæk | 5,481 | 31% | 84% | 1,452 |
| Odsherred | 2,866 | 28% | 93% | 747 |
| Faxe | 3,785 | 40% | 87% | 1,314 |
| Stevns | 1,523 | 30% | 92% | 425 |
| Vordingborg | 3,621 | 30% | 89% | 960 |
| Guldborgsund | 4,698 | 24% | 89% | 1,027 |
| Lolland | 3,108 | 23% | 88% | 641 |

## Named Organizations, Tools, Datasets Referenced
- **COWI** — commissioned analysis firm
- **Danmarks Statistik** — Statistics Denmark (vehicle register extract)
- **Transportvaneundersøgelsen** — Danish National Travel Survey
- **Connected Cars** — telematics/tracking data provider
- **DTU** (Danmarks Tekniske Universitet), **Dansk e-Mobilitet**, **Hybrid Greentech** — developers of the "Ladepunktsberegner" (Charging Point Calculator) methodology, https://elbilviden.dk/offentlig/ladeinfrastruktur/ladepunktsberegner-til-kommuner/
- **BBR** (Bygnings- og Boligregistret) — Danish Building and Dwelling Register, used to classify parking-location building types

## Notes on Extraction Limitations
- Figur 1, Figur 2, Figur 3, Figur 5, Figur 6, Figur 7, and Figur 8 are charts/maps referenced in the text; narrative descriptions and the specific figures discussed in surrounding text have been captured above, but exact bar/axis values beyond what is explicitly stated in the prose (e.g., specific percentages named in text) could not be independently verified from image content and are **not further quantified beyond what is stated in the source narrative**.
- The source text shows an apparent minor inconsistency between the "Hele landet" narrative figures ("78%... 13%... resten (9%)") and the Table 1 row for "Hele landet" ("79%... 13%... 8%"). Both are reproduced exactly as they appear in the source rather than reconciled, per instruction not to alter source figures.
