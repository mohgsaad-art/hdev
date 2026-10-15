# STATUS: NEW (Step 9, item 15 / M4.1 + M6.5 + M6.12, Bob to review). runner.run(base, changes).
#
# WHAT THIS IS: the ORCHESTRATION layer behind real-mode POST /api/run (design §4C). It is NOT an
#   engine. It (a) applies change-sets over a base recording per-slot provided_by, (b) selects the
#   earliest stage whose entry contract is satisfiable, (c) REFUSES on an incomplete entry contract
#   naming exactly what is missing (no silent default - engine-rules §6 / design §4C / req §8.4),
#   (d) runs the pure engines in order, and (e) assembles a §3.3-SHAPED results dict using the SAME
#   client-facing keys and plain words as demo/demo_engine.py, with NULL for any stage that is still a
#   stub or blocked by a 🔒 item. mode='real', illustrative is false.
#
# WHAT IS NULL IN THIS BUILD (and why):
#   - consumption headline energy: the drive physics runs on per-vehicle/route slots, but the aero slot
#     CdxA_Default is 🔒 M1.1 (no source) and the consumption efficiencies are HDEV placeholders
#     (🔒 M0.21). A real run therefore cannot report a trustworthy energy number yet -> energy fields
#     are null until those unlock. (The engines themselves are DONE and pure; the DATA they need is
#     locked, so the orchestrator surfaces null rather than invent inputs.)
#   - charging / grid headline: depend on the (null) consumption hand-over and on dt (🔒 Energinet, no
#     default) -> null.
#   - tco: data model + category sums only; headline metrics 🔒 M6.24 -> null (src.server.tco).
#   - co2: interface + stub, sources 🔒 M6.25 -> null (src.server.co2).
#
# CRITICAL - NUMPY/GYM FREE AT IMPORT: importing src.server.runner (and the hdev.* modules that import
#   it) must NEVER force numpy or gym. So EVERY engine import is LAZY, inside the function that needs it.
#   The demo test suite imports hdev.run_api / demo.demo_engine and must stay numpy-free.
#
# §8 METHOD-HIDING: the assembled results JSON uses only the client-facing demo keys
#   (verdict/kpis/energy/charging/grid/tco/co2/plan/inputs_summary/settings/provenance) and PLAIN words.
#   No coefficient name (k_lin/k_roll/CdxA/P_wheel/P_aux/rho), no physics-source name (VECTO), and no
#   internal charging-strategy name (ASAP/JIT/EDF/ES/cost-based) ever reaches this surface - those live
#   in the engines/tests/docs only.
#
# PURITY: runner.run is a pure, deterministic, offline function of (base, changes). No network, no AI,
#   no clock dependence (the timestamp is a fixed ISO string so repeated runs match, like demo).

import copy
from typing import Any, Dict, List, Mapping, Optional, Tuple

# the four stage names, left-to-right (design §4A). sizing/sweep are operations around stages, not
# stages, so they are not in this list.
STAGES = ("consumption", "charging", "flexibility", "tco")

# the EXACT client-facing TCO category names (kept in step with src.server.tco / demo_engine).
_TCO_CATEGORY_NAMES = (
    "Owning", "Running", "Infrastructure", "Policy & taxes", "Hidden costs", "Climate",
)

# a fixed illustrative-free timestamp. real mode is deterministic in this build (no priced output yet),
# so the run id/timestamp are derived from the resolved project, never the wall clock.
_FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# (a) change-set application  (design §4E)
# ---------------------------------------------------------------------------

def apply_change_sets(base: Optional[Mapping[str, Any]],
                      changes: Optional[Any] = None) -> Dict[str, Any]:
    # merge a list of change-set writes over the base project, recording per-slot provided_by. an empty
    # (or None) change-set returns a deep copy of the base unchanged.
    #
    #   base    : the base project JSON (a dict of slots / stage inputs).
    #   changes : None, [] -> no-op. otherwise a list of writes [{key, slot, provided_by?}] OR a single
    #             such write OR a plain {key: value} mapping (convenience). each write records
    #             provided_by in a sibling 'provenance' map keyed by the slot key.
    project = copy.deepcopy(dict(base or {}))
    provenance: Dict[str, Any] = dict(project.get("provenance") or {})

    if not changes:
        project["provenance"] = provenance
        return project

    # normalise to a list of {key, slot/value, provided_by} writes.
    writes: List[Dict[str, Any]] = []
    if isinstance(changes, Mapping):
        # a plain {key: value} mapping (convenience), provided_by defaults to 'client'.
        for key, value in changes.items():
            writes.append({"key": key, "value": value, "provided_by": "client"})
    elif isinstance(changes, (list, tuple)):
        for item in changes:
            if isinstance(item, Mapping) and "key" in item:
                writes.append(dict(item))
            else:
                raise ValueError("apply_change_sets: each change-set write must be a {key, ...} mapping")
    else:
        raise ValueError("apply_change_sets: changes must be a list of writes or a {key: value} mapping")

    for w in writes:
        key = w["key"]
        value = w["slot"] if "slot" in w else w.get("value")
        provided_by = w.get("provided_by", "client")
        project[key] = value
        provenance[key] = {"provided_by": provided_by}

    project["provenance"] = provenance
    return project


