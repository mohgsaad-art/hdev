"""Item C (slide 3 "Ready by 06:00?"): does charging slow as the battery fills?

Method M4: VECTO's OCV + Ri battery model with ITS charge limits, constant charger
power cap, no thermal model.

VECTO battery (GenericBattery_243kWh, 2 packs, from the generic Group-5 BEV):
  Capacity 324 Ah/pack, Ri 0.04 ohm (constant), I_charge_max 1620 A (FLAT over SoC),
  SOC window 10-90%, OCV table 673.5..750.2 V.
  Per step (Battery.cs:Request):
    I from P=(U0+I*Ri)*I ; SoC += I*dt/Capacity ;
    MaxChargeCurrent(dt)=min((SOC_max-SoC)*Cap/dt, 1620).

Charger: 50 kW (the refuse-truck report's example charger). We model the 2-pack
system; both packs identical so the SoC-vs-time SHAPE is pack-count independent.
We integrate SoC from a start to a stop SoC at a constant 50 kW terminal cap,
throttled only by the battery limits.

KEY VECTO FACTS the result turns on:
  * MaxCurrent map is FLAT 1620 A -> VECTO has NO SoC-dependent charge-current
    taper for this generic pack.
  * SOC_max = 90% -> "80% to 100%" is NOT reachable inside VECTO's declaration
    window. We therefore report 20->80% vs 80->90% (the top of the usable window),
    and flag that a true 80->100% taper is NOT in VECTO (not estimable from VECTO).

Run: /projects/sandbox/.venv/bin/python scratch/pitch_estimates/07_charging.py
"""
import numpy as np

from vecto_data import BATTERY, ocv

CHARGER_KW = 50.0
N_PACKS = 2
CAP_AS = BATTERY["capacity_Ah"] * 3600.0        # As per pack
RI = BATTERY["Ri_ohm"]
I_MAX = BATTERY["I_charge_max_A"]
SOC_MAX = BATTERY["soc_max"]


def charge_time(soc_start, soc_stop, charger_kw=CHARGER_KW, dt=1.0,
                soc_cap=SOC_MAX):
    """Integrate charge time [s] and energy [kWh] from soc_start to soc_stop.
    System = N_PACKS identical packs; charger power split evenly per pack.
    Positive current charges (VECTO sign convention)."""
    p_pack = charger_kw * 1000.0 / N_PACKS          # W per pack (terminal)
    soc = soc_start
    t = 0.0
    e_terminal = 0.0
    e_loss = 0.0
    while soc < soc_stop - 1e-9:
        u0 = ocv(soc)
        # per-step max charge current from the SoC-window cap and the flat limit
        i_window = (soc_cap - soc) * CAP_AS / dt
        i_cap = min(i_window, I_MAX)
        # solve p_pack = (u0 + I*Ri)*I  for I>0 : Ri*I^2 + u0*I - p = 0
        disc = u0 ** 2 + 4 * RI * p_pack
        i_req = (-u0 + np.sqrt(disc)) / (2 * RI)
        i = min(i_req, i_cap)
        # advance SoC (don't overshoot the target)
        dsoc = i * dt / CAP_AS
        if soc + dsoc > soc_stop:
            dsoc = soc_stop - soc
            dt_eff = dsoc * CAP_AS / i if i > 0 else dt
        else:
            dt_eff = dt
        soc += dsoc
        t += dt_eff
        # energy into the pack this step (terminal) and loss
        p_term = (u0 + i * RI) * i
        e_terminal += p_term * dt_eff
        e_loss += (i * i * RI) * dt_eff
    # scale energy to the whole system (N_PACKS)
    return t, e_terminal * N_PACKS / 3.6e6, e_loss * N_PACKS / 3.6e6


def usable_energy_kwh():
    """VECTO UseableStoredEnergy over [SOC_min, SOC_max] = integral U0*Cap dSoC."""
    socs = np.linspace(BATTERY["soc_min"], SOC_MAX, 2000)
    u = ocv(socs)
    cap_as_sys = CAP_AS * N_PACKS
    # energy = integral over SoC of U0 * Capacity dSoC
    e = np.trapz(u * cap_as_sys, socs) if hasattr(np, "trapz") else \
        np.trapezoid(u * cap_as_sys, socs)
    return e / 3.6e6


def main():
    print("Battery: 2 x 324 Ah, Ri 0.04 ohm (const), I_charge 1620 A (FLAT),"
          " SOC window 10-90%")
    print(f"Charger: {CHARGER_KW:.0f} kW (constant power cap)")
    print(f"System usable energy (10-90%, VECTO def): {usable_energy_kwh():.1f} kWh\n")

    for lo, hi, lbl in [(0.20, 0.80, "20% -> 80%"),
                        (0.80, 0.90, "80% -> 90% (top of VECTO window)")]:
        t, e, loss = charge_time(lo, hi)
        # straight-line estimate: energy / charger power
        t_sl = e / CHARGER_KW * 3600.0
        print(f"  {lbl:34s} time {t/60:6.1f} min  energy {e:6.2f} kWh  "
              f"loss {loss:.2f} kWh  (straight-line {t_sl/60:.1f} min, "
              f"+{(t/t_sl-1)*100:.1f}%)")

    # Compare the two phases per % SoC to show whether it slows down.
    t20_80, e20_80, _ = charge_time(0.20, 0.80)
    t80_90, e80_90, _ = charge_time(0.80, 0.90)
    print(f"\n  per 1% SoC: 20-80% = {t20_80/60/60:.2f} min/%  ;  "
          f"80-90% = {t80_90/60/10:.2f} min/%")
    print("\n  FINDING: with a flat 1620 A limit and a 50 kW cap, the charger power"
          "\n  is the binding limit across the whole window -- the battery does NOT"
          "\n  throttle until the SoC-window cap bites in the last fraction of a %."
          "\n  VECTO's generic pack has NO SoC-dependent charge-current taper and"
          "\n  its usable window stops at 90%, so a genuine 80->100% CV taper is NOT"
          "\n  representable from VECTO data -> that specific comparison is NOT"
          "\n  estimable now (needs a real OEM charge-rate-vs-SoC curve).")


if __name__ == "__main__":
    main()
