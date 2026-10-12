# STATUS: ALTERNATIVE / OLDER VERSION - do not treat as canonical.
# Memory note (14 April): the DriverModel class is canonical; the older vecto_driver.py port is deprecated.
# This file is a later variant of that port that Bob pasted on 12 Oct 2026. It contains fixes worth comparing during the
# driver-model audit (deceleration-distance guard, standstill start, snap-to-stop near zero speed) and interpolates grade
# between waypoints (VECTO interpolates ALTITUDE, not grade - see engine notes). Bob to confirm what this file is.

"""
Driver Model

Input pasted directly as strings:
  - VDRI_DATA
  - VACC_DATA
"""

import csv
import math
from dataclasses import dataclass
from io import StringIO
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CycleEntry:
    distance_m: float
    speed_kmh: float
    grade_pct: float
    stop_s: float


@dataclass
class AccPoint:
    speed_kmh: float
    acc_ms2: float
    dec_ms2: float


@dataclass
class TraceRow:
    time_s: float
    distance_m: float
    speed_ms: float
    accel_ms2: float
    grade_deg: float


# ---------------------------------------------------------------------------
# Parsers for pasted string data
# ---------------------------------------------------------------------------

def parse_vdri_text(text: str) -> List[CycleEntry]:
    entries = []
    text = text.replace("\ufeff", "")
    reader = csv.reader(StringIO(text.strip()))

    for row in reader:
        row = [c.strip() for c in row]

        if not row or row[0].startswith("<") or row[0].startswith("#"):
            continue

        try:
            s = float(row[0])
            v = float(row[1])
            grad = float(row[2])
            stop = float(row[3])
            entries.append(CycleEntry(s, v, grad, stop))
        except (ValueError, IndexError):
            continue

    if not entries:
        raise ValueError("No valid VDRI entries found in pasted text")

    return entries


def parse_vacc_text(text: str) -> List[AccPoint]:
    points = []
    text = text.replace("\ufeff", "")
    reader = csv.reader(StringIO(text.strip()))

    for row in reader:
        row = [c.strip() for c in row]

        if not row:
            continue

        try:
            v = float(row[0])
            a = float(row[1])
            d = float(row[2])
            points.append(AccPoint(v, a, d))
        except (ValueError, IndexError):
            continue

    if not points:
        raise ValueError("No valid VACC entries found in pasted text")

    return sorted(points, key=lambda p: p.speed_kmh)


# ---------------------------------------------------------------------------
# Acceleration curve
# ---------------------------------------------------------------------------

class AccelerationCurve:
    def __init__(self, points: List[AccPoint]):
        self.points = sorted(points, key=lambda p: p.speed_kmh)

    def lookup(self, speed_ms: float) -> Tuple[float, float]:
        speed_kmh = speed_ms * 3.6
        pts = self.points

        if speed_kmh <= pts[0].speed_kmh:
            return pts[0].acc_ms2, pts[0].dec_ms2

        if speed_kmh >= pts[-1].speed_kmh:
            return pts[-1].acc_ms2, pts[-1].dec_ms2

        for i in range(len(pts) - 1):
            lo = pts[i]
            hi = pts[i + 1]

            if lo.speed_kmh <= speed_kmh <= hi.speed_kmh:
                t = (speed_kmh - lo.speed_kmh) / (hi.speed_kmh - lo.speed_kmh)
                acc = lo.acc_ms2 + t * (hi.acc_ms2 - lo.acc_ms2)
                dec = lo.dec_ms2 + t * (hi.dec_ms2 - lo.dec_ms2)
                return acc, dec

        return pts[-1].acc_ms2, pts[-1].dec_ms2

    def compute_deceleration_distance(self, v0_ms: float, v1_ms: float) -> float:
        if v1_ms >= v0_ms:
            return 0.0

        breakpoints = [v1_ms]

        for pt in self.points:
            v_ms = pt.speed_kmh / 3.6
            if v1_ms < v_ms < v0_ms:
                breakpoints.append(v_ms)

        breakpoints.append(v0_ms)
        breakpoints.sort()

        total_distance = 0.0

        for i in range(len(breakpoints) - 1, 0, -1):
            v_hi = breakpoints[i]
            v_lo = breakpoints[i - 1]
            v_mid = (v_hi + v_lo) / 2.0

            _, dec = self.lookup(v_mid)

            if dec >= 0:
                dec = -0.01

            ds = (v_hi ** 2 - v_lo ** 2) / (2.0 * abs(dec))
            total_distance += ds

        return total_distance


