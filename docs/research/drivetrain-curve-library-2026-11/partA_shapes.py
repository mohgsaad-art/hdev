"""PART A -- build efficiency shapes (efficiency vs load fraction) from VECTO's own maps.

How (KIT method, but every point traces to a VECTO file):
  1. Drive the VECTO generic truck (GenericVehicleE2 body: 6570 kg + loading) over the VECTO declaration cycles
     (Regional, Urban, LongHaul, Construction, Municipal) with Bob's notebook driver_model + force_engine
     (v2 hdev_test_module), exactly as the v2 gate does.
  2. Push each 1 s wheel-power row through `drivetrain` (Appendix A, verbatim) with VECTO maps for each chain:
       S1  VECTO generic E2 (2 x 125 kW ASM map, ADC 2.0, 2-speed AMT maps, axle map)
       S2  VECTO bus-generic IEPC normalised map (PSM and ASM) de-normalised on the GenericIEPC 1-speed full-load
           curve the VECTO way (GenericBusIEPCData.cs), behind the generic axle map
       S3a VECTO GenericIEPC 1-speed example map (+ axle map)
       S3b VECTO GenericIEPC 3-speed example maps (+ axle map)
       S3c VECTO GenericIEPC wheel-motor 1-speed example (2 wheel units, no axle)
       S4  EU standard-value ASM motor (Annex Xb App. 8, v2 run_hdev._build_std_emap) on the E2 motor rated point,
           + standard gearbox (Annex VI App. 8, 3 Nov _stdval.std_gearbox) + VECTO generic axle (_stdval.std_axle_vecto)
     Gear rule: highest gear the motor can manage (Appendix A note).
     Map coordinates: VECTO's loss maps are triangulated on (input speed, input torque - loss)
     (TransmissionLossMap.cs 76-77); Part A4. The shapes use VECTO's coordinates.
  3. x = |P_wheel| / P_rated; bin; energy-weighted efficiency per bin, separately for driving and recovering;
     per-part loss shares; P10/P90 of the row efficiencies (scatter).

Outputs (printed at the end): partA_shapes.csv, partA_shape_summary.csv, partA_rows_<shape>.csv.gz (per-row
records), partA_*.png.
"""
import csv
import gzip
import os
import sys

import numpy as np

import shapes_lib as SL
import reference_copy as R
import harness as HN

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(R.REPO, "docs", "research", "drivetrain-inputs-fallbacks-2026-11"))
import _stdval as STD      # noqa: E402  (3 Nov standard-value builders, not edited)

CYCLES = ("Regional", "Urban", "LongHaul", "Construction", "Municipal")
LOADS = ("reference", "low")


def _loss_obj_to_table(lobj):
    """_stdval._Loss keeps LinearNDInterpolator on (n_in rpm, T_in - loss) -> loss: these are already VECTO
    coordinates; convert rpm to rad/s for `drivetrain`."""
    pts = np.asarray(lobj.lin.points, float)
    val = np.asarray(lobj.lin.values, float).ravel()
    return np.c_[pts[:, 0] / R.RPM, pts[:, 1], val]


def s4_chain():
    """S4: standard-value motor + standard gearbox + VECTO generic axle on the E2 layout."""
    (w, Td), (wg, Tg) = R.read_vemp(os.path.join(R.E2_DIR, "GenericEMotor_125kW_485Nm.vemp"))
    n_r, t_r, _ = SL.rated_point_vecto(w * R.RPM, Td)                 # rad/s, Nm (VECTO rated-speed rule)
    emap = HN.RH._build_std_emap(t_r, n_r * R.RPM)                    # v2 harness: Annex Xb App.8 ASM, linear
    pts = np.asarray(emap.lin.points, float)
    tab = np.c_[pts[:, 0] / R.RPM, pts[:, 1], np.asarray(emap.lin.values, float).ravel()]
    ch = SL.ChainE2(em_map=tab, eta_adc=1.0, name="S4_std_ASM")
    tmax_in = 2 * 485.0 * 2.0          # 3 Nov [ASSUMP]: N_EM * T_EM_MAX * I_ADC (no published source)
    ch.e2["gear_maps"] = [_loss_obj_to_table(STD.std_gearbox(r, tmax_in)[0]) for r in ch.e2["i_gears"]]
    ch.e2["axle_map"] = _loss_obj_to_table(STD.std_axle_vecto(ch.e2["i_axle"])[0])
    return ch


