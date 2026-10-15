# STATUS: NEW (Step 9, item 12, Bob to review). INTERFACE + STUB ONLY - the map provider is not chosen.
#
# PIPELINE ROLE: route input path 4 (AI / free-text + coordinates) -> waypoint list, the same
#   src.resolver.waypoint_parser.Waypoint shape the other three input paths produce (so the driver model
#   consumes it unchanged). The adapter would turn a list of stop points - each a coordinate and/or a
#   free-text description ("depot", "Netto Vesterbro", "the big Shell on the ring road") - into an
#   ordered waypoint list, using a MAP-API ROAD DISTANCE between consecutive points (not straight-line),
#   plus any geocoding needed to resolve a description to a coordinate.
#
# WHY A STUB (not a working function): the map provider is NOT selected. Choosing one (Google Maps,
#   Mapbox, OSRM/OpenStreetMap, HERE, ...) is a product + cost + data-privacy decision Bob has not made.
#   Picking one here would be inventing a dependency and a data source. Per the engine rules we provide
#   the INTERFACE and a stub that raises NotImplementedError, and FLAG it; where this surfaces to the UI
#   the field stays null so the UI shows "Not yet available".
#
# PURITY (engine rule 7): the eventual implementation keeps the engine pure by taking the road-distance
#   lookup as an INJECTED function (road_distance_fn), so the engine itself never does network I/O - the
#   caller owns the map-API call. The interface is designed that way now so the stub documents the pure
#   contract.

from src.resolver.waypoint_parser import Waypoint  # noqa: F401  (documents the intended output type)


def ai_waypoints_from_descriptions(
    points,
    road_distance_fn=None,
    geocode_fn=None,
    default_speed_kmh=None,
    default_grade_pct=0.0,
    default_stop_s=0.0,
):
    # INTENDED INTERFACE (not implemented - map provider not chosen):
    #
    #   points            : ordered list of stop descriptors. Each is a dict with at least one of
    #                         {'coord': (lat, lon)} or {'description': str}, optionally {'stop_s': float}.
    #                         Order is the visiting order of the route.
    #   road_distance_fn  : INJECTED callable (coord_a, coord_b) -> road distance in metres. This is the
    #                         map-API road-distance lookup; injecting it keeps this engine pure (no
    #                         network I/O inside). Required once implemented.
    #   geocode_fn        : INJECTED callable description -> (lat, lon) to resolve free-text stops to
    #                         coordinates. Required when any point has no 'coord'.
    #   default_speed_kmh : cruise speed to stamp on the generated waypoints (from defaults.py at the
    #                         boundary, passed in - never hard-coded here).
    #   default_grade_pct : flat-grade assumption for AI routes (grade handling is 🔒 M0.12; the adapter
    #                         would stamp a flat grade and flag it, never invent a profile).
    #   default_stop_s    : fallback dwell when a point gives no 'stop_s'.
    #
    # RETURNS (once implemented): {'waypoints': [Waypoint, ...], 'assumptions': [...]} where cumulative
    #   road distance from the injected road_distance_fn fills Waypoint.distance, matching the VDRI/typed
    #   output so the driver model needs no adapter.
    raise NotImplementedError("blocked: map provider not chosen")