# ---------------------------------------------------------------------------
# Acceleration kernel
# ---------------------------------------------------------------------------

def compute_acceleration(
    v0_ms: float,
    v1_ms: float,
    ds_m: float,
    acc_curve: AccelerationCurve,
) -> float:

    if ds_m <= 0 or (v0_ms + v1_ms) <= 0:
        return 0.0

    dt = 2.0 * ds_m / (v0_ms + v1_ms)

    if dt <= 0:
        return 0.0

    a_required = (v1_ms - v0_ms) / dt

    max_acc, max_dec = acc_curve.lookup(v0_ms)
    a_clamped = max(max_dec, min(max_acc, a_required))

    return a_clamped


# ---------------------------------------------------------------------------
# Grade helpers
# ---------------------------------------------------------------------------

def grade_pct_to_deg(grade_pct: float) -> float:
    return math.degrees(math.atan(grade_pct / 100.0))


def interpolate_grade(entry_lo: CycleEntry, entry_hi: CycleEntry, pos_m: float) -> float:
    if entry_hi.distance_m == entry_lo.distance_m:
        return grade_pct_to_deg(entry_lo.grade_pct)

    t = (pos_m - entry_lo.distance_m) / (entry_hi.distance_m - entry_lo.distance_m)
    grade_pct = entry_lo.grade_pct + t * (entry_hi.grade_pct - entry_lo.grade_pct)

    return grade_pct_to_deg(grade_pct)


# ---------------------------------------------------------------------------
# Main driver simulation
# ---------------------------------------------------------------------------

