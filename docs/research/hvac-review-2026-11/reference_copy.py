"""Experimental variants of Bob's HVAC functions (rule 1: nothing in the notebook or src/ is edited).

Method: take the EXACT notebook cell text (cell_source), apply a small, visible text patch (old -> new), exec it in a COPY of the
namespace.  Every variant is therefore "Bob's code + one named change", and the patch is printed by `show_patches()` so the
before/after snippet in the report is generated from the real code.

Variants (engine = would change an engine function; parser = would be a parser job):
  v_step_cop        climate_lookup: COP = value of the NEAREST point (step, like VECTO's per-condition COP) instead of np.interp   [engine]
  v_linear_shares   climate_lookup: heating shares interpolated linearly instead of nearest point                                  [engine]
  v_cop_floor       parser-side: NaN COPs replaced by a given floor (e.g. 1.0) instead of the nearest value (flat clip)             [parser]
  v_fuel_eff        HVAC_thermal: fuel_heat returned as FUEL power (heat / fuel_eff) with the heater-power cap, like VECTO SC 208-210 [engine]
  v_vent_not_zero   (none) -- see report: nothing to patch
Inputs that already accept per-hour ARRAYS without any code change (checked in tests/hvac): U, A_surface (per-hour driving/parked UA),
N_persons, A_window, max_heating_power, max_cooling_power, solar_factor, Q.
"""
import copy
import numpy as np
from _load_notebook import cell_source, NS

PATCHES = {
    "v_step_cop": {13: [("cop_heat = np.interp(T_amb, T_heat_points, cop_heat_points)  # heat pump heating COP per hour",
                         "cop_heat = np.asarray(cop_heat_points, dtype=float)[np.argmin(np.abs(T_amb[..., None] - np.asarray(T_heat_points, dtype=float)), axis=-1)]"),
                        ("cop_cool = np.interp(T_amb, T_cool_points, cop_cool_points)  # cooling COP per hour",
                         "cop_cool = np.asarray(cop_cool_points, dtype=float)[np.argmin(np.abs(T_amb[..., None] - np.asarray(T_cool_points, dtype=float)), axis=-1)]")]},
    "v_linear_shares": {13: [("hp_share = np.asarray(hp_share_points, dtype=float)[idx]     # heat pump part of the heat",
                              "hp_share = np.interp(T_amb, T_heat_points, hp_share_points)"),
                             ("eh_share = np.asarray(eh_share_points, dtype=float)[idx]     # electric heater part",
                              "eh_share = np.interp(T_amb, T_heat_points, eh_share_points)"),
                             ("fuel_share = np.asarray(fuel_share_points, dtype=float)[idx] # fuel heater part",
                              "fuel_share = np.interp(T_amb, T_heat_points, fuel_share_points)")]},
    "v_fuel_eff": {11: [("return HVAC_el, fuel_heat", "return HVAC_el, np.minimum(fuel_heat, fuel_heater_power) / fuel_eff #")]},
}


def _patched(src, repl):
    for old, new in repl:
        if old not in src:
            raise ValueError(f"patch target not found: {old[:60]}")
        src = src.replace(old, new)
    return src


def make_namespace(name=None):
    """Namespace with Bob's functions (name=None) or with one named patch applied."""
    ns = {k: v for k, v in NS.items()}
    if name is None:
        return ns
    patches = PATCHES[name]
    for cell, repl in patches.items():
        src = _patched(cell_source(cell), repl)
        if name == "v_fuel_eff":                                  # the variant needs two extra arguments
            src = src.replace("Q=0.0, p=101325.0, R=287.05, cp=1005.0):", "Q=0.0, p=101325.0, R=287.05, cp=1005.0, fuel_heater_power=30000.0, fuel_eff=0.80):")
        exec(compile(src, f"<variant {name} cell {cell}>", "exec"), ns)
    # re-bind HVAC_thermal to the patched namespace if only a helper changed
    if 11 not in patches:
        exec(compile(cell_source(11), "<cell 11>", "exec"), ns)
    return ns


def variant(name):
    return make_namespace(name)["HVAC_thermal"]


def show_patches():
    for name, p in PATCHES.items():
        for cell, repl in p.items():
            for old, new in repl:
                print(f"--- {name} (notebook cell {cell})\n- {old}\n+ {new}")


if __name__ == "__main__":
    show_patches()
