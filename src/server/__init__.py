# STATUS: NEW (Step 9, items 15/17/18, Bob to review). The server-side orchestration package.
#
# This package holds the NON-engine, orchestration-and-contract layer that sits between the pure engines
# (src/engine, src/charging, src/resolver) and the transport (hdev/*_api.py):
#   - runner.py : runner.run(base, changes) - stage selection, change-set application, refusal, assembly
#   - tco.py    : TCO data model + category sums (headline metrics locked by M6.24)
#   - co2.py    : CO2 interface + stub (sources locked by M6.25)
#
# NOTHING here imports numpy or gym at package-import time: the demo path (hdev.run_api demo branch ->
# demo.demo_engine) must stay numpy-free, so runner.run defers every engine import to call time.
