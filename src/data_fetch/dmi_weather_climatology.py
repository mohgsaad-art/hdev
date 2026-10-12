# STATUS: DRAFT. DMI fetch (daily mean wind + temperature, nearest station). Pasted by Bob 12 Oct 2026.
# KNOWN ISSUE vs decisions (6 Oct close-out section 4): this averages each calendar day ACROSS YEARS, which was decided
# against ("Do not average by calendar day across years - removes extremes; crosswind is non-linear").
# Decided split: fetch_dmi(...) (download once, save raw) + build_weather(...) (pure). Also check wind measurement height vs h_ref.

import requests
import pandas as pd
import math

BASE = "https://opendataapi.dmi.dk/v2/climateData/collections"
DENMARK_BBOX = "7,54,16,58"  # min_lon, min_lat, max_lon, max_lat

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def fetch_json(url, params):
    r = requests.get(url, params=params, timeout=90)
    if not r.ok:
        print(f"FAILED URL: {r.url}\nSTATUS: {r.status_code}")
    r.raise_for_status()
    return r.json()

def get_climate_stations():
    data = fetch_json(f"{BASE}/station/items",
                      {"status": "Active", "bbox": DENMARK_BBOX, "limit": 300000})
    rows = []
    for f in data.get("features", []):
        props = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        rows.append({"station_id": props["stationId"],
                     "station_name": props.get("name"),
                     "lat": lat, "lon": lon})
    return pd.DataFrame(rows)

def get_daily_param(station_id, parameter_id, start_iso, end_iso):
    """Daily values of one parameter for one station, indexed by local date."""
    data = fetch_json(f"{BASE}/stationValue/items", {
        "stationId": station_id,
        "parameterId": parameter_id,
        "timeResolution": "day",
        "datetime": f"{start_iso}/{end_iso}",
        "limit": 300000,
    })
    rows = [{"date": f["properties"]["from"], "value": f["properties"]["value"]}
            for f in data.get("features", [])]
    if not rows:
        return pd.Series(dtype=float)

    df = pd.DataFrame(rows)
    df["date"] = (pd.to_datetime(df["date"], utc=True)
                    .dt.tz_convert("Europe/Copenhagen")
                    .dt.tz_localize(None).dt.normalize())
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna().drop_duplicates("date").set_index("date")["value"]


def get_wind_temp_climatology(lat, lon,
                              start_iso="2023-10-01T00:00:00Z",
                              end_iso="2024-10-01T00:00:00Z",
                              min_days=364,
                              keep_leap_day=False):
    """
    Finds the nearest station that has BOTH wind and temperature data, then
    averages each calendar day (Jan 1, Jan 2, ...) across all years.

    Returns a DataFrame with 365 rows (366 if keep_leap_day=True):
        month_day | avg_wind_speed_mps | avg_temp_c
    """
    stations = get_climate_stations()
    stations["dist_km"] = stations.apply(
        lambda r: haversine_km(lat, lon, r.lat, r.lon), axis=1)
    stations = stations.sort_values("dist_km").reset_index(drop=True)

    for _, st in stations.iterrows():
        try:
            wind = get_daily_param(st["station_id"], "mean_wind_speed", start_iso, end_iso)
            temp = get_daily_param(st["station_id"], "mean_temp", start_iso, end_iso)
        except Exception as e:
            print(f"Failed: {st['station_name']} ({st['station_id']}) - {e}")
            continue

        if len(wind) < min_days or len(temp) < min_days:
            print(f"Skipped: {st['station_name']} - wind rows {len(wind)}, temp rows {len(temp)}")
            continue

        print(f"Using: {st['station_name']} ({st['station_id']}), {st['dist_km']:.2f} km away")

        df = pd.concat([wind.rename("wind"), temp.rename("temp")], axis=1)
        df["month_day"] = df.index.strftime("%m-%d")
        if not keep_leap_day:
            df = df[df["month_day"] != "02-29"]

        out = (df.groupby("month_day")
                 .agg(avg_wind_speed_mps=("wind", "mean"),
                      avg_temp_c=("temp", "mean"))
                 .reset_index())
        return out

    raise RuntimeError("No station with sufficient wind + temperature data found.")


# Usage
clim = get_wind_temp_climatology(55.6800, 12.4500)
print(clim.head())
print(len(clim))  # 365

# If you want plain numpy arrays:
month_day = clim["month_day"].to_numpy()
wind = clim["avg_wind_speed_mps"].to_numpy()
temp = clim["avg_temp_c"].to_numpy()