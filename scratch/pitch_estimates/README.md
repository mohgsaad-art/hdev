# scratch/pitch_estimates — rerunnable pitch estimates

Short, transparent physics scripts behind `docs/pitch/estimates-2026-10.md`.
They import Bob's engines (`src/engine/crosswind_engine.py`, `force_engine.py`,
`payload_engine.py`) **as-is** and read VECTO `.vdri`/`.csv` data from
`reference/vecto/resources/`. The battery item (`07_charging.py`) uses the generic
Group-5 BEV battery tables (`GenericBattery_243kWh*`) whose values are transcribed,
with sources, into `vecto_data.py`.

Nothing here writes to `src/`.

## Setup (numpy only)

```bash
# any Python 3.10+ with numpy works; e.g. a venv:
python3 -m venv .venv && . .venv/bin/activate && pip install numpy
# or, as used when these were produced:
#   uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python numpy
```

## Run

```bash
cd scratch/pitch_estimates
python 00_selfcheck.py                 # trust check: crosswind vs VECTO doc + cycle totals
python 01_steady_realistic_grade.py    # M1 steady state; R realistic vs avg; G grade vs flat
python 02_weather.py                   # W bad-weather vs good day
python 03_sensitivity.py               # T sensitivity bars (refuse truck daily energy)
python 04_crosscheck_braking.py        # H day-energy cross-check; B braking recovered
python 05_pto.py                       # O refuse-body PTO energy + P_aux floor
python 06_payload.py                   # P1 (V2) and P2 (V1) payload cases
python 07_charging.py                  # C 50 kW charge, OCV+Ri battery (M4)
```

## Files

| File | What |
|---|---|
| `vecto_data.py` | all VECTO-sourced inputs (each with file:line / source), engine imports, `.vdri` reader, OCV lookup, air-density helper. |
| `cycle_engine.py` | M1 steady-state power and M2 cycle energy balance built on `force_engine` + `crosswind_engine`. No driver model. |
| `00_…`–`07_…` | one script per deliverable item (see table above). |

All inputs are (a) a VECTO file (cited), (b) Bob's prompt, or (c) a stated ASSUMPTION.
VECTO = stable branch v5.1.3, commit `d16ba783c`.