def simulate_driver(
    cycle: List[CycleEntry],
    acc_curve: AccelerationCurve,
    dt_s: float = 1.0,
) -> List[TraceRow]:

    trace: List[TraceRow] = []

    time_s = 0.0
    pos_m = cycle[0].distance_m
    speed_ms = cycle[0].speed_kmh / 3.6

    # Initial stop
    if cycle[0].stop_s > 0:
        t_elapsed = 0.0

        while t_elapsed < cycle[0].stop_s:
            grade_deg = grade_pct_to_deg(cycle[0].grade_pct)
            trace.append(TraceRow(time_s, pos_m, 0.0, 0.0, grade_deg))

            time_s += dt_s
            t_elapsed += dt_s

        speed_ms = 0.0

    for i in range(len(cycle) - 1):
        left = cycle[i]
        right = cycle[i + 1]

        left_ms = left.speed_kmh / 3.6
        target_ms = right.speed_kmh / 3.6
        seg_end_m = right.distance_m

        while pos_m < seg_end_m:
            remaining_m = seg_end_m - pos_m

            max_acc, max_dec = acc_curve.lookup(speed_ms)

            brake_dist_m = acc_curve.compute_deceleration_distance(speed_ms, target_ms)
            brake_start_m = seg_end_m - brake_dist_m

            # ---------------------------------------------------------------
            # Choose acceleration
            # ---------------------------------------------------------------

            if target_ms < speed_ms and pos_m >= brake_start_m:
                # Braking phase: decelerate to the target speed at the waypoint
                a = compute_acceleration(speed_ms, target_ms, remaining_m, acc_curve)

            else:
                # Cruise / accelerate phase
                #
                # Important:
                # Do NOT drive toward target_ms when target_ms is lower.
                # For example, before a stop, keep driving at the current/left
                # speed until the braking point.
                cruise_ms = max(left_ms, target_ms)

                a = compute_acceleration(speed_ms, cruise_ms, remaining_m, acc_curve)
                a = max(max_dec, min(max_acc, a))

                # Safety for start from standstill
                if speed_ms <= 1e-9 and cruise_ms > 0 and a <= 0:
                    a = max_acc

            grade_deg = interpolate_grade(left, right, pos_m)

            trace.append(TraceRow(time_s, pos_m, speed_ms, a, grade_deg))

            # ---------------------------------------------------------------
            # Kinematic update
            # ---------------------------------------------------------------

            new_speed = speed_ms + a * dt_s
            new_speed = max(0.0, new_speed)

            ds = speed_ms * dt_s + 0.5 * a * dt_s * dt_s
            ds = max(0.0, ds)

            # If this timestep reaches or passes the waypoint, snap exactly there
            if pos_m + ds >= seg_end_m:
                pos_m = seg_end_m
                speed_ms = target_ms
                time_s += dt_s
                break

            # Prevent numerical lo0k-up
            if ds <= 1e-9 and new_speed <= 1e-9:
                if target_ms == 0.0:
                    # This can happen very close to a stop waypoint due to timestep rounding.
                    # Snap to the stop point.
                    pos_m = seg_end_m
                    speed_ms = 0.0
                    time_s += dt_s
                    break

                else:
                    # Start moving toward a positive target speed
                    a = max_acc
                    new_speed = max_acc * dt_s
                    ds = 0.5 * max_acc * dt_s * dt_s

            pos_m += ds
            speed_ms = new_speed
            time_s += dt_s

        # Snap exactly to waypoint
        pos_m = seg_end_m
        speed_ms = target_ms

        # ---------------------------------------------------------------
        # Stop phase
        # ---------------------------------------------------------------

        if right.stop_s > 0:
            speed_ms = 0.0
            t_elapsed = 0.0

            while t_elapsed < right.stop_s:
                grade_deg = grade_pct_to_deg(right.grade_pct)
                trace.append(TraceRow(time_s, pos_m, 0.0, 0.0, grade_deg))

                time_s += dt_s
                t_elapsed += dt_s

    return trace




# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    VDRI_DATA = """
<s>,<v>,<grad>,<stop>
0,0,0.6,45.4
1,34.4,0.6,0
2,34.4,0.6,0
4,34.4,0.7,0
23,34.4,0.8,0
101,29.9,0.8,0
154,22,0.8,0
155,33.6,0.8,0
162,33.6,0.9,0



"""

    VACC_DATA = """
v [km/h],acc [m/s²],dec [m/s²]
0,1,-1
25,1,-1
50,0.642857143,-1
60,0.5,-0.5
120,0.5,-0.5
"""

    cycle = parse_vdri_text(VDRI_DATA)
    acc_pts = parse_vacc_text(VACC_DATA)
    acc_curve = AccelerationCurve(acc_pts)

    trace = simulate_driver(cycle, acc_curve, dt_s=1.0)



    for row in trace[::10]:
        print(
            f"{row.time_s:8.1f} "
            f"{row.distance_m:10.1f} "
            f"{row.speed_ms * 3.6:10.2f} "
            f"{row.accel_ms2:8.3f} "
            f"{row.grade_deg:10.4f}"
        )

    print(f"\nTotal timesteps : {len(trace)}")
    print(f"Total distance  : {trace[-1].distance_m:.1f} m")
    print(f"Total time      : {trace[-1].time_s:.1f} s")

    # Plot speed vs time
    import matplotlib.pyplot as plt

    time_values = [row.time_s for row in trace]
    speed_values = [row.speed_ms * 3.6 for row in trace]

    plt.plot(time_values, speed_values)
    plt.xlabel("Time [s]")
    plt.ylabel("Speed [km/h]")
    plt.title("Speed vs Time")
    plt.grid(True)
    plt.show()