def all_chains():
    return [
        SL.ChainE2(name="S1_E2"),
        SL.iepc_bus_chain("IEPC_Gbx1Speed", "S2_busIEPC_PSM", "IEPC_Gbx1_FLD_max.viepcp", [4.65], "PSM"),
        SL.iepc_bus_chain("IEPC_Gbx1Speed", "S2_busIEPC_ASM", "IEPC_Gbx1_FLD_max.viepcp", [4.65], "ASM"),
        SL.iepc_gbx1(),
        SL.iepc_gbx3(),
        SL.ChainIEPCWheel(),
        s4_chain(),
    ]


def build(write=True):
    vehicle_rows = {(c, l): SL.e2_vehicle_rows(c, l) for c in CYCLES for l in LOADS}
    shape_rows, summary = [], []
    shapes = {}
    for ch in all_chains():
        tables = []
        for (c, l), rows in vehicle_rows.items():
            t = SL.chain_rows_table(ch, rows)
            t["cycle"], t["load"] = c, l
            tables.append(t)
            d, g = t["drive"], t["regen"]
            ev = t["ev"]
            summary.append(dict(
                shape=ch.name, cycle=c, load=l, P_rated_kW=round(ch.P_rated_W / 1e3, 2),
                wheel_drive_kwh_km=round(t["P_wheel"][d].sum() / 3.6e6 / rows["km"], 5),
                wheel_regen_kwh_km=round(t["P_wheel"][g].sum() / 3.6e6 / rows["km"], 5),
                el_kwh_km=round(t["P_el"].sum() / 3.6e6 / rows["km"], 5),
                eta_drive=round(t["P_wheel"][d].sum() / t["P_el"][d].sum(), 5),
                eta_regen=round(t["P_el"][g].sum() / t["P_wheel"][g].sum(), 5),
                share_axle_loss=round(ev["P_axle_loss"].sum() / max(1e-9, (ev["P_axle_loss"] + ev["P_gbx_loss"] + ev["P_adc_loss"] + ev["P_em_loss"]).sum()), 4),
                share_gearbox_loss=round(ev["P_gbx_loss"].sum() / max(1e-9, (ev["P_axle_loss"] + ev["P_gbx_loss"] + ev["P_adc_loss"] + ev["P_em_loss"]).sum()), 4),
                share_motor_loss=round(ev["P_em_loss"].sum() / max(1e-9, (ev["P_axle_loss"] + ev["P_gbx_loss"] + ev["P_adc_loss"] + ev["P_em_loss"]).sum()), 4),
                rows_extrapolated=int(ev["extrapolated"].sum()), rows_over_limit=int(ev["over_limit"].sum()),
                rows_no_gear_ok=int(ev["no_gear_ok"].sum()),
                brake_overflow_kwh_km=round(-ev["P_to_brakes"].sum() / 3.6e6 / rows["km"], 5)))
        b = SL.bin_shape(tables)
        for r in b:
            r["shape"] = ch.name
        shape_rows += b
        shapes[ch.name] = dict(bins=b, P_rated_W=ch.P_rated_W, tables=tables)
        if False and write:   # per-row dumps disabled (size)
            with gzip.open(os.path.join(HERE, "partA_rows_%s.csv.gz" % ch.name), "wt", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["cycle", "load", "row", "x", "side", "P_wheel_W", "P_el_W", "gear", "P_axle_loss_W", "P_gbx_loss_W", "P_em_loss_W"])
                for t in tables:
                    for i in np.where(t["drive"] | t["regen"])[0]:
                        w.writerow([t["cycle"], t["load"], i, "%.6f" % t["x"][i], "drive" if t["drive"][i] else "regen",
                                    "%.2f" % t["P_wheel"][i], "%.2f" % t["P_el"][i], int(t["ev"]["gear"][i]),
                                    "%.2f" % t["ev"]["P_axle_loss"][i], "%.2f" % t["ev"]["P_gbx_loss"][i], "%.2f" % t["ev"]["P_em_loss"][i]])
    return shape_rows, summary, shapes


def no_load_loss(shapes):
    """Electric power needed with zero wheel power at every cycle speed / P_rated (drivetrain spinning only).
    Used as the sourced upper bound of L3's constant loss term."""
    out = {}
    for ch in all_chains():
        vals = []
        for c in CYCLES:
            rows = SL.e2_vehicle_rows(c, "reference")
            r0 = dict(rows)
            r0["P_wheel"] = np.where(rows["use"], 1e-3, 0.0)       # ~zero torque, gear in, wheels turning
            ev = ch.evaluate(r0)
            moving = rows["use"] & (rows["v_avg"] > 0.5)
            vals.append(ev["P_el"][moving] / ch.P_rated_W)
        v = np.concatenate(vals)
        out[ch.name] = dict(mean=float(np.mean(v)), p90=float(np.percentile(v, 90)), max=float(np.max(v)))
    return out


