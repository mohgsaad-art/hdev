"""Line-by-line Python port of VECTO's bus Steady State Model (SSM) for HVAC.  (Gate 3, rule 4 [VECTO])

Source: github.com/mohgsaad-art/VECTO, branch IEPC-experiments, commit b8d6126ab0bc2ab8beb3eaee878f7198126b600a.
File abbreviations used in the "C# ..." citations:
  SR = VectoCore/VectoCore/Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/SSMRun.cs
  SC = .../Impl/HVAC/SSMCalculate.cs
  SI = .../Impl/HVAC/SSMInputs.cs
  CO = VectoCore/VectoCore/Configuration/Constants.cs
  DD = VectoCore/VectoCore/Models/Declaration/DeclarationData.cs
  RD = VectoCore/VectoCore/InputData/Reader/ComponentData/EnvironmentalContidionsMapReader.cs
  HD = .../HeatingDistributionMap.cs
  M14 = VectoCore/VectoCore/Models/BusAuxiliaries/DownstreamModules/Impl/M14Impl.cs

SI units are NOT used here on purpose: the port keeps VECTO's own numbers (degC, W, 1/h) so that every line can be
compared with the C# line next to it.  It is a TEST tool (docs/research), not engine code.

What is ported:   SR TotalW/TCalc; SC base heating/cooling/ventilation power; SC heating distribution and caps;
                  SC COP handling (incl. "COP missing -> 0 W" silent rule); SC weighted sum over environmental
                  conditions; SC technology benefits; M14 waste-heat formula.
What is NOT ported: mechanical compressor power chain after the SSM (alternator, crank), engineering-mode SSM
                  (SimpleSSMTool), fuel consumption of the aux heater in litres.
"""
import csv
import os
import math

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "vecto_data")

# ---- constants ------------------------------------------------------------------------------------------------
# CO 91-118 (class SteadyStateModel) -- declaration-mode constants
PASSENGER_BOUNDARY_T = 17.0          # CO 93
SOLAR_CLOUDING = (0.65, 0.8)         # CO 94-95  (low = T < 17, high)
HEAT_PER_PASSENGER = (50.0, 80.0)    # CO 96-97  (low = T < 17, high)
MAX_DELTA_LOWFLOOR = 3.0             # CO 99  (the .AHSM engineering default file says 4.0: SSMDefaults.AHSM; not used in declaration)
MAX_TECH_BENEFIT = 0.5               # CO 100 (SSMDefaults.AHSM says 0.03)
HEATING_BOUNDARY_T = 18.0            # CO 102
COOLING_BOUNDARY_T = 23.0            # CO 103
HIGH_VENT, HIGH_VENT_HEATING, LOW_VENT = 20.0, 10.0, 7.0   # CO 105-107  [1/h]
AUX_HEATER_EFF_CO = 0.84             # CO 109 (declaration: the aenv column "fuel heater" 0.80 is what SC 187-189 uses)
SPEC_VENT_POWER = 0.56               # CO 111-112 [Wh/m3]
G_FACTOR = 0.95                      # CO 114
T_COOLING_TURNS_OFF = 17.0           # SI 77
SOLAR_LITERAL = 0.25                 # SR 61 (hard-coded literal, no name, no comment; same literal in the original Excel
                                     #   SSHVAC_V07 cell L89: =C47*D9*C17*C18*0.25)
U_VALUE = {"LowFloor": 4.0, "SemiLowFloor": 3.5, "HighFloor": 3.0}   # DD 553-564 [W/(K m2)]
HVAC_ELECTRIC_EFFICIENCY_FACTOR = 0.8   # DD 126 (lorry only: electric = mech / 0.8)
ELECTRIC_HEAT_PUMPS = ("R-744", "non R-744 continuous")   # ISSMDeclarationInputs.cs 323-326 IsElectrical()
HP_TYPES = ("R-744", "non R-744 2-stage", "non R-744 3-stage", "non R-744 4-stage", "non R-744 continuous")
# waste heat to cabin heater (CO 196-201, M14 55-61)
COOLANT_TO_CABIN = 0.75
FUEL_ENERGY_TO_COOLANT = 0.2
ELECTRIC_WASTE_HEAT_TO_COOLANT = 0.9


def _num(s):
    s = s.strip()
    if s in ("", "-"):
        return float("nan")
    return float(s)


