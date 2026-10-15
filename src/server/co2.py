# STATUS: NEW (Step 9, item 18 / 🔒 M6.25, Bob to review). CO2 INTERFACE + STUB.
#
# WHAT THIS IS: the interface for a well-to-wheel + production (LCA) CO2 comparison between a diesel and
#   an electric fleet, plus a STUB body. The sources this needs - LCA factors (vehicle/battery
#   production) and the grid emission-factor time series - are 🔒 M6.25 (not yet sourced), so there is
#   no number to return. Per the master prompt we return a NULL-FILLED structure (not a raise) so the
#   runner can surface every field as null -> the UI shows "Not yet available". A hard raise is also
#   offered (co2_result_strict) for callers that prefer to fail loudly off-pipeline.
#
# INTENDED SLOT SET (design §4I CO2 note), documented so the structure is ready when M6.25 unlocks:
#   - vehicle_production_co2_t      : embodied CO2 of the glider/vehicle (LCA), tonnes. SOURCE: ICCT /
#                                     T&E / IVL / Energistyrelsen - to be sourced.
#   - battery_production_co2_t_per_kwh : embodied CO2 of the battery pack per kWh of capacity. SOURCE:
#                                     IVL / ICCT - to be sourced.
#   - grid_emission_factor_series   : grid CO2 intensity over time (a DECLINING curve), kg/kWh per year
#                                     or per hour. SOURCE: Energistyrelsen / Energinet - to be sourced.
#   - diesel_well_to_wheel_kg_per_l : diesel WTW emission factor, kg CO2 per litre. SOURCE: to be sourced.
#
# §8 METHOD-HIDING: the client-facing output uses PLAIN words (diesel_t_per_year / electric_t_per_year /
#   cumulative_saved_t) - the SAME keys the demo co2 block uses - and never names an LCA source or an
#   emission-factor coefficient on the result surface.
#
# PURITY: pure function of its arguments; no I/O, no numbers baked in.

from typing import Any, Dict, List, Mapping, Optional

_BLOCK = "blocked by M6.25"

# the slot keys this model will read once M6.25 unlocks (documented, all unsourced today).
CO2_SLOT_KEYS = (
    "vehicle_production_co2_t",
    "battery_production_co2_t_per_kwh",
    "grid_emission_factor_series",
    "diesel_well_to_wheel_kg_per_l",
)


def co2_result(
    annual_energy_kwh: Optional[float] = None,
    annual_diesel_litres: Optional[float] = None,
    battery_kwh: Optional[float] = None,
    ownership_years: Optional[int] = None,
    slots: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    # INTERFACE + STUB. The arguments are the quantities a real CO2 model would consume; `slots` would
    # carry the 🔒 M6.25 LCA/grid factors. Because those sources are not available, every output figure
    # is NULL. The structure matches the demo co2 block's client-facing keys so the runner/report can
    # render it directly (as "Not yet available").
    cumulative: Optional[List[Optional[float]]] = None
    if isinstance(ownership_years, int) and ownership_years > 0:
        # a per-year series shaped for the UI chart, every point null (no factor to multiply by).
        cumulative = [None] * (ownership_years + 1)

    return {
        "diesel_t_per_year": None,
        "electric_t_per_year": None,
        "cumulative_saved_t": cumulative,
        "available": False,
        "flag": "CO2 comparison is %s: LCA factors (vehicle/battery production) and the grid "
                "emission-factor time series are not yet sourced." % _BLOCK,
    }


def co2_result_strict(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    # the loud variant: for callers off the UI pipeline who prefer a hard failure to a null structure.
    raise NotImplementedError(_BLOCK)
