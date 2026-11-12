"""Gate 3 + Part C: row-level reproduction of VECTO wheel power with Bob's force_engine.

Feeds VECTO's own speed trace (from each .vmod) into the UNCHANGED notebook force_engine and the
P_wheel equation (consumption_engine step 4), and compares each term with VECTO's column.

Run:  python run_part_c.py            (deterministic; writes CSVs next to this file)
"""
from _common import *

TERMS = ["P_roll", "P_air", "P_slope", "P_veh_inertia", "P_wheel_inertia"]
SMALL_W = 100.0          # 0.1 kW  (prompt: explain rows larger than 1 % of the term or 0.1 kW)
REL = 0.01


def pct(a, b):
    return (a / b - 1) * 100 if abs(b) > 1e-9 else float("nan")


def term_stats(name, hdev, vecto, dt, flagged_extra=None):
    e_h, e_v = energy_kwh(hdev, dt), energy_kwh(vecto, dt)
    d = np.asarray(hdev) - np.asarray(vecto)
    i = int(np.argmax(np.abs(d)))
    flagged = (np.abs(d) > SMALL_W) & (np.abs(d) > REL * np.abs(vecto))
    return dict(term=name,
                vecto_net=e_v["net"], vecto_pos=e_v["pos"], vecto_neg=e_v["neg"],
                hdev_net=e_h["net"], hdev_pos=e_h["pos"], hdev_neg=e_h["neg"],
                d_net_kwh=e_h["net"] - e_v["net"], d_net_pct=pct(e_h["net"], e_v["net"]),
                d_pos_kwh=e_h["pos"] - e_v["pos"], d_pos_pct=pct(e_h["pos"], e_v["pos"]),
                d_neg_kwh=e_h["neg"] - e_v["neg"], d_neg_pct=pct(e_h["neg"], e_v["neg"]),
                rms_W=float(np.sqrt(np.mean(d ** 2))), max_abs_W=float(abs(d[i])), max_at_t=float(i + 1),
                n_rows=int(len(d)), n_flagged=int(flagged.sum()))


