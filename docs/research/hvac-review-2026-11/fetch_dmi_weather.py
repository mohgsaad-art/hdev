"""Download one year of hourly Danish weather from the DMI Open Data API (metObs), no API key needed
(checked 12 Nov 2026). Station 06188 Sjaelsmark (Copenhagen area, ~55.876N 12.412E): the Copenhagen-area
station that has BOTH temp_mean_past1h and radia_glob_past1h (06186 Landbohoejskolen and 06180 Kastrup have
no radiation parameter in the DMI station list). [SOURCE, full API response read]

Output: weather/dmi_06188_2025_hourly.csv  (time_utc, temp_mean_past1h_C, radia_glob_past1h_Wm2)
        weather/dmi_query.txt             (exact query URLs + download date)
Run:    python fetch_dmi_weather.py   (needs network; the CSV in the repo is what all other scripts use)
"""
import csv, json, os, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "weather")
STATION, YEAR = "06188", 2025
BASE = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

def fetch(param):
    data = {}
    urls = []
    for month in range(1, 13):
        a = datetime.datetime(YEAR, month, 1)
        b = datetime.datetime(YEAR + (month == 12), month % 12 + 1, 1)
        url = (f"{BASE}?stationId={STATION}&parameterId={param}"
               f"&datetime={a:%Y-%m-%dT%H:%M:%SZ}/{b:%Y-%m-%dT%H:%M:%SZ}&limit=3000")
        urls.append(url)
        d = json.load(urllib.request.urlopen(url, timeout=120))
        for f in d["features"]:
            p = f["properties"]
            data[p["observed"]] = p["value"]
    return data, urls

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    t, u1 = fetch("temp_mean_past1h")
    r, u2 = fetch("radia_glob_past1h")
    keys = sorted(set(t) | set(r))
    keys = [k for k in keys if k.startswith(str(YEAR))]
    with open(os.path.join(OUT, "dmi_06188_2025_hourly.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["time_utc", "temp_mean_past1h_C", "radia_glob_past1h_Wm2"])
        for k in keys:
            w.writerow([k, t.get(k, ""), r.get(k, "")])
    with open(os.path.join(OUT, "dmi_query.txt"), "w") as fh:
        fh.write(f"Downloaded {datetime.date.today()} from DMI Open Data (opendataapi.dmi.dk), station {STATION}\n")
        fh.write("Monthly queries (items endpoint, no API key):\n")
        for u in u1 + u2: fh.write(u + "\n")
    print("wrote", os.path.join(OUT, "dmi_06188_2025_hourly.csv"), len(keys), "rows")
