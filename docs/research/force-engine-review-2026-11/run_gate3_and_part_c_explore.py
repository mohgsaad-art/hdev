"""Exploration helper (not a deliverable script): quick look at Gate 3 and Part C numbers."""
from _common import *

TERMS = ["P_roll", "P_air", "P_slope", "P_veh_inertia", "P_wheel_inertia"]
for key in LOADING:
    veh = Vehicle(*key)
    cols = load_vmod_run(*key)
    r = vmod_rows(cols)
    vt = vecto_terms(cols)
    vs, ac = trace_for_engine(r, "acc")
    tab = veh.cdxa_table()
    H = hdev_terms(veh, vs, ac, r["dt"], r["grad"], tab=tab)
    H2 = hdev_terms(veh, vs, ac, r["dt"], r["grad"], cdxa_row=vt["cdxa"])
    print(key)
    for t in TERMS:
        e_v = energy_kwh(vt[t], r["dt"])
        e_h = energy_kwh(H[t], r["dt"])
        e_h2 = energy_kwh(H2[t], r["dt"])
        d = H[t] - vt[t]
        print(f"  {t:16s} VECTO net {e_v['net']:8.3f} pos {e_v['pos']:8.3f} | HDEV(tab) net {e_h['net']:8.3f} ({(e_h['net']/e_v['net']-1)*100 if e_v['net'] else 0:+.3f}%) | HDEV(vcdxa) net {e_h2['net']:8.3f} ({(e_h2['net']/e_v['net']-1)*100 if e_v['net'] else 0:+.3f}%)  rms {np.sqrt(np.mean(d**2)):8.1f} W max {np.abs(d).max():8.1f}")
    cd = np.abs(H["cdxa"] - vt["cdxa"])
    print("   cdxa rms diff", np.sqrt(np.mean((H["cdxa"] - vt["cdxa"]) ** 2)), "max", cd.max())
    gate = vt["P_trac"] - (vt["P_roll"] + vt["P_air"] + vt["P_slope"] + vt["P_veh_inertia"])
    gate2 = vt["P_wheel_in"] - (vt["P_trac"] + vt["P_wheel_inertia"])
    print("   gate3 residual P_trac - sum: max", np.abs(gate).max(), "  P_wheel_in - (P_trac+P_wheel_inertia): max", np.abs(gate2).max())
