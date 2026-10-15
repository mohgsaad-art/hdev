# STATUS: NEW (Step 9, item 3 / M4.3, Bob to review). Fresh typed-input resolver.
# PIPELINE ROLE: route input path 2 (typed summary) -> waypoint list, the same shape the VDRI parser
#   produces (src/resolver/waypoint_parser.Waypoint), so the driver model consumes it unchanged.
# INPUT-LAYER DECISIONS (docs/context/input-layer-and-json.md, docs/design/payload-stop-rows-then-fill.md):
#   - the user gives a summary: total distance, number of stops, avg stop duration, cruise speed, grade.
#   - EVEN stop spacing is an HDEV ASSUMPTION and must be flagged (recorded in the returned assumptions).
#   - default cruise speed / dwell / flat grade are ARGUMENTS, not hard-coded. The caller pulls them from
#     defaults.py at the resolver boundary and passes them in; this function records which defaults it used.
#   - speed wins over end time (we lay out distance + speed; the end time is whatever the driving takes).
# PURITY: every parameter is an argument; no file I/O; no reading defaults.py from inside (the boundary
#   caller does that and passes the values + their source/label through, so the assumptions list stays honest).
# FAIL LOUDLY: negative/zero total distance, n_stops < 0, non-positive speed/dwell -> ValueError.

from src.resolver.waypoint_parser import Waypoint


def resolve_typed(
    total_distance_m,
    n_stops,
    avg_stop_duration_s,
    cruise_speed_kmh,
    grade_pct=0.0,
    even_spacing=True,
):
    # build an editable waypoint table from a typed route summary.
    #
    # layout (even_spacing=True, the HDEV assumption): the route is split into n_stops equal legs, so the
    # stops sit at total_distance * i / n_stops for i = 1..n_stops. a depot waypoint is placed at row 0
    # (distance 0). the stops carry avg_stop_duration_s of dwell; the depot and the driving waypoints carry
    # stop 0. example: 30000 m, 3 stops -> waypoints at 0 / 10000 / 20000 / 30000 (4 waypoints, 3 stops).
    #
    # returns {"waypoints": [...], "assumptions": [...], "defaults_used": {...}} so the caller can report
    # exactly which assumptions and default values went into the table (nothing silently hard-coded).

    # ---- validate (fail loudly) ----
    if total_distance_m is None or total_distance_m <= 0:
        raise ValueError("resolve_typed: total_distance_m must be > 0, got %r" % (total_distance_m,))
    if n_stops is None or n_stops < 0:
        raise ValueError("resolve_typed: n_stops must be >= 0, got %r" % (n_stops,))
    if int(n_stops) != n_stops:
        raise ValueError("resolve_typed: n_stops must be a whole number, got %r" % (n_stops,))
    n_stops = int(n_stops)
    if avg_stop_duration_s is None or avg_stop_duration_s < 0:
        raise ValueError("resolve_typed: avg_stop_duration_s must be >= 0, got %r" % (avg_stop_duration_s,))
    if cruise_speed_kmh is None or cruise_speed_kmh <= 0:
        raise ValueError("resolve_typed: cruise_speed_kmh must be > 0, got %r" % (cruise_speed_kmh,))
    if not even_spacing:
        # only even spacing is implemented; anything else needs a per-leg distance list the UI does not yet produce.
        raise NotImplementedError("resolve_typed: only even stop spacing is implemented (blocked: no per-leg distances)")

    # ---- build the waypoint table ----
    waypoints = []

    # row 0: depot start. never a payload change even if it carried a stop (payload design rule); stop 0 here.
    waypoints.append(Waypoint(distance=0.0, speed=cruise_speed_kmh, grade_pct=grade_pct, stop=0.0))

    # even stop spacing: one leg per stop, stops at total_distance * i / n_stops.
    if n_stops > 0:
        leg_m = total_distance_m / n_stops
        for i in range(1, n_stops + 1):
            # snap the final stop exactly to total_distance to avoid float drift
            dist = total_distance_m if i == n_stops else leg_m * i
            waypoints.append(Waypoint(
                distance=dist,
                speed=cruise_speed_kmh,
                grade_pct=grade_pct,
                stop=float(avg_stop_duration_s),
            ))
    else:
        # no stops: a single driving leg from depot to the end point.
        waypoints.append(Waypoint(
            distance=float(total_distance_m),
            speed=cruise_speed_kmh,
            grade_pct=grade_pct,
            stop=0.0,
        ))

    # ---- record what was assumed / which defaults were used (for the assumptions list) ----
    assumptions = []
    if n_stops > 0:
        assumptions.append(
            "HDEV ASSUMPTION: even stop spacing - %d stops placed every %.1f m along %.1f m "
            "(real spacing unknown from a typed summary)" % (n_stops, total_distance_m / n_stops, total_distance_m)
        )
    assumptions.append(
        "speed wins over end time: the route end time is whatever driving at %.1f km/h takes, not a user-set end time"
        % (cruise_speed_kmh,)
    )
    if grade_pct == 0.0:
        assumptions.append("HDEV ASSUMPTION: flat grade (0 %) - no gradient profile given")

    defaults_used = {
        "cruise_speed_kmh": cruise_speed_kmh,
        "avg_stop_duration_s": avg_stop_duration_s,
        "grade_pct": grade_pct,
    }

    return {"waypoints": waypoints, "assumptions": assumptions, "defaults_used": defaults_used}
