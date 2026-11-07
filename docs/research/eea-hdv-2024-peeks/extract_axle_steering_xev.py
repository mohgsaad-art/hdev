# Colab cell: pull the axle (tyre) and steering-pump rows for the vehicles in vehicles_xev.csv
# Output: axle_xev.csv and steering_xev.csv (small) in the folder xev_join_out.
#
# Fill PATHS with Drive paths ("/content/drive/MyDrive/...") or Drive sharing links.
# vehicles_xev.csv is also in the repo: docs/research/eea-hdv-2024-join/vehicles_xev.csv

PATHS = {
    "vehicles_xev":            "PASTE_PATH_OR_LINK",
    "axle":                    "PASTE_PATH_OR_LINK",   # hdv_2024_axle.csv (585 MB)
    "steeringpumptechnology":  "PASTE_PATH_OR_LINK",   # hdv_2024_steeringpumptechnology.csv (197 MB)
}

MOUNT_DRIVE = True
CHUNK = 500_000
OUT = "xev_join_out"

import os
import pandas as pd

if MOUNT_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")

try:
    import gdown
except ImportError:
    os.system("pip install -q gdown")
    import gdown

os.makedirs(OUT, exist_ok=True)
NULLS = ["", "NULL", "null", "N.A.", "N/A", "-"]


def local(path_or_link, name):
    # download a Drive link once; a plain path is used as it is
    if path_or_link.startswith("http"):
        os.makedirs("downloads", exist_ok=True)
        target = f"downloads/{name}.csv"
        if not os.path.exists(target):
            gdown.download(path_or_link, output=target, fuzzy=True, quiet=False)
        return target
    return path_or_link


# the vehicles we care about
ids = set(pd.read_csv(local(PATHS["vehicles_xev"], "vehicles_xev"), usecols=["Vehicle_id"], dtype=str).Vehicle_id)
print("vehicle ids:", len(ids))


def extract(name, out_name):
    parts = []
    total = 0
    for chunk in pd.read_csv(local(PATHS[name], name), dtype=str, encoding="utf-8-sig",
                             na_values=NULLS, keep_default_na=False, chunksize=CHUNK):
        total += len(chunk)
        parts.append(chunk[chunk.Vehicle_id.isin(ids)])
        print(f"  {name}: {total:,} rows read")
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(f"{OUT}/{out_name}", index=False)
    print(f"{out_name}: {len(df):,} rows, {df.Vehicle_id.nunique():,} vehicles")
    return df


axle = extract("axle", "axle_xev.csv")
steer = extract("steeringpumptechnology", "steering_xev.csv")

# quick look: how many vehicles have RRC on every axle, and the value spread
axle["rrc"] = pd.to_numeric(axle.SpecificRRC, errors="coerce")
print("axle rows with RRC:", axle.rrc.notna().sum(), "of", len(axle))
print(axle.rrc.describe())
print(steer.SteeringpumpTechnology.value_counts().head(15))