# ---------------------------------------------------------------------------
# (b) + (c) stage selection and entry-contract check  (design §4B / §4C)
# ---------------------------------------------------------------------------

# the entry-contract required fields per stage (design §4B). these are the fields the orchestrator looks
# for on the project to decide a stage is satisfiable. kept deliberately small and plain.
_ENTRY_CONTRACT = {
    # chain head: the full project description (vehicles + routes + calendar/environment).
    "consumption": ("vehicles", "routes", "calendar_environment"),
    # a session list (the §3C hand-over) OR fed by consumption.
    "charging": ("sessions",),
    # a charging/load profile.
    "flexibility": ("load_profile",),
    # annual energy + peak power (TCO can run standalone from these per §4I).
    "tco": ("annual_energy_kWh", "peak_power_kW"),
}


def check_entry_contract(project: Mapping[str, Any], stage: str) -> List[str]:
    # return the list of entry-contract fields the project is MISSING for `stage` (empty list = ok).
    required = _ENTRY_CONTRACT.get(stage)
    if required is None:
        raise ValueError("check_entry_contract: unknown stage %r" % (stage,))
    missing = [f for f in required if project.get(f) in (None, "", [], {})]
    return missing


def select_start_stage(project: Mapping[str, Any]) -> Optional[str]:
    # pick the EARLIEST stage whose entry contract is fully satisfiable from the project (design §4C).
    # returns None if NO stage can start (the caller turns that into a refusal listing consumption's
    # missing fields, the chain head).
    for stage in STAGES:
        if not check_entry_contract(project, stage):
            return stage
    return None


class RefusalError(ValueError):
    # raised when no stage can start / the selected stage's entry contract is incomplete. carries the
    # plain-language message AND the structured missing-field list so the transport can map it to a 400.
    def __init__(self, message: str, stage: Optional[str], missing: List[str]):
        super().__init__(message)
        self.stage = stage
        self.missing = missing


# ---------------------------------------------------------------------------
# (d) run_from: call the engines in order, null for stubbed/blocked stages
# ---------------------------------------------------------------------------

def _null_energy() -> Dict[str, Any]:
    # consumption headline is null in this build (CdxA 🔒 M1.1 + efficiencies 🔒 M0.21). the SHAPE
    # mirrors demo_engine.energy so the UI renders "Not yet available" in the same slots.
    return {
        "monthly_avg_kwh": None,
        "avg_day_kwh": None,
        "hardest_day_kwh": None,
        "per_vehicle": None,
    }


def _null_charging() -> Dict[str, Any]:
    return {
        "soc_profile": None,
        "strategies": None,
    }


def _null_grid() -> Dict[str, Any]:
    return {
        "load_24h_kw": None,
        "limit_kw": None,
        "flex_24h_kw": None,
        "flex_mwh_per_day": None,
    }


def _tco_block() -> Dict[str, Any]:
    # the real TCO block: data model + category sums only, headline metrics null (🔒 M6.24). built from
    # src.server.tco so there is one source of the category names/structure.
    from src.server import tco as tco_mod

    model = tco_mod.empty_tco_model()
    sums = tco_mod.tco_category_sums(model["categories"])  # all None (no line items supplied yet)
    metrics = tco_mod.headline_metrics(model)              # all None (locked)
    # shape to match demo_engine.tco: categories as {name, diesel, electric}, cumulative/break_even null.
    return {
        "years": None,
        "categories": [{"name": s["name"], "diesel": s["diesel"], "electric": s["electric"]} for s in sums],
        "cumulative": {"diesel": None, "electric": None},
        "break_even_year": metrics["break_even_year"],
    }


def _co2_block(ownership_years: Optional[int]) -> Dict[str, Any]:
    # the real CO2 block: interface + stub, all figures null (🔒 M6.25). shape matches demo_engine.co2.
    from src.server import co2 as co2_mod

    r = co2_mod.co2_result(ownership_years=ownership_years)
    return {
        "diesel_t_per_year": r["diesel_t_per_year"],
        "electric_t_per_year": r["electric_t_per_year"],
        "cumulative_saved_t": r["cumulative_saved_t"],
    }


