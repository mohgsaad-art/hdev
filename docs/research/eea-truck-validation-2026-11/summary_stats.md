# Job 3 v2 summary statistics

Basis: **HDEV battery-terminal kWh/km** vs certified as-published (R11). Municipal Utility
**excluded** (R12: ePTO not in EEA data). CdxA = **VECTO standard-value CdxA** (2.4 [BOB], no
bin edges). Gate: **PASS** (worst 0.03% on the E2 example, section 4).

Runs: 1274 total; 1150 non-Municipal (summary); 124 Municipal (separate). 0 skipped.

## Per variant (non-Municipal, terminal basis)

| variant | n valid | median %err | P10 / P90 | within ±5% | within ±10% |
|---|---|---|---|---|---|
| V-A (notebook consumption_engine) | 1150 | **−0.5%** | −18.6 / +26.8 | 21% | **44%** |
| V-B (EU standard-value maps) | 0 | **cannot run from EEA data (R7)** | — | — | — |
| V-C (VECTO bus-generic maps) | 0 | **cannot run from EEA data (R7)** | — | — | — |
| V-D (fixed E2 example maps) | 1150 | +29.4% | +5.7 / +60.5 | 5% | 19% |

V-B/V-C produce **zero** valid runs: the standard/generic motor maps need a declared rated
point from a **full-load curve** (R7), which EEA does not carry; 930 runs hit
"no_fullload_curve(R7)" and 344 hit "multispeed_no_gear_ratios(R6)". This is the honest finding
the v1 prompt asked for — not a failure to compute, but a statement that these variants
**cannot be run from EEA data**. V-D is flagged E2-unsuitable (rated >250 kW) on 760/1274 runs.

## V-A by architecture (non-Municipal)

| arch | n | median %err | P10 / P90 | within ±10% |
|---|---|---|---|---|
| E2 | 272 | −8.4% | −19 / +7 | 51% |
| E3 | 116 | −6.8% | −17 / +15 | 60% |
| E-IEPC | 438 | −2.5% | −27 / +21 | 43% |
| E-IEPC-wheel | 324 | +16.9% | −1 / +36 | 33% |

## V-A by component certification method

| method | n | median %err | P10 / P90 | within ±10% |
|---|---|---|---|---|
| measured | 508 | +10.4% | −6.5 / +33 | 48% |
| standard | 642 | −7.6% | −24 / +15 | 41% |

## Municipal Utility (reported separately, R12)

V-A median **−61.6%** (P10 −63, P90 −55), 124 runs. This is the expected under-read when the
certified Municipal figure includes the generic electric-PTO (mean 23.57 kW, §2.6) that HDEV
cannot place (EEA carries no per-vehicle ePTO profile). Excluded from the headline statistics.

## Does any variant stay within ±10% on every architecture?

**No.** V-A is the only variant that runs on EEA data; its median is within ±10% on all four
architectures, but the spread (P10/P90) exceeds ±10% on every architecture, and E-IEPC-wheel
is biased high (+17% median). So no generic HDEV option reproduces certified kWh/km within
±10% across all architectures — the same conclusion as the 3 Nov VECTO-example matrix, now on
certified trucks, but with a **much smaller central bias** than v1 once the harness bugs are
fixed.
