# STATUS: OLD EXPLORATION SCRIPT (daily mean wind, one station, plot). Pasted by Bob 12 Oct 2026.
# Superseded by dmi_weather_climatology.py for wind+temperature. Kept for the station search pattern.
# Note: comment says "7-day" but rolling window is 30; title says 2024 but range is 2022-2025.
import requests
import pandas as pd
import matplotlib.pyplot as plt
import math

BASE = "https://opendataapi.dmi.dk/v2/climateData/collections"
DENMARK_BBOX = "7,54,16,58"

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
    url = f"{BASE}/station/items"
    params = {"status": "Active", "bbox": DENMARK_BBOX, "limit": 300000}
    data = fetch_json(url, params)
    rows = []
    for f in data.get("features", []):
        props = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        rows.append({"station_id": props["stationId"], "station_name": props.get("name"), "lat": lat, "lon": lon})
    return pd.DataFrame(rows)

def get_daily_mean_wind_speed(station_id, start_iso, end_iso):
    url = f"{BASE}/stationValue/items"
    params = {
        "stationId": station_id,
        "parameterId": "mean_wind_speed",
        "timeResolution": "day",
        "datetime": f"{start_iso}/{end_iso}",
        "sortorder": "from,DESC",
        "limit": 300000,
    }
    data = fetch_json(url, params)
    rows = []
    for f in data.get("features", []):
        props = f["properties"]
        rows.append({"from": props["from"], "mean_wind_speed_10m_mps": props["value"]})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["from"] = pd.to_datetime(df["from"], utc=True)
        df["mean_wind_speed_10m_mps"] = pd.to_numeric(df["mean_wind_speed_10m_mps"], errors="coerce")
        df = df.dropna().sort_values("from").reset_index(drop=True)
    return df

input_lat, input_lon = 55.6800, 12.4500
start_iso, end_iso = "2022-01-01T00:00:00Z", "2025-01-01T00:00:00Z"

stations = get_climate_stations()
stations["dist_km"] = stations.apply(lambda r: haversine_km(input_lat, input_lon, r.lat, r.lon), axis=1)
stations = stations.sort_values("dist_km").reset_index(drop=True)

df = pd.DataFrame()
chosen_station = None
for _, station in stations.head(10).iterrows():
    try:
        temp = get_daily_mean_wind_speed(station["station_id"], start_iso, end_iso)
        if len(temp) > 300:
            df, chosen_station = temp, station
            break
    except:
        continue

if not df.empty:
    # Calculate weekly smoothed average (7-day rolling mean)
    df["weekly_smooth"] = df["mean_wind_speed_10m_mps"].rolling(window=30, center=True).mean()

    print(f"Using: {chosen_station['station_name']} ({chosen_station['station_id']})")
    plt.figure(figsize=(16, 5))
    plt.plot(df["from"], df["mean_wind_speed_10m_mps"], alpha=0.3, label="Daily Mean", color="steelblue")
    plt.plot(df["from"], df["weekly_smooth"], label="Weekly Smoothed (7d)", color="darkorange", linewidth=2)

    plt.title(f"Wind Speed 2024 - {chosen_station['station_name']} (10m Height)")
    plt.ylabel("Wind Speed [m/s]")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()
else:
    print("No data found for the nearest stations in 2024.")
