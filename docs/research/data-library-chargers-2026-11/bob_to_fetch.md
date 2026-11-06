# Bob to fetch (charger library, pass 1)

Scope note: the brief says list only links **not already** in
`manual-fetch-list-2026-11-06.md`. That file is **not in the repo** (nor is the
`inputs/`/`knowledge-base/` material), so I can't diff against it. When you have
the manual-fetch-list, drop any row already there.

Columns: `what | link | how | why`.

## Highest priority — unlocks whole sections

- **The Danish knowledge-base documents (section 1)** | add to
  `docs/research/inputs/` or `claude/knowledge-base/` | copy from the claude.ai
  project | These hold the real SLA, uptime %, response/fix-time, penalty, price
  and contract-term clauses (sections 3.5, 4.1, Q9). Without them
  `contracts_and_sla.md` cannot be filled. The single biggest gap.
- **Danish AFIR National Access Point** | candidates: the Danish ITS NAP,
  Vejdirektoratet, Energistyrelsen, energidataservice.dk | search "Danmark
  national adgangspunkt ladepunkter AFIR" + check the EC NAP registry page |
  Confirm it exists, its URL, licence, and whether it carries **price** fields.
  If open, it is the best DK `cpo_sites`+`cpo_prices` source (Q1).
- **Current DSO takstblade: Radius, Cerius, N1, TREFOR El-net, Konstant** |
  radiuselnet.dk/elpriser, cerius.dk, n1.dk, trefor.dk/el-net, konstant.dk |
  download current tariff PDFs | Current tilslutningsbidrag per A + TOU net
  tariffs (Lav/Høj/Spids) per customer category. COWI's Radius figure is 2024
  (Q7).

## Regulation / standards

- **AFIR consolidated text (verify article numbers)** |
  http://data.europa.eu/eli/reg/2023/1804/2026-01-08/eng | read Articles 3-4,
  payment, data | Confirm the exact article/paragraph for HDV pools, ad-hoc
  payment thresholds, NAP data, and whether a delegated act added MCS to Annex
  II. EU reuse (open).
- **CharIN MCS 2.0 whitepaper** | charin.global (resources) | download |
  Confirm MCS comms (ISO 15118-20 only), connector, cooling. Confirm licence.
- **SAE J3271 publication status** | sae.org standards catalogue | search J3271 |
  Confirm published vs draft and the exact power/current/voltage it defines.
- **OCA OCPP Certified Products registry** | openchargealliance.org | browse |
  Which charger models are OCPP 2.0.1 certified (per-model `ocpp_certified_flag`).
- **Energinet ancillary-services prequalification** |
  en.energinet.dk/electricity/ancillary-services | download FCR/aFRR/mFRR docs |
  Exact response-time requirements for EV-depot flexibility (Q3, section 3.3).

## OEM datasheets (cite-only; store values, not PDFs)

- Siemens Sicharge D; Ekoenergetyka Axon/ELMo; ADS-TEC ChargeBox; Delta; Autel;
  Circontrol; Zaptec; Efacec; SBRS; Hitachi Energy Grid-eMotion; Kostad;
  Teltonika; Exicom (Tritium). | each OEM site | download current EU datasheet |
  Fill `charger_power_specs` / `charger_comms`; capture standby W + ramp if any
  OEM publishes it. Verify Enercon has a relevant charger line.
- MCS connectors/cables: Staubli QCC, Huber+Suhner, Phoenix Contact, ITT Cannon
  | each site | datasheet | MCS connector current/voltage/cooling/cycle ratings.
- Heliox MCS, ABB A200/HVC360, Kempower Mega Satellite Flex | OEM sites |
  datasheet | Confirm voltage/current/standby/efficiency for the MCS products
  (we only have power so far).
- Pantograph: Schunk, SBRS, Hitachi, Furrer+Frey (OppCharge) | sites | bus
  opportunity-charging contact ratings and kW.

## Costs

- **CEF AFIF award lists** | cinea.ec.europa.eu / EU Funding portal | download
  award lists | Per-site HDV MCS pool budgets = real cost points (section 3.4).
- **Independent DK 2024-26 hardware quotes** | installers / Danish ladepuljer
  award lists (Energistyrelsen) | | To compare like-for-like with COWI bands (Q6).
- **Danish ladepuljer for trucks + award lists** | Energistyrelsen /
  Vejdirektoratet | | Subsidy amounts, rules, and per-project real costs.

## CPOs and prices (cite published pages; respect app terms)

- Clever published price page + Clever One subscription | clever.dk | capture |
  Confirm ~799 DKK/mo and ad-hoc DKK/kWh (Q8). Record capture date + terms.
- edri | edri.com/en-dk | confirm operator identity, DC 3.45 / AC 2.65 DKK/kWh,
  date, dynamic-pricing flag, terms.
- E.ON Drive, Circle K, OK, Uno-X, Ionity, Spirii, Monta, Allego, Aral pulse,
  Shell Recharge, EnBW | each operator site | capture published prices + HD-bay
  access. Confirm which are real DK operators; drop wrong leads.
- Milence DK hub site(s): location, kW, opening date | milence.com/our-charging
  -hubs | capture | We have the price, not the site detail.
- eMSP/fuel cards for trucks: DKV, UTA, Shell Card, Circle K, Travis Road
  Services | each site | charging roaming mark-up on top of CPO price.
- Roaming platforms: Hubject, Gireve, e-clearing.net | sites | fee structures if
  public (usually B2B).
- FDM newer public fast-charge average | fdm.dk | replace the dated 2024 3.25
  DKK/kWh figure.

## Open datasets (confirm fields, size, licence, commercial use)

- EAFO live statistics dashboard | alternative-fuels-observatory.ec.europa.eu |
  per-country public charger counts by power class (DK/DE/NL/SE). CC BY 4.0.
- Bundesnetzagentur Ladesäulenregister (DE) | bundesnetzagentur.de | download
  CSV | comparator for DK NAP completeness. DE public/open.
- NOBIL (NO/Nordic) | nobil.no | API key | Nordic charger DB; confirm DK
  coverage + commercial terms.
- Open Charge Map | openchargemap.org/site/develop/api | confirm exact licence
  (CC BY-SA?) + API terms (Q10, share-alike).
- ElaadNL datasets | platform.elaad.io | charging-session/load profiles;
  confirm licence + any HD/bus coverage.
- ACN-Data (Caltech) | ev.caltech.edu/dataset | confirm licence (likely
  research-only / non-commercial). LD cars only.
- NREL Fleet DNA | nrel.gov | confirm whether it includes depot **charging
  load** data (not just drive cycles). CC BY 4.0 per earlier pass.

## Electricity stack

- Energinet current system + transmission + balance tariffs | en.energinet.dk |
  download | replace the Elindsigt modelled examples with current values.
- Energi Data Service dataset licence | energidataservice.dk | confirm the exact
  open-data terms (commercial reuse) for Elspotprices + DatahubPricelist.
- skat.dk elafgift refund eligibility detail | info.skat.dk E.A.4.6.1.x | read |
  Confirm who can claim the EV-charging refund and its interaction with the
  2026-27 general cut.
- Danish finance act 2026 (elafgift cut) | retsinformation.dk | confirm the
  exact 2026-27 general elafgift rate and scope (replaces ground.news `[C]`).
