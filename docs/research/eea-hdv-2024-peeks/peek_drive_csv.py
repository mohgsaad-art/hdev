# Colab cell: peek at CSV files in Google Drive (also .zip files that contain CSVs)
# Paste one or more Drive sharing links below, set the options, run the cell.
# The link must be "Anyone with the link can view".
# Output is printed and also saved as peek_<file>.txt (download it from the left file panel).

LINKS = [
    "PASTE_DRIVE_LINK_HERE",
    # "PASTE_SECOND_LINK_HERE",
]

HEAD_ROWS = 5          # first rows to show
SPREAD_ROWS = 5        # extra rows picked from across the whole file (0 = skip)
FULL_SCAN = False      # True = read the whole file in chunks: exact row count, null % and value counts (slow on big files)
TOP_VALUES = 8         # with FULL_SCAN: most common values shown per column (0 = skip)
CHUNK = 200_000        # rows per chunk when scanning

import os
import csv
import zipfile
import random
import pandas as pd

# make sure gdown is available (it normally is in Colab)
try:
    import gdown
except ImportError:
    os.system("pip install -q gdown")
    import gdown

pd.set_option("display.max_rows", 1000)
pd.set_option("display.max_columns", 1000)
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 60)


def download(link, folder="drive_files"):
    # download one shared Drive file and return its local path
    os.makedirs(folder, exist_ok=True)
    path = gdown.download(link, output=folder + "/", fuzzy=True, quiet=False)
    return path


def csv_paths(path):
    # a plain CSV gives itself; a zip is unpacked and its CSV/TXT files are returned
    if not zipfile.is_zipfile(path):
        return [path]
    out_dir = path + "_unzipped"
    # Python zipfile cannot open Deflate64 zips (EEA uses them), so use the unzip tool
    os.system(f'unzip -o -q "{path}" -d "{out_dir}"')
    found = []
    for root, _, files in os.walk(out_dir):
        for name in files:
            full = os.path.join(root, name)
            print("  in zip:", full, round(os.path.getsize(full) / 1e6, 1), "MB")
            if name.lower().endswith((".csv", ".txt", ".tsv")):
                found.append(full)
    return found


def detect_separator(path):
    # look at the first line and pick the most likely separator
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        first_line = f.readline()
    try:
        return csv.Sniffer().sniff(first_line, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def count_lines(path):
    # fast line count (data rows = lines - 1; can be off if text fields contain line breaks)
    n = 0
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            n += block.count(b"\n")
    return n


def peek(path):
    lines = []

    def say(text=""):
        print(text)
        lines.append(str(text))

    sep = detect_separator(path)
    size_mb = os.path.getsize(path) / 1e6
    say("=" * 100)
    say(f"FILE: {path}")
    say(f"size: {size_mb:.1f} MB   separator: {sep!r}")

    # 1. header + first rows (everything read as text, so nothing gets reformatted)
    head = pd.read_csv(path, sep=sep, nrows=HEAD_ROWS, dtype=str, encoding="utf-8-sig",
                       encoding_errors="replace", keep_default_na=False)
    say(f"columns: {len(head.columns)}")
    say()
    say("--- column list ---")
    for i, col in enumerate(head.columns):
        say(f"{i:4d}  {col}")

    say()
    say(f"--- first {HEAD_ROWS} rows (one line per column) ---")
    say(head.T.to_string())

    # 2. rows count (approximate, quick)
    say()
    say(f"approx. data rows: {count_lines(path) - 1:,}")

    # 3. rows from across the file, and optional full scan
    if SPREAD_ROWS > 0 or FULL_SCAN:
        spread_parts = []
        null_counts = None
        value_counts = {}
        total_rows = 0
        reader = pd.read_csv(path, sep=sep, chunksize=CHUNK, dtype=str, encoding="utf-8-sig",
                             encoding_errors="replace", keep_default_na=False)
        for chunk in reader:
            total_rows += len(chunk)
            # keep one random row per chunk as a candidate for the spread sample
            spread_parts.append(chunk.sample(1, random_state=total_rows))
            if FULL_SCAN:
                empty = chunk.isin(["", "NULL", "null", "NaN", "nan", "None"])
                null_counts = empty.sum() if null_counts is None else null_counts + empty.sum()
                if TOP_VALUES > 0:
                    for col in chunk.columns:
                        vc = chunk[col].value_counts()
                        value_counts[col] = vc if col not in value_counts else value_counts[col].add(vc, fill_value=0)
            if not FULL_SCAN and len(spread_parts) >= 50:
                # without a full scan, stop after 50 chunks to save time
                break

        if SPREAD_ROWS > 0:
            spread = pd.concat(spread_parts)
            spread = spread.sample(min(SPREAD_ROWS, len(spread)), random_state=1)
            say()
            say(f"--- {len(spread)} rows picked from across the file ---")
            say(spread.T.to_string())

        if FULL_SCAN:
            say()
            say(f"exact data rows: {total_rows:,}")
            say()
            say("--- empty / NULL share per column (%) ---")
            say((null_counts / total_rows * 100).round(1).to_string())
            if TOP_VALUES > 0:
                say()
                say(f"--- top {TOP_VALUES} values per column (count) ---")
                for col in head.columns:
                    vc = value_counts[col].sort_values(ascending=False)
                    say(f"[{col}]  distinct: {len(vc):,}")
                    say(vc.head(TOP_VALUES).astype(int).to_string())
                    say()

    # 4. save everything printed above to a text file
    out_name = "peek_" + os.path.basename(path).rsplit(".", 1)[0] + ".txt"
    with open(out_name, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nsaved: {out_name}")


for link in LINKS:
    local = download(link)
    for p in csv_paths(local):
        peek(p)
