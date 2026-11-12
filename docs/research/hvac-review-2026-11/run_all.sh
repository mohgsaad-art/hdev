#!/usr/bin/env bash
# Runs every script of the HVAC review.  Usage: bash run_all.sh   (needs numpy, pandas, matplotlib, pytest)
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python}
$PY _load_notebook.py
$PY gate2_code_of_record.py
$PY gate3_vecto_unit_tests.py
$PY gate3_grid.py
$PY run_part_b_jumps.py
$PY run_part_c.py
$PY run_part_d_e.py
$PY run_part_k.py
$PY run_part_f_variants.py
$PYTHON run_part_i.py
