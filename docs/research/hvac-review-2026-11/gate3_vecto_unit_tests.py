"""Gate 3a: run the Python port (vecto_ssm_port.py) against the expected values that VECTO's OWN unit tests assert.

VECTO test file (commit b8d6126):
  VectoCore/VectoCoreTest/Models/Declaration/BusAux/SSMTestHeatingCooling.cs
  (bus: GetAuxParametersConventionalSingleDeckForTest, lines 1579-1617: Urban, class 31a, vehicle code CA, 4x2,
   not low entry, length 12 m, height 3 m, width 2.55 m, 40 seats, reference load)
The expected numbers below are COPIED from that file (line numbers in the 'src' column).  Tolerance = the test's own 1e-3.

Run:  python gate3_vecto_unit_tests.py      ->  gate3_vecto_unit_tests.csv
"""
import csv
import math
import os
import vecto_ssm_port as P

HERE = os.path.dirname(os.path.abspath(__file__))
ENVS = P.read_env_map()
HDT = P.read_heating_distribution()
HDC = P.read_hd_cases()
ENV = {e.id: e for e in ENVS}
TOL = 1e-3

# resource tables (kW, kW/m3 -> W, W/m3) as read by HVACLookup (HVACCoolingPower.cs: value*1000)
def _lookup(fname, cfg, col="Interurban"):
    rows = list(csv.reader(open(os.path.join(P.DATA, fname))))
    head = [h.strip() for h in rows[0]]
    for r in rows[1:]:
        if int(r[0]) == cfg:
            return float(r[head.index(col)]) * 1000.0
    raise KeyError(cfg)

DRIVER_ONLY_AC = (2, 4)
REQ_DRIVER = (2, 4, 7, 9)
REQ_PASS = tuple(c for c in range(1, 11) if c not in (1, 2, 3, 4))
HEAT_ELEC = {"Air": ["air electric heater"], "Water": ["water electric heater"], "Other": ["other electric heating"],
             "Other+Air": ["other electric heating", "air electric heater"], "Water+Air": ["water electric heater", "air electric heater"],
             "None": []}


def make_bus(cfg, cooling, hp_driver="none", hp_pass="none", heater="None", fuel_power=0.0,
             length=12.0, height=3.0, width=2.55, seats=40, tech_vc=0.04):
    """SpecificCompletedBusAuxiliaryDataAdapter.cs 325-420 (CreateSpecificSSMModelParameters) for vehicle code CA."""
    drv_only = cfg in DRIVER_ONLY_AC
    internal_len = 2 * 1.2 if (cooling and drv_only) else length         # adapter 336-340 (DriverCompartmentLength 1.2: Constants.cs 207)
    vent_len = length                                                     # adapter 341-343 (high floor single deck: DD 497-503)
    internal_h = height - 0.5                                             # DD 526-531 (class II, 3.0 m <= 3.1 m)
    width_c = 2.55 if 2.5 <= width <= 2.55 else width                     # DD 481-487
    surface = 2 * (length * width_c + internal_len * internal_h + 1.0 * width_c * height)   # adapter 358-359
    window = 1.5 * internal_len + 5.0                                     # adapter 356-357
    volume = (vent_len - 0.0) * width_c * internal_h                      # adapter 360
    vol_pass = (vent_len - 1.2 - 0.0) * internal_h * width                # adapter 106-111 / 128-133
    # DD 322-343 GetNumberOfPassengers: floor area = (internal length - 1.2 m) * width (DD 476-479); density 2.2 pass/m2
    # (CompletedBusSegmentationTable.csv line 9: vehicle code CA, class II, 2 axles -> group 32a, Interurban 2.2 / Coach 1.4;
    #  the test takes segment.Missions.FirstOrDefault() = Interurban [ASSUMPTION: first mission = Interurban])
    n_pass = min((internal_len - 1.2) * width_c * 2.2, seats) + 1         # adapter 363-367 (+1 driver)
    rate_vent = 7.0 if cfg in (1, 2) else 20.0                            # DD 454-470
    rate_heat = 7.0 if cfg in (1, 2) else 10.0
    max_cool_d = _lookup("HVACCoolingPowerDriver.csv", cfg)
    max_cool_p = _lookup("HVACCoolingPowerPassenger.csv", cfg) * vol_pass / 1000.0 * 1000.0 / 1000.0 * 1.0
    # note: HVACLookup multiplies the kW/m3 column by 1000 -> W/m3; times volume -> W
    max_cool_p = _lookup("HVACCoolingPowerPassenger.csv", cfg) * vol_pass
    max_heat_d = _lookup("HVACHeatingPowerDriver.csv", cfg)
    max_heat_p = _lookup("HVACHeatingPowerPassenger.csv", cfg) * vol_pass
    req_d, req_p = cfg in REQ_DRIVER, cfg in REQ_PASS
    if cooling:                                                           # adapter 389-402
        dl = (2 * 1.2 if drv_only else 1.2) if req_d else 0.0
        pl = (0.0 if drv_only else internal_len - 1.2) if req_p else 0.0
    else:                                                                 # adapter 403-414
        dl = 1.2 if req_d else 0.0
        pl = internal_len - 1.2 if req_d else internal_len
    tot = dl + pl
    has_eh = heater != "None"
    return P.Bus(
        surface=surface, window=window, volume=volume, U=P.U_VALUE["HighFloor"], n_pass=n_pass, g=P.G_FACTOR, floor="HighFloor",
        vent_rate=rate_vent, vent_rate_heating=rate_heat, vent_on_heating=True, vent_idle=True, vent_during_ac=True,
        hp_driver=hp_driver, hp_passenger=hp_pass, requires_driver_ac=req_d, requires_passenger_ac=req_p,
        driver_contribution=0.0 if tot == 0 else dl / tot, passenger_contribution=0.0 if tot == 0 else pl / tot,   # SI 217-223
        max_cool_driver=max_cool_d if req_d else 0.0, max_cool_passenger=max_cool_p if req_p else 0.0,
        max_cool_total=(max_cool_d if req_d else 0.0) + (max_cool_p if req_p else 0.0),
        max_heat_total=max_heat_d + max_heat_p,
        electric_heater_types=HEAT_ELEC[heater], fuel_power=fuel_power, tech={"C": tech_vc, "VC": tech_vc},
        hd_case_driver=P.heating_distribution_case(HDC, hp_driver, has_eh, fuel_power > 0),       # SI 194-198
        hd_case_passenger=P.heating_distribution_case(HDC, hp_pass, has_eh, fuel_power > 0))


