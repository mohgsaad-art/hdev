# STATUS: NEW (Step 9, item 17 / 🔒 M6.24, Bob to review). TCO DATA MODEL + CATEGORY SUMS ONLY.
#
# WHAT THIS IS (and is NOT): this file defines the SHAPE of a total-cost-of-ownership breakdown and the
#   arithmetic that SUMS line items into category totals. It is NOT a priced TCO model. Per 🔒 M6.24 the
#   headline metrics (TCO/km, breakeven, monthly cost) stay LOCKED until the coefficients are sourced,
#   and per the no-invented-numbers rule (master prompt §0) NO price or coefficient is hard-coded here -
#   every line-item value and every method coefficient is a to-be-sourced SLOT that starts None.
#
#   design §4I is the contract: price/tariff slots carry source+date+version; the method shapes
#   (annuity + residual balloon, lost-production, breakeven, lademeter, DSO fee, cheapest-N-hours
#   electricity) are from COWI, but "every coefficient is a to-be-sourced slot" and "no COWI number is a
#   default". So this module gives you the category/line-item container and category_sums; it computes a
#   headline metric ONLY when the caller has filled the required coefficient slots, otherwise returns
#   None for that metric. The runner surfaces those Nones as "Not yet available".
#
# §8 METHOD-HIDING: the category names are the SIX client-facing names used by the demo and §5.6
#   (Owning / Running / Infrastructure / Policy & taxes / Hidden costs / Climate). This module never
#   emits a coefficient name or a formula name on a client-facing surface - those live in the slot
#   `source` strings and in docs only.
#
# PURITY: pure functions of their arguments; no I/O, no prices baked in.

from typing import Any, Dict, List, Mapping, Optional

# the SIX client-facing TCO category names, IN ORDER (demo_engine.cats order / §5.6).
CATEGORY_NAMES = (
    "Owning",
    "Running",
    "Infrastructure",
    "Policy & taxes",
    "Hidden costs",
    "Climate",
)


def new_slot(unit: Optional[str] = None, source: Optional[str] = None,
             label: str = "to-be-sourced") -> Dict[str, Any]:
    # one to-be-sourced coefficient / line-item SLOT. value starts None (no invented number). The slot
    # records its unit and WHY it is empty (source note) so the assumptions list can report it.
    return {
        "value": None,
        "unit": unit,
        "source": source,
        "label": label,          # 'to-be-sourced' until a real {VECTO/REG/literature/...} source lands
        "locked": True,          # 🔒 M6.24: locked until sourced
    }


def new_line_item(name: str, unit: str = "DKK",
                  diesel: Optional[float] = None,
                  electric: Optional[float] = None,
                  source: Optional[str] = None) -> Dict[str, Any]:
    # a single cost LINE ITEM inside a category. diesel/electric are the two totals for this line; both
    # start None (no price hard-coded). The caller fills them from sourced slots or leaves them None.
    return {
        "name": name,
        "unit": unit,
        "diesel": diesel,
        "electric": electric,
        "source": source,
        "label": "to-be-sourced" if (diesel is None and electric is None) else "supplied",
    }