# ---- data: environmental conditions (RD 37-94), heating distribution (HD, reader) ----------------------------
class Env:
    def __init__(self, id_, T, solar, weight, cop, heater_eff):
        self.id, self.T, self.solar, self.weight, self.cop, self.heater_eff = id_, T, solar, weight, cop, heater_eff


def read_env_map(path=None):
    path = path or os.path.join(DATA, "DefaultClimatic.aenv")
    rows = list(csv.reader(open(path, newline="")))
    head = [h.strip() for h in rows[0]]
    envs = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        d = {h: v.strip() for h, v in zip(head, r)}
        cop = {k: _num(d[k]) for k in HP_TYPES if not math.isnan(_num(d[k]))}              # RD 66-70 (NaN -> key absent)
        heater = {k: _num(d[k]) for k in ("water electric heater", "air electric heater", "other electric heating",
                                           "fuel heater") if k in d and not math.isnan(_num(d[k]))}   # RD 73-77
        envs.append(Env(int(d["ID"]), _num(d["EnvTemp"]), _num(d["Solar"]), _num(d["WeightingFactor"]), cop, heater))
    s = sum(e.weight for e in envs)                                                         # RD 88-91 normalise weights
    for e in envs:
        e.weight /= s
    return envs


def read_heating_distribution(path=None):
    """HD reader: value/100, '-' -> NaN (treated as 0 by Entry.Get...Contribution, HD 41-58)."""
    path = path or os.path.join(DATA, "HeatingDistribution.csv")
    out = {}
    lines = [l for l in open(path) if l.strip() and not l.lstrip().startswith("#")]
    rdr = csv.reader(lines)
    head = [h.strip() for h in next(rdr)]
    for r in rdr:
        d = {h: v.strip() for h, v in zip(head, r)}
        hp = {k: _num(d[k]) / 100.0 for k in HP_TYPES}
        out[(d["HeatingDistributionCase"], int(d["Environmental ID"]))] = dict(
            hp=hp, eh=_num(d["electric heater"]) / 100.0, fuel=_num(d["fuel heater"]) / 100.0)
    return out


def read_hd_cases(path=None):
    path = path or os.path.join(DATA, "HeatingDistributionCases.csv")
    lines = [l for l in open(path) if l.strip()]
    rdr = csv.reader(lines)
    head = [h.strip() for h in next(rdr)]
    entries = []
    for r in rdr:
        d = {h: v.strip() for h, v in zip(head, r)}
        allowed = [k for k in HP_TYPES if d[k] == "1"] or ["none"]
        entries.append((d["HeatingDistributionCase"], allowed[0], d["electric heater"] == "1", d["fuel heater"] == "1"))
    return entries


def heating_distribution_case(entries, hp, has_electric_heater, has_fuel_heater):
    """HeatingDistributionCasesMap.GetHeatingDistributionCase (file HeatingDistributionCasesMap.cs 77-86)."""
    m = [e[0] for e in entries if e[1] == hp and e[2] == has_electric_heater and e[3] == has_fuel_heater]
    if len(m) != 1:
        raise ValueError(f"Zero or more than one matching entry! {len(m)}")
    return m[0]


def hd_entry(hdtab, case, env_id):
    return hdtab[(case, env_id)]          # HD 17-24 (returns null if missing -> NullReference in C#)


def _nz(x):                                # HD 52, 57: NaN -> 0
    return 0.0 if (x is None or math.isnan(x)) else x


# ---- SR: heat balance -----------------------------------------------------------------------------------------
def t_calc(run, t_env, floor="HighFloor", t_heat=HEATING_BOUNDARY_T, t_cool=COOLING_BOUNDARY_T, d_low=MAX_DELTA_LOWFLOOR):
    """SR 26-45."""
    if run == 1:
        return t_heat                                                    # SR 36-38
    return max(t_cool, t_env - d_low) if floor == "LowFloor" else t_cool   # SR 40-44


def solar_clouding(t_env):             # SI 49-55
    return SOLAR_CLOUDING[0] if t_env < PASSENGER_BOUNDARY_T else SOLAR_CLOUDING[1]


def heat_per_passenger(t_env):         # SI 58-64
    return HEAT_PER_PASSENGER[0] if t_env < PASSENGER_BOUNDARY_T else HEAT_PER_PASSENGER[1]


