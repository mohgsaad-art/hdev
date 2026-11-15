#!/usr/bin/env bash
# Runs every script of the consumption review (deterministic ones twice is done by check_determinism.sh).  Usage: bash run_all.sh [--skip-timing]
set -e
cd "$(dirname "$0")"
export MPLCONFIGDIR=${MPLCONFIGDIR:-/tmp/mpl}
export VECTO_SRC=${VECTO_SRC:-/projects/sandbox/vecto-src}
PY=${PY:-python}
$PY gate2_code_of_record.py
$PY gate3_chain.py
$PY partA_tables.py
$PY partC_vecto_rows.py
$PY partD_sensitivity.py
$PY partF_numbers.py
if [ "$1" != "--skip-timing" ]; then $PY partK_performance.py --skip-old-long; fi