def main():
    gate_rows, term_rows, cause_rows, cls_rows, split_rows = [], [], [], [], []
    for key in LOADING:
        cyc, load = key
        veh = Vehicle(cyc, load)
        cols = load_vmod_run(cyc, load)
        r = vmod_rows(cols)
        vt = vecto_terms(cols)
        dt = r["dt"]
        tab = veh.cdxa_table()

        # ---------------- Gate 3
        res1 = vt["P_trac"] - (vt["P_roll"] + vt["P_air"] + vt["P_slope"] + vt["P_veh_inertia"])
        res2 = vt["P_wheel_in"] - (vt["P_trac"] + vt["P_wheel_inertia"])
        gate_rows.append(dict(cycle=cyc, load=load, n_rows=len(dt),
                              max_abs_W_trac_identity=float(np.abs(res1).max()), rms_W_trac_identity=float(np.sqrt(np.mean(res1 ** 2))),
                              max_abs_W_wheel_identity=float(np.abs(res2).max()), rms_W_wheel_identity=float(np.sqrt(np.mean(res2 ** 2))),
                              rounding_of_vmod_W=0.1,
                              identity="P_trac = P_roll+P_air+P_slope+P_veh_inertia ; P_wheel_in = P_trac + P_wheel_inertia"))

        # ---------------- baseline: acc-based reconstruction, atan, CdxA from Bob's table at v_avg
        vs, ac = trace_for_engine(r, "acc")
        base = hdev_terms(veh, vs, ac, dt, r["grad"], tab=tab)
        base_v = hdev_terms(veh, vs, ac, dt, r["grad"], cdxa_row=vt["cdxa"])
        moving = base["v_avg"] > 0.05
        cd_rms_tab = float(np.sqrt(np.mean((base["cdxa"][moving] - vt["cdxa"][moving]) ** 2)))
        cd_max_tab = float(np.max(np.abs(base["cdxa"][moving] - vt["cdxa"][moving])))
        cd_rel_tab = float(np.max(np.abs(base["cdxa"][moving] / vt["cdxa"][moving] - 1)) * 100)

        for variant, H in (("i_table", base), ("ii_vecto_cdxa", base_v)):
            for t in TERMS:
                s = term_stats(t, H[t], vt[t], dt)
                s.update(cycle=cyc, load=load, variant=variant, cdxa_rms_moving=cd_rms_tab if variant == "i_table" else 0.0,
                         cdxa_max_moving=cd_max_tab if variant == "i_table" else 0.0)
                term_rows.append(s)
            # P_trac and P_wheel (sum)
            s = term_stats("P_trac(sum)", H["P_trac"], vt["P_trac"], dt)
            s.update(cycle=cyc, load=load, variant=variant, cdxa_rms_moving=cd_rms_tab if variant == "i_table" else 0.0, cdxa_max_moving=0.0)
            term_rows.append(s)
            s = term_stats("P_wheel_in(sum)", H["P_wheel"], vt["P_wheel_in"], dt)
            s.update(cycle=cyc, load=load, variant=variant, cdxa_rms_moving=0.0, cdxa_max_moving=0.0)
            term_rows.append(s)

        # ---------------- classify flagged rows (what explains each large row difference)
        # distance (in rows = seconds) to the nearest standing row: the 1 Hz speed columns are rebuilt by ModalData1HzFilter and
        # disagree with the exact time-averaged P_* columns in the seconds around a stop (Q8 [OPEN]); the effect reaches ~3 s.
        stand = np.flatnonzero(base["v_avg"] < 0.05)
        idx = np.arange(len(dt))
        pos = np.searchsorted(stand, idx)
        d_left = np.where(pos > 0, idx - stand[np.clip(pos - 1, 0, len(stand) - 1)], 10 ** 6)
        d_right = np.where(pos < len(stand), stand[np.clip(pos, 0, len(stand) - 1)] - idx, 10 ** 6)
        near_stop = np.minimum(d_left, d_right) <= 3
        a_prev = np.r_[ac[0], ac[:-1]]
        a_next = np.r_[ac[1:], ac[-1]]
        a_jump = (np.abs(ac - a_prev) > 0.2) | (np.abs(ac - a_next) > 0.2)
        g_prev = np.r_[r["grad"][0], r["grad"][:-1]]
        g_next = np.r_[r["grad"][1:], r["grad"][-1]]
        g_jump = (np.abs(r["grad"] - g_prev) > 0.2) | (np.abs(r["grad"] - g_next) > 0.2)      # grade (%) changes at a waypoint inside the second
        for t in TERMS:
            d = base[t] - vt[t]
            fl = (np.abs(d) > SMALL_W) & (np.abs(d) > REL * np.abs(vt[t]))
            cls = np.where(near_stop, "A_within_3s_of_standstill", np.where(a_jump, "B_accel_changes_in_second", np.where(g_jump, "G_grade_changes_in_second", "C_other")))
            for c in ("A_within_3s_of_standstill", "B_accel_changes_in_second", "G_grade_changes_in_second", "C_other"):
                m = fl & (cls == c)
                cls_rows.append(dict(cycle=cyc, load=load, term=t, cause_class=c, n_flagged=int(m.sum()),
                                     sum_abs_diff_kWh=float(np.abs(d[m]).sum() * 1 / 3.6e6) if m.any() else 0.0,
                                     max_abs_W=float(np.abs(d[m]).max()) if m.any() else 0.0,
                                     share_of_all_flagged_abs_pct=float(np.abs(d[m]).sum() / max(np.abs(d[fl]).sum(), 1e-9) * 100) if fl.any() else 0.0))

        # ---------------- isolate causes one at a time (effect on each term's energy, net / positive part)
        def variant(name, H, note=""):
            for t in TERMS + ["P_wheel_in(sum)"]:
                hv = H["P_wheel"] if t == "P_wheel_in(sum)" else H[t]
                vv = vt["P_wheel_in"] if t == "P_wheel_in(sum)" else vt[t]
                s = term_stats(t, hv, vv, dt)
                cause_rows.append(dict(cycle=cyc, load=load, variant=name, note=note, term=t,
                                       vecto_pos=s["vecto_pos"], hdev_pos=s["hdev_pos"], d_pos_pct=s["d_pos_pct"], d_pos_kwh=s["d_pos_kwh"],
                                       vecto_net=s["vecto_net"], hdev_net=s["hdev_net"], d_net_pct=s["d_net_pct"], d_net_kwh=s["d_net_kwh"],
                                       rms_W=s["rms_W"], max_abs_W=s["max_abs_W"]))

        variant("0 baseline", base, "acc-based v1/v2, atan, CdxA(v_avg) from Bob's table")
        # (a) v1/v2 reconstruction
        vs2, ac2 = trace_for_engine(r, "chain")
        variant("a1 chain reconstruction", hdev_terms(veh, vs2, ac2, dt, r["grad"], tab=tab), "v2=2*v_act-v1, v1[k+1]=v2[k]")
        vs3, ac3 = trace_for_engine(r, "naive")
        variant("a2 v_act read as START speed (naive)", hdev_terms(veh, vs3, ac3, dt, r["grad"], tab=tab), "force_engine gets v_act as speed-at-start: WRONG per Q7")
        # (a3) v_avg from distance moved in the row instead of (v1+v2)/2  (roll term only is linear in v_avg)
        ds_row = np.diff(r["dist"], prepend=0.0)
        Hd = dict(base)
        Hd["P_roll"] = veh.mass ** BETA * veh.crr_eff() * G * np.cos(np.arctan(r["grad"] / 100)) * ds_row / dt
        Hd["P_wheel"] = base["P_wheel"] - base["P_roll"] + Hd["P_roll"]
        variant("a3 roll with v = dist/dt", Hd, "only P_roll changed: speed = distance moved in the row (file dist column)")
        # (b) grade conversion
        variant("b1 grade asin", hdev_terms(veh, vs, ac, dt, r["grad"], tab=tab, grade_mode="asin"), "sin(theta)=G (ratio treated as sine)")
        variant("b2 grade none (sin=G, cos=1)", hdev_terms(veh, vs, ac, dt, r["grad"], tab=tab, grade_mode="none"), "slope uses the ratio directly, cos=1")
        # (c) CdxA lookup speed
        variant("c1 CdxA at START speed", hdev_terms(veh, vs, ac, dt, r["grad"], tab=tab, cdxa_speed="start"))
        variant("c2 CdxA at END speed", hdev_terms(veh, vs, ac, dt, r["grad"], tab=tab, cdxa_speed="end"))
        variant("c3 VECTO's own CdxA_eff column", base_v, "isolates lookup/crosswind table from L")
        # (d) mass in the slope term: with reduced wheel mass
        Hs = dict(base)
        Hs["P_slope"] = (veh.mass + veh.m_red_wheels) * G * np.sin(np.arctan(r["grad"] / 100)) * base["v_avg"]
        Hs["P_wheel"] = base["P_wheel"] - base["P_slope"] + Hs["P_slope"]
        variant("d slope mass incl. reduced wheel mass", Hs, "NOT what VECTO does (Vehicle.cs:232-237 uses TotalVehicleMass)")
        # (e) motor rotor inertia added as extra reduced mass (gear 2 fixed in E2 runs; ratio from .vmod)
        J_rot = 0.225 * 2             # [VECTO] GenericEMotor_125kW_485Nm.vem Inertia 0.225 x 2 motors (EngineeringDataAdapter.cs:1011)
        gear_ratio = {0: 1.93, 1: 3.86, 2: 1.93}    # [VECTO] AMT.vgbx / Gear_1.vtlm 3.86, Gear_2.vtlm 1.93 (gear 0 = standing: a=0, value irrelevant)
        gear = VM.col(cols, "Gear").astype(int)
        i_row = 2.0 * 2.59 * np.array([gear_ratio[g_] for g_ in gear])    # ADC 2.0 (.vveh) x axle 2.59 x gear
        # rotor term built exactly like k_rot but with a per-row ratio (force_engine accepts only a scalar theta_red -> done outside)
        rot_series = (J_rot * i_row ** 2 / veh.r_dyn ** 2) * ac * base["v_avg"]
        He = dict(base)
        He["P_wheel_inertia"] = base["P_wheel_inertia"] + rot_series
        He["P_wheel"] = base["P_wheel"] + rot_series
        variant("e rotor inertia as extra wheel-side mass", He, f"+ J_rot*i_row^2/r^2*a*v_avg, J={J_rot} kg m2, i = 2.0*2.59*gear ratio per row")
        # compare the added term with VECTO's motor-side column
        rot_h = rot_series
        rot_v = VM.col(cols, "P_E2-em_inertia_loss") * 1000.0
        s = term_stats("rotor_inertia", rot_h, rot_v, dt)
        s.update(cycle=cyc, load=load, variant="e_vs_P_E2-em_inertia_loss", cdxa_rms_moving=0.0, cdxa_max_moving=0.0)
        term_rows.append(s)

    write_csv("partC_gate3_identity.csv", gate_rows)
    write_csv("partC_terms.csv", term_rows)
    write_csv("partC_causes_isolated.csv", cause_rows)
    write_csv("partC_flagged_rows_classes.csv", cls_rows)


if __name__ == "__main__":
    main()
