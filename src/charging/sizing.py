# STATUS: NEW (Step 9, item 11 / M3.1 + 🔒 M3.2, Bob to review). Battery sizing, two modes.
#
# MODE A (M3.1, DECIDED): the pack size comes straight from the vehicle datasheet. No loop, no model -
#   size_battery_mode_a(datasheet_kwh) simply validates and returns the datasheet value. This is the
#   path used when the truck's battery is already specified.
#
# MODE B (🔒 M3.2): "glider + kWh/kg + payload iterate" - estimate the pack size that a given glider,
#   payload and energy demand imply, accounting for the fact that a bigger pack is heavier, which raises
#   the energy demand, which needs a bigger pack... a fixpoint. The two inputs that have NO
#   HDEV-provided source are:
#     - glider_mass_kg   (the mass of the truck WITHOUT the battery pack)
#     - pack_kwh_per_kg  (pack-level gravimetric energy density, kWh per kg)
#   Per the rules we do NOT invent those numbers and we do NOT default them: they are REQUIRED
#   arguments. DECISION (recorded in FEAT-004 findings): because the iteration STRUCTURE runs purely
#   from the required arguments once the caller supplies them, we IMPLEMENT the fixpoint loop (it is
#   just arithmetic on the arguments) and FLAG that the SOURCES for glider_mass_kg and pack_kwh_per_kg
#   are not provided by HDEV - the caller must supply sourced values or the result stays flagged. We do
#   NOT stub it out, because stubbing would hide a working structure behind a lock that only concerns
#   the data source, not the method.
#
# PURITY (engine rule 7): every parameter is an argument; no I/O; works for any vehicle.
# FAIL LOUDLY (engine rule 6): non-positive / missing inputs raise; a non-converging fixpoint raises.

# SI note: masses in kg, energy in kWh, distance in km, energy intensity in kWh/km. The caller converts
# tonnes <-> kg at the UI edge (engine rule: SI inside).


def size_battery_mode_a(datasheet_kwh):
    # MODE A (decided): the datasheet value IS the pack size. Validate and return it unchanged.
    if datasheet_kwh is None:
        raise ValueError("size_battery_mode_a: datasheet_kwh is required (no invented size)")
    if datasheet_kwh <= 0:
        raise ValueError("size_battery_mode_a: datasheet_kwh must be > 0, got %r" % (datasheet_kwh,))
    return float(datasheet_kwh)


