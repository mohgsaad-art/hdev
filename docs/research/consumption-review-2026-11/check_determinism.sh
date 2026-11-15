#!/usr/bin/env bash
# Runs the deterministic scripts twice and compares the CSV files byte for byte.
cd "$(dirname "$0")"
PY=${PY:-python}
bash run_all.sh --skip-timing > /dev/null 2>&1
mkdir -p /tmp/det1 && rm -f /tmp/det1/* && cp part[ACDF]_*.csv gate3_chain.csv /tmp/det1/
bash run_all.sh --skip-timing > /dev/null 2>&1
fail=0
for f in part[ACDF]_*.csv gate3_chain.csv; do cmp -s "$f" "/tmp/det1/$f" || { echo "DIFFERENT: $f"; fail=1; }; done
[ $fail = 0 ] && echo "all deterministic CSVs identical between two runs"
