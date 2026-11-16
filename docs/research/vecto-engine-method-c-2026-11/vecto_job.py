"""Writes a declaration-mode VECTO job (.vecto + .vveh + IEPC + battery files) for one truck and one method-C parameter set,
runs vectocmd, and reads the terminal energy of every result from the .vsum.

Method C as VECTO inputs (all constructions by us, [ASSUMPTION], explained in the report):
  IEPC power map   P_el(n, T) = P_mech/eta_d + 0 for T > 0 ; P_el = P_mech * eta_r for T < 0 ; P_mech = T * omega.  Map axes are the IEPC OUTPUT
                   (wheel side, because the differential is part of the IEPC in both EEA configs): n_out [rpm], T_out [Nm], P_el [kW].
  F0               constant torque loss  T0 = F0 * r_dyn  [Nm at the wheel]. Two constructions:
                   f0_mode = "axle" : separate axle gear, ratio 1.0, whose loss map has a constant torque loss column (the way the
                                      prompt asks; TransmissionLossMap.cs 66-70, 90-100). IEPC then declared with DifferentialIncluded = false.
                   f0_mode = "iepc" : the same loss inside the IEPC map, P_el = (T + T0) * omega / eta_d  (sensitivity variant).
  full load curve  T_drive_out(n) = min(T_cap, P_rated / omega) ; T_recuperation_out = -(same). P_rated = EEA IEPC rated power.
  drag curve       0 Nm (the harness variant V-A has zero coasting drag).
  CdxA             CdA in the .vveh (declared value) ; VECTO uses the default on Construction and adds the trailer delta itself.
"""
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VECTOCMD = os.environ.get("VECTOCMD", os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "vectocmd", "vectocmd.dll")))
ENV = dict(os.environ, DOTNET_ROLL_FORWARD="Major", DOTNET_NOLOGO="1", DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="1",
           HOME=os.environ.get("HOME", "/tmp"))
T_CAP = {"C0091": 60000.0, "C0059": 12000.0}      # Nm at the wheel; see report: chosen so the driver's acceleration limit binds first
SPEED_MAX_RPM = 1400.0
IEPC_VOLTAGES = (100.0, 2000.0)