def total_w(run, t_env, solar, surface, window, u, n_pass, g=G_FACTOR, floor="HighFloor"):
    """SR 48-64: Q_wall + persons + solar.   Positive = cabin gains heat."""
    q_wall = (t_env - t_calc(run, t_env, floor)) * surface * u                       # SR 56-57
    per = n_pass * heat_per_passenger(t_env)                                          # SR 58-59
    sol = solar * window * g * solar_clouding(t_env) * SOLAR_LITERAL                  # SR 60-61
    return q_wall + per + sol                                                         # SR 63


# ---- single-compartment point calculation, shares/COPs supplied (used for the Bob-vs-port grid) ---------------
def point_parts(t_env, solar, bus, cop_heat, cop_cool, hp_share, eh_share, fuel_share, max_heat, max_cool,
                waste_heat=0.0, eh_eff=0.93, fuel_eff=0.80, fuel_power=0.0,
                vent_on_heating=True, vent_when_idle=True, vent_during_ac=True, tech=None):
    """One environmental condition, one compartment (driver-compartment-like), electric heat pump and electric AC.
    Returns dict of electrical parts [W] exactly as VECTO adds them: hp, eh, ac, fan (+ fuel_in, heat demand).
    tech = dict(VH,VV,VC,C) technology benefits (SC 432-551), default none.
    Each line cites the C# line."""
    tech = tech or {}
    run1 = total_w(1, t_env, solar, bus["surface"], bus["window"], bus["U"], bus["n_pass"], bus.get("g", G_FACTOR), bus.get("floor", "HighFloor"))
    run2 = total_w(2, t_env, solar, bus["surface"], bus["window"], bus["U"], bus["n_pass"], bus.get("g", G_FACTOR), bus.get("floor", "HighFloor"))

    # --- heating demand: SC 757-771 (CalculateAverageHeatingPower)
    demand = 0.0
    if run1 < 0 and run2 < 0:                                                      # SC 763
        demand = abs(run1 if run1 > run2 else run2) - waste_heat                   # SC 764-769
    demand = max(demand, 0.0)                                                      # SC 771

    # --- heating distribution: SC 215-242
    aux_p = demand * _nz(fuel_share)                                               # SC 220
    hp_p = demand * _nz(hp_share)                                                  # SC 221
    eh_p = demand * _nz(eh_share)                                                  # SC 222
    s = min(max_heat, hp_p + eh_p)                                                 # SC 224
    denom = 1 - _nz(fuel_share)
    base = s if abs(denom) < 1e-9 else s / denom                                   # SC 225-227, 229-231  (IsEqual(0))
    hp_ltd = base * _nz(hp_share)                                                  # SC 228
    eh_ltd = base * _nz(eh_share)                                                  # SC 232

    # --- SC 191-211: COP division; NaN COP -> 0 W silently (SC 194-197)
    hp_el = 0.0 if math.isnan(cop_heat) else hp_ltd / cop_heat                     # SC 198-202
    eh_el = eh_ltd / eh_eff                                                        # SC 203-207
    fuel_in = min(fuel_power, aux_p) / fuel_eff * (1 - tech.get("H", 0.0))         # SC 208-210

    # --- cooling electrical: SC 337-374 + 553-578
    cooling = 0.0
    if t_env >= T_COOLING_TURNS_OFF and not (run1 <= 0 or run2 <= 0):             # SC 343, 356
        cooling = min(run1, run2)                                                  # SC 360
    ac_el = 0.0 if math.isnan(cop_cool) else min(cooling, max_cool) / cop_cool     # SC 566-570

    # --- ventilation: SC 272-296, 376-398, 400-427
    vp_heat = bus["volume"] * bus["vent_rate_heating"] * SPEC_VENT_POWER           # SI 88 (heating=true)
    vp_other = bus["volume"] * bus["vent_rate"] * SPEC_VENT_POWER                  # SI 88 (heating=false)
    v_heat = vp_heat if (run1 < 0 and run2 < 0 and vent_on_heating) else 0.0       # SC 290-292
    v_cool = vp_other if (t_env >= T_COOLING_TURNS_OFF and run1 > 0 and run2 > 0 and vent_during_ac) else 0.0   # SC 394-397
    idle = (t_env < T_COOLING_TURNS_OFF and run1 > 0 and run2 > 0) or (run1 > 0 and run2 < 0)   # SC 419-421
    v_idle = vp_other if (idle and vent_when_idle) else 0.0                        # SC 422-425
    # SC 697-704: I93 (vent during heating) x (1-I99=VH), I94 (vent during AC) x (1-I100=VC), I95 (idle vent) x (1-I101=VV)
    fan = v_heat * (1 - tech.get("VH", 0.0)) + v_cool * (1 - tech.get("VC", 0.0)) + v_idle * (1 - tech.get("VV", 0.0))
    return dict(run1=run1, run2=run2, demand=demand, hp=hp_el, eh=eh_el, ac=ac_el, fan=fan, fuel_in=fuel_in,
                total_el=hp_el + eh_el + ac_el + fan)


