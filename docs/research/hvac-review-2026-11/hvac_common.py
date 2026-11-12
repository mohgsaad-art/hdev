"""Shared helpers for the HVAC review scripts (test tooling, not engine code).

* load_weather(): DMI 06188 2025 hourly CSV -> arrays on a full 8760-h UTC grid. Gaps are filled by linear interpolation
  in time; the number of filled hours is returned and printed (this plays the role of the PARSER's gap-fill, decision 5).
  Convention: DMI stamps *_past1h values at the END of the hour, so hour_start = stamp - 1 h.  [SOURCE: DMI API field
  'observed' + parameter name 'past1h'; the end-of-hour convention is [ASSUMPTION], checked on the diurnal solar peak.]
* ILLUSTRATIVE operating schedule: Mon-Fri, local hours 06:00-16:00 (10 h).  [ILLUSTRATIVE - not a Bob input]
* Parameter sets: PLACEHOLDER (Bob's 12 Nov placeholders) and VECTO_DRIVER_ANALOGUE (VECTO bus driver compartment).
"""
import os
import numpy as np
import pandas as pd
from _load_notebook import NS

HERE = os.path.dirname(os.path.abspath(__file__))
HVAC_thermal, ssm_total_w, climate_lookup = NS["HVAC_thermal"], NS["ssm_total_w"], NS["climate_lookup"]

# ---- VECTO-sourced curves (DefaultClimatic.aenv, copied in vecto_data/) -------------------------------------------
T_HEAT = [-20.0, -5.0, 2.0, 8.0, 14.0]     # heating rows 1,2,3,4(=5),6(=7)
T_COOL = [20.5, 26.0, 33.0]                # cooling rows 8(=9),10,11
COP_H = {"R-744": [1.80, 2.04, 2.50, 2.98, 3.38],
         "non R-744 continuous": [np.nan, 1.78, 2.22, 2.94, 3.50]}
COP_C = {"R-744": [3.80, 2.82, 2.14], "non R-744 continuous": [3.88, 3.36, 2.74]}
SHARES = {  # (hp, eh, fuel) per heating point; HeatingDistribution.csv HD2 = R-744 + electric heater; HD1 = R-744 only
    "HD1": ([1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0] * 5),
    "HD2": ([.5, 1, 1, 1, 1], [.5, 0, 0, 0, 0], [0] * 5),
    "HD9": ([0] * 5, [1] * 5, [0] * 5),
}
VECTO_WEIGHTS = {  # DefaultClimatic.aenv: (T, solar, weight raw) -- normalised by their sum (EnvironmentalContidionsMapReader.cs 88-91)
    1: (-20, 10, .0053), 2: (-5, 30, .0826), 3: (2, 30, .0826), 4: (8, 20, .1661), 5: (8, 155, .0826), 6: (14, 30, .0826),
    7: (14, 175, .1243), 8: (20.5, 30, .1243), 9: (20.5, 200, .1243), 10: (26, 150, .0826), 11: (33, 150, .0427)}


def base_args(geom, hp="R-744", hd="HD2", cap_h=5000.0, cap_c=5000.0, vent=7.0, vent_h=7.0):
    hps, ehs, fus = SHARES[hd]
    return dict(A_surface=geom["A"], U=geom["U"], N_persons=geom["N"], A_window=geom["Aw"],
                T_heat_points=T_HEAT, cop_heat_points=COP_H[hp], T_cool_points=T_COOL, cop_cool_points=COP_C[hp],
                hp_share_points=hps, eh_share_points=ehs, fuel_share_points=fus,
                max_heating_power=cap_h, max_cooling_power=cap_c, cab_volume=geom["V"], vent_rate=vent, vent_rate_heating=vent_h)