def _w(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def _hdr(fv):
    return {"CreatedBy": "", "Date": "2026-11-16T00:00:00Z", "AppVersion": "3", "FileVersion": fv}


N_RPM = np.array([0, 3.37, 33.7, 50.6, 67.4, 84.3, 101, 118, 135, 152, 168, 185, 202, 219, 236, 253, 270, 303, 337, 404, 505, 674, 1000, 1400.])
N_TORQUE = 45


def power_map(P_rated_W, eta_d, eta_r, T0, T_cap):
    """Grid of (n_out rpm, T_out Nm, P_el kW). The speed grid follows the VECTO generic IEPC maps (first speeds 0, 3.37, 33.7 rpm: the reader finds the
    zero-rpm entries by clustering the two lowest speeds, IEPCMapReader.cs 144-190, and fails on duplicates when they are closer). P_el is the product
    T*omega divided by eta; a Delaunay linear interpolation reproduces that only approximately between grid points. The offline test on the harness
    wheel-power rows of both trucks (p1_grid_test.csv) gives an energy error of at most 0.14 % for this grid."""
    n_rad = N_RPM * math.pi / 30.0
    g = np.geomspace(30.0, T_cap, N_TORQUE)
    T = np.unique(np.concatenate([-g, g, [0.0, -10.0, 10.0]]))
    rows = []
    for w, n in zip(n_rad, N_RPM):
        for t in T:
            tt = t + T0                                # wheel torque including the constant loss torque [Nm]
            pel = (tt * w) / eta_d if tt > 0 else (tt * w) * eta_r
            rows.append((n, t, pel / 1000.0))
    return rows


def fld(P_rated_W, T_cap):
    n_rad = np.concatenate([[0.0], np.geomspace(P_rated_W / T_cap * 0.5, 150.0, 40)])
    n_corner = P_rated_W / T_cap
    n_rad = np.unique(np.concatenate([n_rad, [n_corner], np.arange(1.0, 150.0, 5.0)]))
    out = []
    for w in n_rad:
        t = T_cap if w <= n_corner else P_rated_W / w
        out.append((w * 30.0 / math.pi, t, -t))
    return out


def write_job(d, tr, eta_d, eta_r, F0, cdxa, f0_mode="axle", T_cap=None):
    os.makedirs(d, exist_ok=True)
    T_cap = T_cap or T_CAP[tr["config_id"]]
    P = tr["rated_kw"] * 1000.0
    r_dyn = tr["axles"][1]["r_dyn"]                 # driven axle = axle 2 (as harness, driven_axle_number 2)
    T0 = F0 * r_dyn
    diff_in_iepc = (f0_mode == "iepc")
    # --- IEPC files
    pm = power_map(P, eta_d, eta_r, T0 if f0_mode == "iepc" else 0.0, T_cap)
    _w(os.path.join(d, "iepc.viepco"), "n_out, T_out, P_el\n" + "\n".join("%.4f, %.3f, %.5f" % r for r in pm) + "\n")
    fl = fld(P, T_cap)
    _w(os.path.join(d, "fld.viepcp"), "n_out, T_drive_out, T_recuperation_out\n" + "\n".join("%.4f, %.3f, %.3f" % r for r in fl) + "\n")
    _w(os.path.join(d, "drag.viepcd"), "n_out, T_drag_out\n0.00, 0.0\n%.2f, 0.0\n" % SPEED_MAX_RPM)
    n_corner_rpm = P / T_cap * 30.0 / math.pi
    lev = []
    for v in IEPC_VOLTAGES:
        lev.append({"Voltage": v, "ContinuousTorque": T_cap, "ContinuousTorqueSpeed": round(n_corner_rpm, 4), "OverloadTorque": T_cap,
                    "OverloadTorqueSpeed": round(n_corner_rpm, 4), "OverloadTime": 300.0, "FullLoadCurve": "fld.viepcp", "PowerMaps": {"1": "iepc.viepco"}})
    ratio = tr["total_ratio"]
    iepc = {"Header": _hdr(1), "Body": {"SavedInDeclMode": True, "Model": "Method C construction", "ElectricMachineType": "PSM", "Inertia": 0.0,
                                        "DifferentialIncluded": True if f0_mode != "axle" else False, "DesignTypeWheelMotor": False,
                                        "NrOfDesignTypeWheelMotorMeasured": 1, "ThermalOverloadRecoveryFactor": 0.0,
                                        "R85RatedPower": tr["rated_kw"], "Gears": [{"Ratio": ratio}], "VoltageLevels": lev,
                                        "DragCurves": {"1": "drag.viepcd"}}}
    _w(os.path.join(d, "iepc.viepc"), json.dumps(iepc, indent=1))
    # --- axle gear for the F0 construction
    if f0_mode == "axle":
        sp = [0.0, 100.0, 500.0, 1500.0]
        tq = [-100000.0, -20000.0, -2000.0, 0.0, 2000.0, 20000.0, 100000.0]
        _w(os.path.join(d, "axle.vtlm"), "Input Speed [rpm],Input Torque [Nm],Torque Loss [Nm]\n" + "\n".join("%g,%g,%.4f" % (n, t, T0) for n in sp for t in tq) + "\n")
        _w(os.path.join(d, "axle.vgbx"), json.dumps({"Header": _hdr(6), "Body": {
            "SavedInDeclMode": True, "ModelName": "constant loss axle", "Inertia": 0.0, "TracInt": 1.0,
            "Gears": [{"Ratio": 1.0, "LossMap": "axle.vtlm"}], "TqReserve": 0.0, "ShiftTime": 2.0, "StartTqReserve": 20.0, "StartSpeed": 2.222222222222,
            "StartAcc": 0.8, "GearboxType": "IEPC", "TorqueConverter": {"Enabled": False}, "DownshiftAfterUpshiftDelay": 6.0,
            "UpshiftAfterDownshiftDelay": 6.0, "UpshiftMinAcceleration": 0.1, "PowershiftShiftTime": 0.0}}, indent=1))
    # --- battery (terminal energy does not depend on it; sized to the EEA installed energy)
    cap_ah = tr["bat_kwh"] * 1000.0 / 750.0
    _w(os.path.join(d, "bat.vbat"), json.dumps({"Header": _hdr(1), "Body": {
        "SavedInDeclMode": True, "REESSType": "Battery", "Model": "Generic Battery scaled to EEA installed kWh", "Capacity": round(cap_ah, 3), "SOC_min": 10.0, "SOC_max": 90.0,
        "MaxCurrentMap": "bat.vimax", "InternalResistanceCurve": "bat.vbatr", "SoCCurve": "bat.vbatv", "TestingTemperature": 40.0,
        "JunctionboxIncluded": False, "ConnectorsSubsystemsIncluded": True}}, indent=1))
    src = os.path.join(os.environ.get("VECTO_SRC", os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "VECTO"))),
                       "Generic Vehicles", "Declaration Mode", "PEV", "GenericIEPC", "Common")
    for a, b in (("GenericBattery_243kWh.vbatr", "bat.vbatr"), ("GenericBattery_243kWh.vbatv", "bat.vbatv")):
        shutil.copy(os.path.join(src, a), os.path.join(d, b))
    _w(os.path.join(d, "bat.vimax"), "SOC, I_charge, I_discharge\n0, 10000, 10000\n100, 10000, 10000\n")
    # --- vehicle
    axles = []
    for i, a in enumerate(tr["axles"]):
        axles.append({"Inertia": a["inertia_per_tyre"], "Wheels": a["dim"], "AxleWeightShare": 0.0, "TwinTyres": a["twin"], "RRCISO": a["rrc"],
                      "FzISO": tr["fziso_N"], "Type": "VehicleDriven" if i == 1 else "VehicleNonDriven"})
    veh = {"Header": _hdr(11), "Body": {
        "SavedInDeclMode": True, "VehCat": "Tractor" if tr["group"] == "5" else "RigidTruck", "LegislativeClass": tr["category"],
        "CurbWeight": tr["curb_mass_kg"], "CurbWeightExtra": 0.0, "MassMax": tr["tpmlm_t"], "Loading": 0.0, "rdyn": 0.0,
        "CdCorrMode": "CdofVdecl", "CdCorrFile": "", "AxleConfig": {"Type": tr["axle_config"], "Axles": axles},
        "EngineStopStart": False, "EcoRoll": "None", "PredictiveCruiseControl": "None", "ATEcoRollReleaseLockupClutch": False,
        "CdA": cdxa, "VehicleHeight": 4.0 if tr["group"] == "5" else 3.6, "InitialSoC": 80.0, "PowertrainConfiguration": "IEPC_E", "IEPC": "iepc.viepc",
        "Batteries": [{"NumPacks": 1, "BatteryFile": "bat.vbat", "StreamId": 0}],
        "PTO": {"Type": "None", "LossMap": "", "Cycle": "", "CycleEPTO": "", "CycleDriving": ""}}}
    _w(os.path.join(d, "veh.vveh"), json.dumps(veh, indent=1))
    job = {"Header": _hdr(12), "Body": {"SavedInDeclMode": True, "VehicleFile": "veh.vveh", "Padd_electric": 0.0, "Aux": [
        {"ID": "STP", "Type": "Steering pump", "Technology": ["Full electric steering gear"]},
        {"ID": "AC", "Type": "HVAC", "Technology": ["Default"]},
        {"ID": "ES", "Type": "Electric System", "Technology": ["Standard technology"]},
        {"ID": "PS", "Type": "Pneumatic System", "Technology": [tr["pneu"]]}]}}
    if f0_mode == "axle":
        job["Body"]["GearboxFile"] = "axle.vgbx"
    _w(os.path.join(d, "job.vecto"), json.dumps(job, indent=1))
    return os.path.join(d, "job.vecto")


