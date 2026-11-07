# Contracts, SLAs and charging-business models (pass 1)

Written for Bob. Plain English. Short sentences.

## The big gap, stated plainly

The brief's single highest-value instruction (section 1, 4.1) was to mine the
**Danish tender, concession and service-level documents** for real SLA clauses:
required kW, OCPP version, uptime %, response/fix times, penalties, price
structure, contract term, who owns the hardware, who pays the grid connection.

**Those documents are not in the repo.** The brief says Bob copies them in from
the claude.ai project (folders `claude/knowledge-base/charging-infrastructure/`
and `data-reports-misc/`). None of them are present on this branch or any
sibling branch. I checked:

- No `docs/research/inputs/` folder.
- No `manual-fetch-list-2026-11-06.md`, no `session-closeout-...`.
- None of: `ladestandere-kravspecifikation-paradigme.md`,
  `ladestandere-koncessionskontrakt-udkast.md`,
  `ladestandere-operatoerens-serviceniveau.md`,
  `region-hovedstaden-charging-tender-spec.md`, `roskilde-charging-contract.md`,
  `lyngby-taarbaek-charging-contract-draft.md`,
  `hilleroed-kommune-charger-tender-locations.md`, the municipal strategies, or
  the fleet-electrification guides.

So I **cannot extract clause-level SLA/price/term values with section numbers**
from them in this pass. That is the core of sections 4.1 and 3.5, and it is
blocked until the files are added. This is the same situation the vehicle-side
pass-3 hit with its named input files. Every such item below is tagged `[BOB]`.

What I *can* do: lay out the contract-model structure EV Scope needs, mark which
clauses each document type typically carries, and point to what to fetch. When
the files land, this file fills in fast.

## Contract models to capture (structure only this pass)

For each model, EV Scope needs: term, who owns the hardware, who pays the grid
connection (tilslutningsbidrag), price basis and indexation, uptime penalty,
and end-of-term treatment. `[INFERENCE]` these are the fields; the values come
from the documents.

1. **Charging-as-a-Service (CaaS) / Charge-Point-as-a-Service (CPaaS).**
   Operator owns and runs the hardware; customer pays a fixed DKK/kWh or a
   monthly fee. Who pays the grid connection varies by contract. `[BOB]` values.
2. **Hardware lease / financing.** Customer gets the asset over a term; service
   is a separate line. `[BOB]`.
3. **Concession contract (municipal).** Municipality grants a CPO the right to
   operate on public land, often with an uptime SLA, price caps, and a revenue
   share or concession fee. The Danish `ladestandere-koncessionskontrakt-udkast`
   is exactly this. `[BOB]` — not in repo.
4. **Revenue share.** Site host and CPO split charging revenue. `[BOB]`.
5. **Fixed DKK/kWh offtake / Energy-as-a-Service.** Depot buys delivered energy
   at an agreed DKK/kWh; the provider carries hardware + grid + O&M risk.
   Milence's fleet "volume-based tariff models" sit near here (`[C]`, electrive
   2026-06-10; exact terms not public).

## SLA fields the Danish service-level paradigm typically sets

`[INFERENCE]` from how Danish public procurement charging documents are built.
The actual values are in `ladestandere-operatoerens-serviceniveau.md` and the
tender specs, which are not in the repo.

- Uptime / availability (% per charge point per period).
- Response time (time to acknowledge a fault).
- Fix time / restore time (time to restore service).
- Reporting cadence and data delivery (now also an AFIR obligation — static +
  dynamic data to the National Access Point).
- Penalties / bod for missed uptime.
- Required kW per point and connector types.
- Required OCPP version and payment means (AFIR ad-hoc rules apply).

All `[BOB]` until the documents are added.

## What AFIR itself fixes (this we can source)

AFIR, Reg. (EU) 2023/1804, puts hard obligations on operators that effectively
become contract clauses. See `standards_regulation.md` for article references.
Most relevant to contracts/SLA:

- **Ad-hoc charging and price transparency.** Users must be able to charge
  without a subscription, and the ad-hoc price must be shown clearly. `[V]`
  EUR-Lex consolidated text.
- **Static and dynamic data to the National Access Point.** CPOs must publish
  location, power, connector, availability and price data. Monta confirms it
  reports this to NAPs on operators' behalf (`[C]`, monta.com). This is a real,
  current operator obligation in any DK contract.

## Flexibility / aggregator contracts (depot as a grid asset)

If an EV depot sells flexibility, it enters an Energinet ancillary-services
contract. The technical prerequisites (and therefore the charger/OCPP
requirements) are set by Energinet prequalification, not by the CPO. `[BOB]`:
fetch the Energinet prequalification documents for FCR, aFRR and mFRR to get
exact response-time requirements (e.g. FCR full activation within ~30 s). Listed
in `catalogue.csv` as `energinet_prequal`. See also `standards_regulation.md`.

## Action for Bob

Add the `claude/knowledge-base/charging-infrastructure/` and
`data-reports-misc/` files to the branch (or to `docs/research/inputs/`). Then
this file can be filled with clause-level values and section numbers — the
highest-value content in the whole brief.
