"""Small synthetic routes (1 s rows) for the Part D placement tests.  ALL numbers here are ILLUSTRATIVE.

build_route(legs, stops) mimics the notebook driver row layout (measured on MunicipalUtility, Part D):
  * standing rows: V == 0, M == 0, S == waypoint distance exactly  (driver sets s = trig[1])
  * the FIRST row after a stop is an accelerating row that also has V == 0 (speed at the start of the step), M == 1
  * moving rows: V = v (m/s), M = 2
"""
import numpy as np

# the VECTO generic refuse profile (reference/vecto/resources/MissionCycles/MunicipalUtility_PTO_generic.vptoel), kW -> W.
VPTOEL_T = list(range(24))
VPTOEL_KW = [8.42] * 5 + [33.69] * 4 + [25.92] * 15
VPTOEL_W = [x * 1000.0 for x in VPTOEL_KW]
VPTOEL_KWH = (5 * 8.42 + 4 * 33.69 + 14 * 25.92) / 3600.0       # 0.149927... = 0.14993 kWh  [CALC, left-hold, t=0..22]


def build_route(legs, stops, v=10.0):
    """legs: leg length [m] between waypoints (multiples of v), len = n_wp - 1.  stops: FINAL stop seconds per waypoint (len n_wp).
    returns dict(T, S, V, M, wp_s, stop_wp)"""
    n_wp = len(stops)
    assert len(legs) == n_wp - 1
    S, V, M = [], [], []
    wp_s = [0.0]
    s = 0.0
    for k in range(n_wp):
        for _ in range(int(stops[k])):
            S.append(s); V.append(0.0); M.append(0)
        if k == n_wp - 1:
            break
        n_move = int(round(legs[k] / v))
        s0 = s
        for j in range(n_move):
            first_after_stop = (j == 0 and stops[k] > 0)
            S.append(s); V.append(0.0 if first_after_stop else v); M.append(1 if first_after_stop else 2)
            s += (v / 2 if first_after_stop else v)
        s = s0 + legs[k]
        wp_s.append(s)
    T = np.arange(len(S), dtype=float)
    return dict(T=T, S=np.array(S), V=np.array(V), M=np.array(M), wp_s=np.array(wp_s), stop_wp=np.array(stops, dtype=float))