def size_battery_mode_b(
    glider_mass_kg,
    pack_kwh_per_kg,
    payload_kg,
    energy_per_km_per_kg,
    range_km,
    usable_fraction=1.0,
    max_iter=200,
    tol_kwh=1e-6,
):
    # MODE B (🔒 M3.2 on the DATA SOURCES; the method below is just arithmetic on the arguments).
    #
    # Required arguments (NO defaults, NO invented sources - the caller must supply sourced values):
    #   glider_mass_kg       : truck mass without the battery pack, kg.
    #   pack_kwh_per_kg      : pack gravimetric energy density, kWh per kg (pack size <-> pack mass).
    #   payload_kg           : carried payload, kg.
    #   energy_per_km_per_kg : drive energy intensity, kWh per km PER kg of total mass. This is the
    #                          mass-sensitivity of consumption the fixpoint turns on; the caller gets it
    #                          from the consumption engine for the vehicle/route. Required.
    #   range_km             : the daily/route range the pack must cover between charges, km. Required.
    # Optional (sane, source-free arithmetic knobs, flagged):
    #   usable_fraction      : usable share of the nominal pack (e.g. SOC window). Default 1.0 = neutral.
    #   max_iter, tol_kwh    : fixpoint controls.
    #
    # The fixpoint:
    #   total_mass   = glider_mass_kg + payload_kg + pack_mass
    #   energy_need  = energy_per_km_per_kg * range_km * total_mass          (kWh of usable energy)
    #   nominal_pack = energy_need / usable_fraction                         (kWh nameplate)
    #   pack_mass    = nominal_pack * ... wait: mass = nominal_pack / pack_kwh_per_kg
    # Iterate pack_mass until it stops moving. Converges when the per-km-per-kg energy and the pack
    # specific energy are such that each extra kg of pack adds less than 1 kg of required pack
    # (otherwise the design is infeasible and we raise - a real finding, not a silent number).
    #
    # Returns {'battery_kwh', 'pack_mass_kg', 'total_mass_kg', 'iterations', 'assumptions'}.

    # ---- validate (fail loudly, no defaults for the sourced inputs) ----
    for name, val in (
        ("glider_mass_kg", glider_mass_kg),
        ("pack_kwh_per_kg", pack_kwh_per_kg),
        ("payload_kg", payload_kg),
        ("energy_per_km_per_kg", energy_per_km_per_kg),
        ("range_km", range_km),
    ):
        if val is None:
            raise ValueError("size_battery_mode_b: %s is required (no invented source)" % name)
    if glider_mass_kg <= 0:
        raise ValueError("size_battery_mode_b: glider_mass_kg must be > 0, got %r" % (glider_mass_kg,))
    if pack_kwh_per_kg <= 0:
        raise ValueError("size_battery_mode_b: pack_kwh_per_kg must be > 0, got %r" % (pack_kwh_per_kg,))
    if payload_kg < 0:
        raise ValueError("size_battery_mode_b: payload_kg must be >= 0, got %r" % (payload_kg,))
    if energy_per_km_per_kg <= 0:
        raise ValueError("size_battery_mode_b: energy_per_km_per_kg must be > 0, got %r" % (energy_per_km_per_kg,))
    if range_km <= 0:
        raise ValueError("size_battery_mode_b: range_km must be > 0, got %r" % (range_km,))
    if not (0.0 < usable_fraction <= 1.0):
        raise ValueError("size_battery_mode_b: usable_fraction must be in (0,1], got %r" % (usable_fraction,))

    # ---- fixpoint iteration ----
    pack_mass = 0.0  # start with no pack, let it grow
    nominal_pack = 0.0
    iterations = 0
    for iterations in range(1, max_iter + 1):
        total_mass = glider_mass_kg + payload_kg + pack_mass
        energy_need = energy_per_km_per_kg * range_km * total_mass   # usable kWh needed
        new_nominal_pack = energy_need / usable_fraction             # nameplate kWh
        new_pack_mass = new_nominal_pack / pack_kwh_per_kg           # kg

        if abs(new_nominal_pack - nominal_pack) <= tol_kwh:
            nominal_pack = new_nominal_pack
            pack_mass = new_pack_mass
            break
        nominal_pack = new_nominal_pack
        pack_mass = new_pack_mass
    else:
        # did not converge inside max_iter -> the pack grows without bound (each kg of pack needs more
        # than a kg of pack). That is an infeasible design, not a number we are allowed to guess.
        raise ValueError(
            "size_battery_mode_b: fixpoint did not converge in %d iterations - the pack mass diverges "
            "(each added kg of pack requires >1 kg of pack for this energy intensity / specific energy). "
            "Infeasible design or wrong units." % max_iter
        )

    total_mass = glider_mass_kg + payload_kg + pack_mass
    assumptions = [
        "SOURCE FLAG (🔒 M3.2): glider_mass_kg and pack_kwh_per_kg are NOT HDEV-provided - the caller "
        "supplied them. The iteration method is sound arithmetic, but the RESULT inherits the "
        "uncertainty of those two source-less inputs and must be shown flagged.",
    ]
    if usable_fraction != 1.0:
        assumptions.append("usable_fraction=%.3f applied (SOC window), caller-supplied." % usable_fraction)

    return {
        "battery_kwh": nominal_pack,
        "pack_mass_kg": pack_mass,
        "total_mass_kg": total_mass,
        "iterations": iterations,
        "assumptions": assumptions,
    }