# ---- full bus (two compartments), weighted over the environmental conditions: used for the VECTO unit tests -----
class Bus:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def hd_distribution(bus, hd_case, hp_type, env, demand, max_power, hdtab):
    """SC 215-242 CalculateHeatingDistribution (returns hp_heat, eh_heat, aux_heat; heat, not electric)."""
    e = hd_entry(hdtab, hd_case, env.id)
    fuel = _nz(e["fuel"])
    aux = demand * fuel                                                    # SC 220
    hp_c = _nz(e["hp"].get(hp_type, 0.0)) if hp_type in e["hp"] else 0.0   # HD 41-48
    hp_p = demand * hp_c                                                   # SC 221
    eh_p = demand * _nz(e["eh"])                                           # SC 222
    s = min(max_power, hp_p + eh_p)                                        # SC 224
    base = s if abs(1 - fuel) < 1e-9 else s / (1 - fuel)                   # SC 225-231
    return base * hp_c, base * _nz(e["eh"]), aux


def calculate_heating_power(bus, env, hdtab, waste_heat):
    """SC 172-213 (+ 757-771).  Returns weighted sums of RequiredHeatingPower, HP el/mech, EH el, Aux fuel."""
    run1 = total_w(1, env.T, env.solar, bus.surface, bus.window, bus.U, bus.n_pass, bus.g, bus.floor)
    run2 = total_w(2, env.T, env.solar, bus.surface, bus.window, bus.U, bus.n_pass, bus.g, bus.floor)
    demand = 0.0
    if run1 < 0 and run2 < 0:
        demand = abs(run1 if run1 > run2 else run2) - waste_heat
    demand = max(demand, 0.0)
    dr, pa = bus.driver_contribution, bus.passenger_contribution                # SI 217-223
    d_hp = d_eh = d_aux = p_hp = p_eh = p_aux = 0.0
    hp_d, hp_p = bus.hp_driver, bus.hp_passenger
    d_hp, d_eh, d_aux = hd_distribution(bus, bus.hd_case_driver, hp_d, env, demand * dr, bus.max_heat_total * dr, hdtab)     # SC 178-179
    p_hp, p_eh, p_aux = hd_distribution(bus, bus.hd_case_passenger, hp_p, env, demand * pa, bus.max_heat_total * pa, hdtab)  # SC 180-181
    tech_fuel = 1 - bus.tech.get("H", 0.0)                                      # SC 182
    cop_d = env.cop.get(hp_d, float("nan"))                                     # SC 184
    cop_p = env.cop.get(hp_p, float("nan"))                                     # SC 185
    # SC 186: electric heater efficiency = mean over the heater types present that exist in env
    effs = [env.heater_eff[k] for k in bus.electric_heater_types if k in env.heater_eff]
    eh_eff = sum(effs) / len(effs) if effs else float("nan")
    fuel_eff = env.heater_eff.get("fuel heater", float("nan"))                  # SC 187-189
    def hp_term(heat, cop, hp):
        return 0.0 if math.isnan(cop) else heat / cop                          # SC 194-196
    # the C# splits mech/el per compartment (SC 236-237); do it per compartment here:
    hp_el = (hp_term(d_hp, cop_d, hp_d) if hp_d in ELECTRIC_HEAT_PUMPS else 0.0) + \
            (hp_term(p_hp, cop_p, hp_p) if hp_p in ELECTRIC_HEAT_PUMPS else 0.0)
    hp_mech = (hp_term(d_hp, cop_d, hp_d) if hp_d not in ELECTRIC_HEAT_PUMPS else 0.0) + \
              (hp_term(p_hp, cop_p, hp_p) if hp_p not in ELECTRIC_HEAT_PUMPS else 0.0)
    eh_el = 0.0 if math.isnan(eh_eff) else (d_eh + p_eh) / eh_eff              # SC 203-207
    aux = 0.0 if math.isnan(fuel_eff) else min(bus.fuel_power, d_aux + p_aux) / fuel_eff * tech_fuel   # SC 208-210
    w = env.weight
    return dict(required=demand * w, hp_el=hp_el * w, hp_mech=hp_mech * w, eh_el=eh_el * w, aux=aux * w)