def run(job, mod=False, timeout=900):
    d = os.path.dirname(job)
    for f in os.listdir(d):
        if f.endswith((".vsum", ".vmod")) or f.startswith("job.RSLT"):
            os.remove(os.path.join(d, f))
    cmd = ["dotnet", VECTOCMD, "-t"] + (["-mod"] if mod else []) + [os.path.basename(job)]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=d, env=ENV, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr, time.time() - t0


def read_vsum(d):
    """Returns list of dict(cycle, loading, mass, distance, term kWh/km, final kWh/km, status)."""
    path = os.path.join(d, "job.vsum")
    if not os.path.exists(path):
        return []
    rows = [r for r in csv.reader(open(path, encoding="utf-8-sig")) if len(r) > 5]
    h = rows[0]; ix = {n: i for i, n in enumerate(h)}
    out = []
    for row in rows[2:] if rows[1][0].startswith("[") else rows[1:]:
        if row[ix["Status"]] != "Success":
            out.append(dict(cycle=row[ix["Cycle [-]"]], status=row[ix["Status"]]))
            continue
        km = float(row[ix["distance [km]"]])
        out.append(dict(cycle=row[ix["Cycle [-]"]].replace(".vdri", ""), loading=float(row[ix["Loading [kg]"]]), mass=float(row[ix["Total vehicle mass [kg]"]]),
                        distance_km=km, cdxa=float(row[ix["CdxA [m²]"]]), declared_cdxa=float(row[ix["Declared CdxA [m²]"]]),
                        term_kwh_km=(float(row[ix["E_REESS_T_dischg [kWh]"]]) - float(row[ix["E_REESS_T_chg [kWh]"]])) / km,
                        final_kwh_km=float(row[ix["EC_el_final [kWh/km]"]]), status="Success"))
    return out


if __name__ == "__main__":
    import truck_inputs as TI
    cid = sys.argv[1]
    tr = TI.vehicle_inputs(cid)
    d = os.path.join(HERE, "work", "probe_" + cid + "_" + (sys.argv[2] if len(sys.argv) > 2 else "axle"))
    job = write_job(d, tr, 0.95, 0.90, 300.0, 0.5 * (5.38 + 5.65) if cid == "C0091" else 7.1, f0_mode=(sys.argv[2] if len(sys.argv) > 2 else "axle"))
    rc, out, dt = run(job)
    print(rc, "%.1f s" % dt)
    print(out[-3000:])
    for r in read_vsum(d):
        print(r)
