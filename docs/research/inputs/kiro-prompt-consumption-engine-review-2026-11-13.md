# Kiro prompt: `consumption_engine` full review (13 Nov 2026)

> NOTE: this file is Kiro's copy of Bob's prompt of 13 Nov 2026, kept in condensed form
> (rules, scope, decisions, parts and deliverables; the long Appendix 1/2 code listings are
> NOT repeated here because they are in the notebook `HDEV_NEW_code_of_record_2026-11-13.ipynb`
> and are checked byte-for-byte in Gate 2). Bob: replace with the original text if you want
> the verbatim copy in the repo.

Owner: Bob. Repo `mohgsaad-art/hdev`. Branch `consumption-review-2026-11` from `main`. One uninterrupted pass, one PR.
Outputs only in `docs/research/consumption-review-2026-11/`, `tests/consumption/`, `docs/explainers/consumption-explained.md`, `reference/vecto/jobs/consumption-2026-11/`.

## Rules
1. Do not edit Bob's engine code (notebook, `src/`). Variants only in `reference_copy.py`; every proposal = before/after snippet + measured effect.
2. No invented numbers; every value needs a named source (VECTO file+line, Reg. 2017/2400, ISO/EN/SAE/UN/JRC/NREL/EPA, paper) or `NO SOURCE`. Illustrative test values labelled `ILLUSTRATIVE`.
3. No silent fallbacks: `BLOCKED: <what is missing>`.
4. Tag every statement: [VECTO] [REG] [STD] [SOURCE] [CALC] [TEST] [ASSUMPTION] [SIMPLIFICATION] [OPEN].
5. VECTO 5.1.6-RC; source `mohgsaad-art/VECTO` branch `IEPC-experiments` commit `b8d6126`.
6. VECTO cannot run in the sandbox; new runs = Bob's job (Part J).
7. Engine purity: pure maths, SI inside (kelvin), no I/O, no defaults in signatures; parser checks inputs; `defaults.py` holds defaults. Judge each change: engine / parser / defaults / fetch layer.
8. Matching VECTO is not validation; need independent sources. Swapping one assumption for another with no source is not worth it.
9. HDEV must not underestimate energy; target within 5 % kWh/km.
10. Inputs a fleet user can really give; otherwise best sourced default.
11. Vectorised (numpy over rows); loops over rows are bugs unless cheap.
12. Plain English, owner = "Bob". 13. Never decide open design choices for Bob; "Kiro's recommendation" label.

## Gates
1. `docs/research/drag-default-test-2026-11/run_steps.py` -> Chain S V1 reference Regional 0.9749, Urban 0.8502 (+-0.0005).
2. Notebook functions identical to Appendix 1/2; diff against `src/engine/consumption.py`.
3. Real driver -> force -> pto -> P_aux -> consumption chain on E2 Regional, Urban, MunicipalUtility; minimal adapter `consumption_engine_v_signature_only`.

## Parts
A line-by-line audit + Q1-Q12 (VECTO source). B unit/analytic tests. C row-level VECTO reproduction (VECTO efficiencies vs HDEV placeholders). D sensitivity. E deviation register. F physics beyond VECTO. G other tools. H independent validation. I proposed `consumption_engine_v_proposed`. J VECTO runs for Bob. K performance. L layers around the engine (Q-L1..Q-L6). M plain-English explainer.

## Deliverables
Report `docs/research/consumption-review-2026-11.md` (summary first), folder with loader/reference_copy/scripts/CSVs, `tests/consumption/`, optional `reference/vecto/jobs/consumption-2026-11/`, `docs/explainers/consumption-explained.md`, one PR.