def single(env_id):
    e = ENV[env_id]
    return P.Env(e.id, e.T, e.solar, 1.0, dict(e.cop), dict(e.heater_eff))          # test copies the env with weight 1.0 (test lines 405-409)


results = []


def check(name, src, got, exp):
    ok = abs(got - exp) <= TOL
    results.append(dict(test=name, src=src, expected=exp, port=round(got, 4), diff=round(got - exp, 6), result="PASS" if ok else "FAIL"))


# 1) heating demand, CFG1..: SSMTest_HeatingDemand_SingleEnvironment (SSMTestHeatingCooling.cs 322-331)
EXP_DEMAND = {1: 13475.4938, 2: 7261.9812, 3: 4395.4812, 4: 1973.9875, 5: 1494.6531, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}
for cfg in (1, 3):
    bus = make_bus(cfg, cooling=False)
    for eid, exp in EXP_DEMAND.items():
        r = P.calculate_heating_power(bus, single(eid), HDT, 0.0)
        check(f"HeatingDemand CFG{cfg} env{eid}", "SSMTestHeatingCooling.cs:322-331 (CFG1), 345-ff (CFG3)", r["required"], exp)

# 2) heating distribution CFG1: SSMTest_HeatingDistribution_SingleEnvironment_CFG1 (lines 426-445)
H = "None"
CFG1_CASES = [  # id, env, heater, auxP, exp_demand, exp_hp_el, exp_hp_mech, exp_eh, exp_aux
    ("1a", 1, "None", 0, 13475.4938, 0, 0, 0, 0), ("1b", 1, "Air", 0, 13475.4938, 0, 0, 14489.7782, 0),
    ("1c", 1, "Water", 0, 13475.4938, 0, 0, 14489.7782, 0), ("1d", 1, "Other+Air", 0, 13475.4938, 0, 0, 14489.7782, 0),
    ("1e", 1, "None", 30e3, 13475.4938, 0, 0, 0, 16844.3672), ("1f", 1, "Air", 30e3, 13475.4938, 0, 0, 2897.9556, 13475.4938),
    ("1g", 1, "Water", 30e3, 13475.4938, 0, 0, 2897.9556, 13475.4938), ("1h", 1, "Other+Air", 30e3, 13475.4938, 0, 0, 2897.9556, 13475.4938),
    ("2a", 2, "None", 0, 7261.9812, 0, 0, 0, 0), ("2b", 2, "Air", 0, 7261.9812, 0, 0, 7808.582, 0),
    ("2c", 2, "Water", 0, 7261.9812, 0, 0, 7808.582, 0), ("2d", 2, "Other+Air", 0, 7261.9812, 0, 0, 7808.582, 0),
    ("2e", 2, "None", 30e3, 7261.9812, 0, 0, 0, 9077.4766), ("2f", 2, "Air", 30e3, 7261.9812, 0, 0, 0, 9077.4766),
    ("2g", 2, "Water", 30e3, 7261.9812, 0, 0, 0, 9077.4766), ("2h", 2, "Other+Air", 30e3, 7261.9812, 0, 0, 0, 9077.4766)]