def average_heater_power(bus, envs, hdtab, waste_heat=0.0):
    """SC 149-170 (batch mode): sum of weighted per-condition results."""
    tot = dict(required=0.0, hp_el=0.0, hp_mech=0.0, eh_el=0.0, aux=0.0)
    for env in envs:
        r = calculate_heating_power(bus, env, hdtab, waste_heat)
        for k in tot:
            tot[k] += r[k]
    return tot


def waste_heat_usable(engine_waste_heat_w=0.0, em_waste_heat_w=0.0):
    """M14 54-61: usable waste heat [W] = ICE heat*0.2*0.75 + EM heat*0.9*0.75 (averages over the cycle)."""
    return engine_waste_heat_w * FUEL_ENERGY_TO_COOLANT * COOLANT_TO_CABIN + \
        em_waste_heat_w * ELECTRIC_WASTE_HEAT_TO_COOLANT * COOLANT_TO_CABIN


# ---- cooling / ventilation electrical power, weighted: SC 553-578 and 684-707 --------------------------------------
def get_cop_cooling(bus, env):
    """SC 580-611."""
    if bus.requires_driver_ac and bus.requires_passenger_ac:                                   # SC 583
        cd = env.cop.get(bus.hp_driver, float("nan")); cp = env.cop.get(bus.hp_passenger, float("nan"))   # SC 587-588
        if math.isnan(cd) or math.isnan(cp):
            return float("nan")                                                                # SC 590-592
        return (bus.max_cool_driver * cd + bus.max_cool_passenger * cp) / (bus.max_cool_driver + bus.max_cool_passenger)   # SC 594-595
    if bus.requires_passenger_ac:
        return env.cop.get(bus.hp_passenger, float("nan"))                                     # SC 598-602
    if bus.requires_driver_ac:
        return env.cop.get(bus.hp_driver, float("nan"))                                        # SC 604-608
    return float("nan")                                                                        # SC 610


def electrical_w_adjusted(bus, envs):
    """SC 101-123 + 684-707. Returns weighted electrical power [W]."""
    tot = 0.0
    for env in envs:
        run1 = total_w(1, env.T, env.solar, bus.surface, bus.window, bus.U, bus.n_pass, bus.g, bus.floor)
        run2 = total_w(2, env.T, env.solar, bus.surface, bus.window, bus.U, bus.n_pass, bus.g, bus.floor)
        # H94 BaseCoolingW_ElectricalCoolingHeating SC 337-365
        h94 = 0.0
        if env.T >= T_COOLING_TURNS_OFF and not (run1 <= 0 or run2 <= 0):
            c = min(run1, run2)
            h94 = (c * bus.driver_contribution if bus.hp_driver in ELECTRIC_HEAT_PUMPS else 0.0) + \
                  (c * bus.passenger_contribution if bus.hp_passenger in ELECTRIC_HEAT_PUMPS else 0.0)
        vp_h = bus.volume * bus.vent_rate_heating * SPEC_VENT_POWER
        vp_o = bus.volume * bus.vent_rate * SPEC_VENT_POWER
        i93 = vp_h if (run1 < 0 and run2 < 0 and bus.vent_on_heating) else 0.0                 # SC 290-292
        i94 = vp_o if (env.T >= T_COOLING_TURNS_OFF and run1 > 0 and run2 > 0 and bus.vent_during_ac) else 0.0   # SC 394-397
        i95 = vp_o if (((env.T < T_COOLING_TURNS_OFF and run1 > 0 and run2 > 0) or (run1 > 0 and run2 < 0))
                       and bus.vent_idle) else 0.0                                             # SC 419-425
        lim = lambda x: max(-MAX_TECH_BENEFIT, min(MAX_TECH_BENEFIT, x))                       # SC 443-445 etc.
        h100 = lim(bus.tech.get("C", 0.0))                                                     # SC 511-513
        i99, i100, i101 = lim(bus.tech.get("VH", 0.0)), lim(bus.tech.get("VC", 0.0)), lim(bus.tech.get("VV", 0.0))
        cop = get_cop_cooling(bus, env)
        cooling = 0.0 if math.isnan(cop) else min(h94 * (1 - h100), bus.max_cool_total) / cop    # SC 701
        tot += (cooling + i93 * (1 - i99) + i94 * (1 - i100) + i95 * (1 - i101)) * env.weight   # SC 703-706
    return tot