def new_category(name: str, line_items: Optional[List[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    # a TCO category: a client-facing name plus a list of line items. name must be one of the six.
    if name not in CATEGORY_NAMES:
        raise ValueError("tco: unknown category name %r (allowed: %s)" % (name, ", ".join(CATEGORY_NAMES)))
    return {
        "name": name,
        "line_items": [dict(li) for li in (line_items or [])],
    }


def empty_tco_model() -> Dict[str, Any]:
    # the EMPTY TCO data model: all six categories, each with no line items yet, plus the method
    # coefficient slots (all None, locked). This is what the runner emits when no priced TCO is possible
    # (which is always, under 🔒 M6.24) - a structurally-complete container with every number null.
    return {
        "categories": [new_category(n) for n in CATEGORY_NAMES],
        "method_slots": _method_coefficient_slots(),
        "flag": "TCO headline metrics are blocked by M6.24 (coefficients not yet sourced); "
                "category sums are available once line items are supplied.",
    }


def _method_coefficient_slots() -> Dict[str, Dict[str, Any]]:
    # the COWI method SHAPES (design §4I) expressed as to-be-sourced coefficient slots. NO number is set:
    # the formula shapes exist so the structure is ready, but every coefficient is None until sourced.
    return {
        # financing = PMT annuity + residual balloon
        "interest_rate": new_slot(unit="fraction/yr", source="design §4I annuity; coefficient to be sourced"),
        "residual_value_fraction": new_slot(unit="fraction", source="design §4I residual balloon; to be sourced"),
        "ownership_years": new_slot(unit="yr", source="client input / design §4I; to be sourced"),
        # lost-production cost (EV) = monthly fixed x (public-charging h / daily operating h)
        "monthly_fixed_cost": new_slot(unit="DKK/month", source="design §4I lost-production; to be sourced"),
        "public_charging_hours": new_slot(unit="h", source="design §4I lost-production; to be sourced"),
        "daily_operating_hours": new_slot(unit="h", source="design §4I lost-production; to be sourced"),
        # breakeven = capex difference / avg monthly operating saving
        "capex_difference": new_slot(unit="DKK", source="design §4I breakeven; to be sourced"),
        "avg_monthly_operating_saving": new_slot(unit="DKK/month", source="design §4I breakeven; to be sourced"),
        # lademeter = TCO/km / 13.6 m  (13.6 is a trailer-length constant, not a price - still a slot)
        "trailer_length_m": new_slot(unit="m", source="design §4I lademeter; to be sourced"),
        # DSO connection fee = base + per-A (DSO-specific, e.g. Radius formula)
        "dso_fee_base": new_slot(unit="DKK", source="design §4I DSO fee; DSO-specific, to be sourced"),
        "dso_fee_per_amp": new_slot(unit="DKK/A", source="design §4I DSO fee; DSO-specific, to be sourced"),
        # electricity = mean of the cheapest N hours/day x ToU
        "cheapest_hours_n": new_slot(unit="h", source="design §4I electricity; to be sourced"),
        "electricity_price_series": new_slot(unit="DKK/kWh", source="design §4I ToU series; to be sourced (versioned)"),
    }


# ---------------------------------------------------------------------------
# CATEGORY SUMS (the only arithmetic this module performs)
# ---------------------------------------------------------------------------

def tco_category_sums(categories: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    # sum each category's line items into {name, diesel, electric}. A line item whose total is None
    # contributes nothing (it is unsourced); if a category has NO supplied totals at all, its sum is
    # None (not 0) so the UI shows "Not yet available" rather than a misleading zero.
    out: List[Dict[str, Any]] = []
    for cat in categories:
        name = cat["name"]
        items = cat.get("line_items", [])
        diesel_vals = [li.get("diesel") for li in items if li.get("diesel") is not None]
        electric_vals = [li.get("electric") for li in items if li.get("electric") is not None]
        out.append({
            "name": name,
            "diesel": sum(diesel_vals) if diesel_vals else None,
            "electric": sum(electric_vals) if electric_vals else None,
        })
    return out


def tco_totals(category_sums: List[Mapping[str, Any]]) -> Dict[str, Optional[float]]:
    # overall diesel/electric totals across categories. None when nothing is supplied for a side.
    diesel_vals = [c.get("diesel") for c in category_sums if c.get("diesel") is not None]
    electric_vals = [c.get("electric") for c in category_sums if c.get("electric") is not None]
    return {
        "diesel": sum(diesel_vals) if diesel_vals else None,
        "electric": sum(electric_vals) if electric_vals else None,
    }


def headline_metrics(model: Mapping[str, Any]) -> Dict[str, Optional[float]]:
    # 🔒 M6.24: the headline metrics (TCO/km, breakeven year, monthly cost) are LOCKED until the method
    # coefficient slots are sourced. Since no coefficient is set (all None), every metric returns None.
    # This is intentionally not a stub-raise: the runner needs a null-filled structure to surface
    # "Not yet available" per the master prompt. Should a coefficient ever be filled, this is where the
    # formula shapes in design §4I would compute - but that is Bob's off-lock work, not Step 9.
    return {
        "tco_per_km_dkk": None,
        "break_even_year": None,
        "monthly_cost_dkk": None,
        "lademeter_dkk_per_m": None,
    }
