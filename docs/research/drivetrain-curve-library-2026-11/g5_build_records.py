"""Build cached VECTO-equivalent records for only group 5 configs, in batches of 30.

Uses the unchanged Part 3 settings: P3.set_bounds(), HN.AIRDRAG_MODE='range_mid', and the range-aware
harness. The cache is one compressed, git-ignored .npz per batch. Run one batch per command so each remains
well below the 10-minute limit.

Usage: python g5_build_records.py 0   # batch number 0..8
"""
import csv
import os
import sys
import time

import harness as HN
import part3_loo as P3

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH_SIZE = 30
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")


def ids():
    return [r["config_id"] for r in csv.DictReader(open(os.path.join(HN.V2_DIR, "truck_configs.csv"))) if r["VehicleGroup"] == "5"]


def main(i):
    P3.set_bounds()
    HN.AIRDRAG_MODE = "range_mid"
    all_ids = ids()
    start, end = i * BATCH_SIZE, min((i + 1) * BATCH_SIZE, len(all_ids))
    batch = all_ids[start:end]
    if not batch:
        raise SystemExit("no group 5 batch %d" % i)
    t0 = time.monotonic()
    recs, skipped = HN.load_or_build(batch, "g5_%02d" % i, processes=8)
    elapsed = time.monotonic() - t0
    f = os.path.join(HERE, "g5_build_batch_%02d.csv" % i)
    with open(f, "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=["batch", "configs_requested", "records", "skipped", "wall_s", "config_ids"])
        w.writeheader(); w.writerow(dict(batch=i, configs_requested=len(batch), records=len(recs), skipped=len(skipped),
                                         wall_s=round(elapsed, 2), config_ids=";".join(batch)))
    sf = os.path.join(HERE, "g5_build_batch_%02d_skipped.csv" % i)
    with open(sf, "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.writer(fh); w.writerow(["config_id", "mission", "payload_kg", "reason"]); w.writerows(skipped)
    print("batch %d: %d configs, %d records, %d skipped, %.1f s" % (i, len(batch), len(recs), len(skipped), elapsed))
    print("wrote", f); print("wrote", sf)
    if elapsed > 600:
        raise SystemExit("BLOCKED: batch exceeded 10 minutes")


if __name__ == "__main__":
    main(int(sys.argv[1]))