def run_from(start: str, project: Mapping[str, Any]) -> Dict[str, Any]:
    # run the pipeline from `start` to the end, returning the per-stage result blocks. stages BEFORE the
    # start are treated as "supplied" (fed by the project); stages that are stubbed/blocked return null.
    # in THIS build every physics headline is null (see module header), so run_from returns the null
    # blocks for consumption/charging/flexibility/grid and the real-but-null tco/co2 blocks.
    #
    # the engines are DONE and pure; they are NOT invoked here with invented inputs. when the locked
    # data (CdxA, efficiencies, dt, prices, LCA/grid factors) is sourced, this is the single place that
    # wires the pure engines into live headline numbers.
    ownership_years = project.get("ownership_years")
    if not isinstance(ownership_years, int):
        ownership_years = None

    blocks = {
        "energy": _null_energy(),
        "charging": _null_charging(),
        "grid": _null_grid(),
        "tco": _tco_block(),
        "co2": _co2_block(ownership_years),
    }
    return blocks


# ---------------------------------------------------------------------------
# runner.run  (design §4C)
# ---------------------------------------------------------------------------

def _settings_from_project(project: Mapping[str, Any]) -> Dict[str, Any]:
    # echo back the client-facing settings the project carried (same keys demo emits), with plain
    # defaults where absent. NO engine-internal term appears here.
    return {
        "fleet_size": project.get("fleet_size"),
        "charging_priority": project.get("charging_priority"),
        "electricity_price": project.get("electricity_price"),
        "weather_year": project.get("weather_year"),
        "ownership_years": project.get("ownership_years"),
        "shift_end": project.get("shift_end"),
    }


def _run_id(project: Mapping[str, Any], start: str) -> str:
    import hashlib

    seed = "|".join(str(project.get(k)) for k in sorted(project.keys()) if k != "provenance")
    return "real-" + hashlib.sha256((start + "|" + seed).encode("utf-8")).hexdigest()[:12]


def run(base: Optional[Mapping[str, Any]], changes: Optional[Any] = None) -> Dict[str, Any]:
    # the real-mode entry point. applies change-sets, selects the start stage, REFUSES on an incomplete
    # entry contract (raising RefusalError with the missing fields named), runs the pipeline, and
    # assembles the §3.3-shaped results dict with mode='real' and nulls where a stage is stubbed/blocked.
    project = apply_change_sets(base, changes)

    start = select_start_stage(project)
    if start is None:
        # nothing can start: refuse, listing what the CHAIN HEAD (consumption) needs. this is the clear,
        # no-silent-default refusal of design §4C / req §8.4.
        missing = check_entry_contract(project, "consumption")
        raise RefusalError(
            "Cannot run: the project is missing the inputs needed to start. "
            "Missing: " + ", ".join(missing) + ".",
            stage="consumption",
            missing=missing,
        )

    # the selected stage's entry contract is satisfiable by construction (select_start_stage checked it),
    # but re-check so a future caller that passes a stage directly still gets the explicit refusal.
    missing = check_entry_contract(project, start)
    if missing:
        raise RefusalError(
            "Cannot start at %s: missing %s." % (start, ", ".join(missing)),
            stage=start,
            missing=missing,
        )

    blocks = run_from(start, project)
    settings = _settings_from_project(project)
    ownership_years = settings.get("ownership_years")

    # provenance: which slots were provided_by whom (from apply_change_sets) + which stages ran vs were
    # supplied. plain words only.
    stage_index = STAGES.index(start)
    stages_report = {
        "start_stage": start,
        "simulated": list(STAGES[stage_index:]),
        "supplied_before": list(STAGES[:stage_index]),
    }

    results = {
        "run_id": _run_id(project, start),
        "timestamp": _FIXED_TIMESTAMP,
        "mode": "real",
        "illustrative": False,
        "settings": settings,
        # verdict is null in this build: no priced/headline number is available, so the orchestrator does
        # not assert a can-electrify verdict. the UI shows "Not yet available".
        "verdict": {
            "can_electrify": None,
            "headline": None,
            "reason": None,
        },
        "kpis": {
            "battery_kwh": None,
            "charger_kw": None,
            "charger_count": None,
            "ready_by": None,
            "grid_peak_kw": None,
            "grid_limit_kw": None,
            "grid_fits": None,
            "tco_diff_dkk": None,
            "break_even_year": None,
            "co2_saved_t_per_year": None,
        },
        "energy": blocks["energy"],
        "charging": blocks["charging"],
        "grid": blocks["grid"],
        "tco": blocks["tco"],
        "co2": blocks["co2"],
        "plan": None,
        "inputs_summary": None,
        "provenance": {
            "slots": project.get("provenance", {}),
            "stages": stages_report,
        },
    }
    return results
