# Findings: Ban & Stipetić 2019, ePTO load cycles (for the PTO profile library)

Source [SOURCE, full text read]: B. Ban, S. Stipetić, "Electric Multipurpose Vehicle Power Take-Off: Overview, Load Cycles and Actuation via Synchronous Reluctance Machine", ACEMP-OPTIM 2019, Istanbul. https://ieeexplore.ieee.org/document/9007187 (author postprint, uploaded by Bob 12 Nov 2026).

## What it gives
- Table IV: PTO load cycles as time / shaft torque [Nm] / shaft speed [rpm] for refuse truck, concrete mixer (8 m3 drum), vacuum truck, hook-loader.
- PTO requirement range: approx. 30-90 kW, 190-570 Nm (Fig. 3); PTO speed 1500-3000 rpm (eq. 1, from Volvo).
- Cycles are **approximations built from OEM documents** (Volvo PTO guide, Veolia, HIAB, Kanematsu, etc.), **not measurements**. Purpose in the paper: ePTO machine sizing (peak/continuous), not energy.
- Refuse cycle is only the illustrated subcycle (footnote of Table IV); the full cycle must be built from Fig. 5 (bins, 2 m3 bin, 40 m3 body, compaction factor 0.5).

## [CALC] shaft energy per cycle (Claude, from Table IV; P = T·n·2π/60)
| Body | Cycle length | Shaft energy, linear between points | Left-hold (VECTO-style) | Peak | Mean |
|---|---|---|---|---|---|
| Refuse (illustrated subcycle) | 5070 s | 1.45 kWh | 1.43 kWh | 39.6 kW | 1.0 kW |
| Concrete mixer | 6060 s | 42.6 kWh | 45.0 kWh | 90.5 kW | 25.3 kW |
| Vacuum | 5495 s | 1.51 kWh | 1.51 kWh | 63.9 kW | 1.0 kW |
| Hook-loader | 4011 s | 0.86 kWh | 0.90 kWh | 39.8 kW | 0.8 kW |
[ASSUMPTION] The paper does not say whether values ramp linearly or step between points; both shown. Mixer differs by 6 %.

## Caveats before use in HDEV
1. Mechanical **shaft** power at the pump. Electric W needs the ePTO motor + inverter efficiency: NO SOURCE in the paper.
2. Time points at 0.5 s: HDEV profiles must be whole seconds (parser) → needs per-second averaging (parked item).
3. Mixer drum runs while driving → fits the drive-PTO / always-on path, not stop PTO.
4. Not validation data. Tag as [SOURCE, approximated cycle].

## References worth fetching (from the paper)
- [2] Volvo, "Power take-offs: Fields of application and Calculation guide", 2018: http://productinfo.vtc.volvo.se/files/pdf/lo/PowerTake-off(PTO)_Eng_08_580114.pdf (robots-blocked for Claude) — PTO power by application; the paper's main data source.
- [5] Volvo body builder instructions, PTO and pumps: https://www.volvotrucks.ca/en-ca/parts-and-services/service/body-builder/manuals/
- [8] Parker Hannifin truck hydraulics catalogue MSG30-8200/UK (pump efficiency): https://www.parker.com/Literature/PMDE/Catalogs/Truck_Hydraulics/MSG30-8200_UK.pdf
- [6] Bae et al. 2018, mixer truck gearbox strength, IOP MSE 317: doi 10.1088/1757-899X/317/1/012010
- [12] Ferraris, "Concrete mixing methods and concrete mixers", J. Res. NIST 106(2) 391 (2001, paper cites 2012): doi 10.6028/jres.106.016
- [14] HIAB multilift specs; [16] Kanematsu Mobile Vac specs (OEM pages)
- Skip: [13] Yang 2017 (Mech. Sci. 8:165, doi 10.5194/ms-8-165-2017): checked, vibration only, no drum torque/power. Rare-earth / SyRM references not relevant.