for cid, eid, htr, aux, d, hpe, hpm, eh, ax in CFG1_CASES:
    bus = make_bus(1, False, heater=htr, fuel_power=aux)
    r = P.calculate_heating_power(bus, single(eid), HDT, 0.0)
    src = "SSMTestHeatingCooling.cs:426-445"
    check(f"HD CFG1 {cid} demand", src, r["required"], d)
    check(f"HD CFG1 {cid} heater el", src, r["eh_el"], eh)
    check(f"HD CFG1 {cid} aux fuel in", src, r["aux"], ax)

# 3) heating distribution CFG2 (driver heat pump only): lines 480-514
HP = {"2St": "non R-744 2-stage", "Cont": "non R-744 continuous", "R744": "R-744"}
CFG2_CASES = [  # id, env, hp, heater, aux, exp_hp_el, exp_hp_mech, exp_eh, exp_aux
    ("2a", 2, "2St", "None", 0, 0, 471.5572, 0, 0), ("2b", 2, "2St", "Water", 0, 0, 471.5572, 7027.7238, 0),
    ("2c", 2, "2St", "None", 30e3, 0, 330.0901, 0, 8442.0532), ("2d", 2, "2St", "Air", 30e3, 0, 330.0901, 0, 8442.0532),
    ("2e", 2, "Cont", "None", 0, 407.9765, 0, 0, 0), ("2f", 2, "Cont", "Other", 0, 407.9765, 0, 7027.7238, 0),
    ("2g", 2, "Cont", "None", 30e3, 285.5835, 0, 0, 8442.0532), ("2h", 2, "Cont", "Water+Air", 30e3, 285.5835, 0, 0, 8442.0532),
    ("2i", 2, "R744", "None", 0, 355.9795, 0, 0, 0), ("2j", 2, "R744", "Water", 0, 355.9795, 0, 7027.7238, 0),
    ("2k", 2, "R744", "None", 30e3, 249.1856, 0, 0, 8442.0532), ("2l", 2, "R744", "Water", 30e3, 249.1856, 0, 0, 8442.0532),
    ("3a", 3, "2St", "None", 0, 0, 219.7741, 0, 0), ("3b", 3, "2St", "Water", 0, 0, 219.7741, 4253.6915, 0),
    ("3e", 3, "Cont", "None", 0, 197.9947, 0, 0, 0), ("3i", 3, "R744", "None", 0, 175.8192, 0, 0, 0),
    ("3k", 3, "R744", "None", 30e3, 140.6554, 0, 0, 5054.8034)]
for cid, eid, hp, htr, aux, hpe, hpm, eh, ax in CFG2_CASES:
    bus = make_bus(2, False, hp_driver=HP[hp], heater=htr, fuel_power=aux)
    r = P.calculate_heating_power(bus, single(eid), HDT, 0.0)
    src = "SSMTestHeatingCooling.cs:480-514"
    check(f"HD CFG2 {cid} HP el", src, r["hp_el"], hpe)
    check(f"HD CFG2 {cid} HP mech", src, r["hp_mech"], hpm)
    check(f"HD CFG2 {cid} heater el", src, r["eh_el"], eh)
    check(f"HD CFG2 {cid} aux fuel in", src, r["aux"], ax)

# 4) cooling / ventilation, single environment: SSMTest_Cooling_SingleEnvironment (CFG1 lines 54-57, CFG3 lines 61-64)
for cfg, exp in ((1, {1: 299.88, 6: 299.88, 8: 287.8848, 11: 287.8848}), (3, {1: 428.4, 6: 856.8, 8: 822.528, 11: 822.528})):
    bus = make_bus(cfg, True)
    for eid, e in exp.items():
        check(f"Cooling/vent CFG{cfg} env{eid} electric", "SSMTestHeatingCooling.cs:54-64", P.electrical_w_adjusted(bus, [single(eid)]), e)

# 5) cooling, weighted over all 11 conditions: SSMTest_Cooling_AvgAllEnvironments (lines 238-249 + 262-263)
AVG = [(1, "none", "none", 295.3949), (3, "none", "none", 664.4004),
       (2, "non R-744 continuous", "none", 395.9945), (2, "R-744", "none", 418.4411),
       (4, "non R-744 continuous", "none", 676.364), (4, "R-744", "none", 698.8106)]
for cfg, hd, hpp, exp in AVG:
    bus = make_bus(cfg, True, hp_driver=hd, hp_pass=hpp)
    check(f"Cooling weighted avg CFG{cfg} driver HP={hd}", "SSMTestHeatingCooling.cs:238-263", P.electrical_w_adjusted(bus, ENVS), exp)

out = os.path.join(HERE, "gate3_vecto_unit_tests.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(results[0])); w.writeheader(); w.writerows(results)
n_pass = sum(r["result"] == "PASS" for r in results)
print(f"VECTO unit-test replication: {n_pass}/{len(results)} PASS (tolerance {TOL})")
for r in results:
    if r["result"] != "PASS":
        print("  FAIL", r)
print("wrote", out)