FASTSIM_BOLT = dict(   # [SOURCE] mohgsaad-art/fastsim branch fastsim-3, fastsim-core/resources/vehicles/
    # "2020 Chevrolet Bolt EV thrml.yaml" lines 113-145 (em.eff_interp_achieved). Passenger car. PLOT ONLY.
    x=[0.0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
    eta=[0.8736113907685258, 0.894336709838892, 0.9150620289092581, 0.9357873479796243, 0.9461500075148074,
         0.9565126670499905, 0.9772379861203567, 0.9876006456555396, 0.9876006456555396, 0.9772379861203567,
         0.9668753265851735])


def plots(shape_rows, shapes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    files = []
    for side in ("drive", "regen"):
        fig, ax = plt.subplots(1, 2, figsize=(13, 5))
        for name in shapes:
            b = sorted([r for r in shape_rows if r["shape"] == name and r["side"] == side], key=lambda r: r["x_mid"])
            x = [r["x_mid"] for r in b]; e = [r["eta"] for r in b]
            ax[0].plot(x, e, "-o", ms=3, label=name)
            ax[0].fill_between(x, [r["eta_p10"] for r in b], [r["eta_p90"] for r in b], alpha=0.08)
            ax[1].plot(x, np.array(e) / max(e), "-o", ms=3, label=name)
        if side == "drive":
            ax[0].plot(FASTSIM_BOLT["x"], FASTSIM_BOLT["eta"], "k--", label="FASTSim Bolt EV motor only (plot only)")
            ax[1].plot(FASTSIM_BOLT["x"], np.array(FASTSIM_BOLT["eta"]) / max(FASTSIM_BOLT["eta"]), "k--", label="FASTSim (plot only)")
        ax[0].set_title("Chain efficiency, %s (bands = P10-P90 of 1 s rows)" % side)
        ax[1].set_title("Normalised by own peak (A5)")
        for a in ax:
            a.set_xscale("log"); a.set_xlabel("load fraction x = |P_wheel| / P_rated"); a.grid(alpha=0.3)
        ax[0].set_ylabel("efficiency"); ax[0].set_ylim(0, 1.0); ax[1].set_ylim(0, 1.05)
        ax[1].legend(fontsize=7)
        fig.tight_layout()
        f = os.path.join(HERE, "partA_shapes_%s.png" % side)
        fig.savefig(f, dpi=110); plt.close(fig); files.append(f)
    # per-part losses for S1 and S3b
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    for a, name in zip(ax, ("S1_E2", "S3b_IEPC_3speed", "S4_std_ASM")):
        b = sorted([r for r in shape_rows if r["shape"] == name and r["side"] == "drive"], key=lambda r: r["x_mid"])
        x = [r["x_mid"] for r in b]
        a.stackplot(x, [r["loss_axle"] for r in b], [r["loss_gearbox"] for r in b], [r["loss_adc"] for r in b],
                    [r["loss_motor"] for r in b], labels=["axle", "gearbox", "ADC", "motor+inverter (map)"])
        a.set_xscale("log"); a.set_ylim(0, 2); a.set_title("%s: loss per kWh at the wheel (driving)" % name)
        a.set_xlabel("x"); a.grid(alpha=0.3)
    ax[0].legend(fontsize=7)
    fig.tight_layout()
    f = os.path.join(HERE, "partA_losses_by_part.png")
    fig.savefig(f, dpi=110); plt.close(fig); files.append(f)
    return files


def main():
    shape_rows, summary, shapes = build()
    nl = no_load_loss(shapes)
    cols = ["shape", "side", "x_lo", "x_hi", "x_mid", "eta", "eta_p10", "eta_p90", "n_rows", "wheel_kwh",
            "loss_axle", "loss_gearbox", "loss_adc", "loss_motor", "brake_overflow"]
    f1 = os.path.join(HERE, "partA_shapes.csv")
    with open(f1, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in shape_rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k in cols})
    f2 = os.path.join(HERE, "partA_shape_summary.csv")
    with open(f2, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0].keys()))
        w.writeheader(); w.writerows(summary)
    f3 = os.path.join(HERE, "partA_no_load_loss.csv")
    with open(f3, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["shape", "no_load_P_el_over_P_rated_mean", "p90", "max"])
        for k, v in nl.items():
            w.writerow([k, round(v["mean"], 6), round(v["p90"], 6), round(v["max"], 6)])
    files = plots(shape_rows, shapes)
    for f in [f1, f2, f3] + files + [os.path.join(HERE, "partA_rows_%s.csv.gz" % n) for n in shapes]:
        print("wrote", f)


if __name__ == "__main__":
    main()
