# Input registry (PR 1)

Owner: Bob. Status: NEW, for review.

This package is the single source of truth for every input the tool knows about. The UI draws its
sections and fields only from here (user §3.1 / §3.2 / §5.4). It is pure structure: no server, no I/O,
pure-Python stdlib only.

## What is here

- `slot.py` — the `Slot` class.
- `fields.py` — the `Field` structure and the section / type / visibility enums.
- `registry.py` — the full registry: 8 sections, 112 fields, §5.4 subgroup names and counts, plus
  section metadata and lookup helpers.
- `levers.py` — `LEVERS`, verbatim from user §3.2.

## Open 🔒 items touched

- **M6.7 — slot shape.** The slot shape `{value, unit, source, date, label, provided_by, locked,
  version}` is still 🔒 (undecided, may change). It is deliberately wrapped in the single `Slot` class
  so a future change lands in one place. It is **not** treated as final here.
- **M6.14 — lock enforcement.** The `locked` flag is defined on the slot; the validator (in
  `src/validate`) rejects a write to a locked slot. This is the lock-flag check only — there is no role
  system (out of scope and partly 🔒).

## Values without a source

There are **no physics default values** in this package. Rule 3 (no invented numbers) and the fact that
`defaults.py` is a separate later task (M1.1) mean every field here carries structure only; every `Slot`
starts empty (`value=None`, `source="missing"`). This absence is expected for PR 1, not a flag.

## Method hiding (§8)

Every client-facing `label` uses plain words only. No parameter, coefficient, formula, physics
data-source, or technical charging-strategy name appears in any label. `collapsed` and `hidden` fields
are counted in totals but never listed by name in the UI. The charging-priority field exposes only the
three client-facing names (`lowest_cost` / `grid_friendly` / `ready_earliest`).

## Visibility choices for Bob to review

- Per §3.1, every Vehicles, Weather, Charging and Depot & grid field is `collapsed`.
- Only Operation and Energy prices fields are `open`.
- Costs & finance and Policy & taxes default to `collapsed`. Bob to confirm whether any of those should
  be `open` price-facing fields.

## Registry vs mock-up counts

The §5.4 subgroup counts total exactly 112 and the registry matches them exactly, so there is no
registry-vs-mock-up discrepancy. If one ever appears, the registry wins and the UI follows (§5.4).