# Bob's 12 Nov placeholders (prompt 0.3 item 2 and Part C.2); N, vents, caps, COP/share choices = my choices (report "Choices I made")
PLACEHOLDER = dict(A=20.0, U=3.0, Aw=4.0, V=6.5, N=2)                  # all [ASSUMPTION] (Bob's placeholders)
# VECTO bus driver compartment analogue: DriverCompartmentLength 1.2 m (Constants.cs:207), width 2.55 m (DD 481-487),
# internal height 2.5 m (= 3.0 m body - 0.5 m, DD 531, high floor class II), A=2(LW+LH+WH) with body height 3.0 for the W*H term
# (adapter lines 358-359 pattern), window = 1.5 m * 1.2 m + 5 m2 (adapter 356-357, Constants 211,213), U=3 (DD 561), +1 driver (adapter 367)
_L, _W, _Hi, _Hb = 1.2, 2.55, 2.5, 3.0
VECTO_DRIVER_ANALOGUE = dict(A=2 * (_L * _W + _L * _Hi + _W * _Hb), U=3.0, Aw=1.5 * _L + 5.0, V=_L * _W * _Hi, N=1)   # BUS values


def load_weather(verbose=True):
    d = pd.read_csv(os.path.join(HERE, "weather", "dmi_06188_2025_hourly.csv"), parse_dates=["time_utc"])
    d["hour_start"] = d["time_utc"] - pd.Timedelta(hours=1)
    grid = pd.date_range("2024-12-31T23:00Z", "2025-12-31T22:00Z", freq="h")          # hour starts covering the stamps 00:00..23:00 of 2025
    d = d.set_index("hour_start").reindex(grid)
    n_missing_rows = int(d["time_utc"].isna().sum())
    T = d["temp_mean_past1h_C"].astype(float); S = d["radia_glob_past1h_Wm2"].astype(float)
    n_T, n_S = int(T.isna().sum()), int(S.isna().sum())
    T = T.interpolate(limit_direction="both"); S = S.interpolate(limit_direction="both")
    loc = grid.tz_convert("Europe/Copenhagen")
    op = (loc.dayofweek < 5) & (loc.hour >= 6) & (loc.hour < 16)                       # ILLUSTRATIVE schedule
    if verbose:
        print(f"weather: {len(grid)} h; missing rows {n_missing_rows}; temperature gaps filled {n_T} h; radiation gaps filled {n_S} h; "
              f"operating hours (ILLUSTRATIVE Mon-Fri 06-16 local) {int(op.sum())}")
    return dict(T=T.values, S=S.values, op=op, grid=grid, local=loc, gaps=dict(rows=n_missing_rows, T=n_T, S=n_S))


def annual_kwh(hvac_w, op):
    """kWh over the operating hours only (the cab is only conditioned while the truck works - ILLUSTRATIVE)."""
    return float(np.sum(np.asarray(hvac_w)[op]) / 1000.0)


def vecto_e2():
    """E2 reference-load missions: VECTO lorry AC electric W (.vmod P_aux_AC_el), distance, time, kWh/km (Chain S, V1 from Gate 1)."""
    out = {}
    vm = os.path.join(os.path.dirname(HERE), "vecto")
    for m in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
        f = os.path.join(vm, f"BEV_E2_{m}_ReferenceLoad_1Hz.vmod")
        df = pd.read_csv(f, skiprows=1, encoding="latin-1", usecols=["time [s]", "dist [m]", "P_aux_AC_el [kW]"])
        out[m] = dict(ac_w=float(df["P_aux_AC_el [kW]"].median() * 1000), dist_km=float(df["dist [m]"].iloc[-1] / 1000),
                      time_h=float(df["time [s]"].iloc[-1] / 3600))
    s3 = pd.read_csv(os.path.join(os.path.dirname(HERE), "drag-default-test-2026-11", "step3_kwh_per_km.csv"))
    for m in out:
        r = s3[(s3.cycle == m) & (s3.load == "reference") & (s3.chain == "S") & (s3.variant.str.startswith("V1"))]
        out[m]["kwh_km_chainS_V1"] = float(r.kwh_km.iloc[0]) if len(r) else float("nan")
    return out
