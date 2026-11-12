# Auxiliaries and PTO explained (plain English)

Written 12 Nov 2026 for Bob. It explains `P_aux`, `SP_power_helper`, `pto_engine` and the aux/PTO part of
`consumption_engine`, as they are in the notebook of 12 Nov 2026 (the "code of record"). It does not change any code.
Every number in the worked examples is **ILLUSTRATIVE** unless it carries a source tag. The facts about VECTO come from
`mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`. The full evidence is in
`docs/research/aux-pto-review-2026-11.md`.

## 1. Words used here

- **Auxiliary ("aux")**: anything on the truck that uses energy but does not move the truck. The battery pays for it.
- **Electric W**: power drawn from the battery, in watts. This is what HDEV needs.
- **Mechanical W**: power taken from a rotating shaft. In VECTO's tables many aux values are written as mechanical W (what a
  diesel engine would have had to deliver). To get electric W, VECTO multiplies or divides by a factor.
- **PEV / BEV**: battery-electric vehicle (VECTO says PEV).
- **PTO (power take-off)**: a power outlet for the body on the truck: the bin lifter and compactor on a refuse truck, the drum of a
  concrete mixer, a crane, a sweeper brush, a fridge unit.
- **Stop PTO**: the body works while the truck stands still (bin lift).
- **Drive PTO**: the body works while the truck moves (sweeper brush).
- **Always-on PTO**: runs the whole time on the route, standing or driving (a fridge unit). HDEV puts this into `P_aux`.
- **Row**: one second of the simulated drive. The driver model makes the rows; each row has time `T`, distance `S`, speed `V`
  (speed at the **start** of that second), and a driving mode `M` (0 standing, 1 accelerating, 2 cruising, 3 coasting, 4 braking).
- **Waypoint**: one line of the route (a VDRI line): a distance, a target speed, a gradient and a stop time. The route has few
  waypoints and thousands of rows.
- **Profile**: a list of time/power pairs, for example "0–4 s: 8.42 kW, 5–8 s: 33.69 kW …". Each power value holds until the next time.
- **Parser**: the code, not yet written (`defaults.py`), that reads tables and user input, checks it, converts units and hands clean
  numbers to the engines. **Engine**: pure maths, no tables, no unit conversion.

## 2. The five aux of a battery-electric lorry in VECTO

| Aux | What it is | Table | Table value means | Factor to electric W | E2 Regional example |
|---|---|---|---|---|---|
| **ES** electric system | lights, controllers, 24 V loads | `ES-Tech.csv` | mechanical W at an alternator shaft | × 0.7 | 1428.57 W → **1000 W** |
| **PS** pneumatic system | air compressor (brakes, doors); for a BEV only the "elec. driven" kinds | `PS-Table.csv`, the `_el` columns | **electric W**, as is | × 1.0 | 200 W → **200 W** |
| **HVAC** cab air-conditioning | A/C compressor ("Default"), no heater | `HVAC-Table.csv` | mechanical W of the compressor | ÷ 0.8 (= × 1.25) | 200 W → **250 W** |
| **SP** steering pump | pump or electric steering gear | `SP-Table.csv` × `SP-Axles.csv` × `SP-Tech.csv` | mechanical W | × 0.7 | 32.87 W → **23.0 W** |
| **Cond** conditioning | cooling/heating of the electric drive parts ("electric propulsion components") | `Cond-Table.csv` | **electric W**, as is | × 1.0 | **600 W** |

Where the factors come from (VECTO `DeclarationData.cs` lines 123–126): 0.7 is VECTO's "generic alternator efficiency", used for
everything that is written as mechanical power at an alternator. 0.8 is the "HVAC electric efficiency factor", and
`HeavyLorryAuxiliaryDataAdapter.cs` line 78 uses its inverse, 1/0.8 = 1.25. VECTO's release notes say the same 0.7 principle
applies to PEVs. The *reason* for 0.8 is not stated in any file I read.

`P_aux` does exactly these multiplications, with the factors as arguments. `HVAC_eff` must be 1.0 when the HVAC power already
comes from HDEV's own thermal model.

## 3. When each aux is on (VECTO) and what HDEV does

VECTO decides on **the state at the start of the step**.

- ES, PS, HVAC: always on, also when standing.
- SP: off when the truck stands (|v| ≤ 0.01 m/s). `ElectricAuxiliaries.cs` line 114 removes the ID "STP" when the vehicle is stopped.
  A VECTO commit of 29 Sep 2022 (`be6ce764`, message "ignore steering pump when vehicle is stopped") made this on purpose for the steering pump.
- Cond: on when at least one electric motor is **not off**, or when the electric PTO is on (`Conditioning.cs` lines 83–91). The motor is "off" when the
  controller gives no torque: standing, **coasting**, and braking at very low speed.

HDEV today: SP is on when `V > 0`; Cond is on when `V > 0` or a stop PTO runs. The only real difference is Cond while coasting (HDEV on, VECTO off).
On the six E2 runs this makes HDEV's aux total 0.3–1.1 % higher than VECTO's, which is 0.01–0.09 % of the trip energy.

## 4. `P_aux` line by line

```python
powers = [np.asarray(p, dtype=float) for p in (ES_power, ...)]   # turns numbers or lists into arrays so the maths works on both
effs   = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)   # the five factors
for p in powers: if np.any(p < 0): raise ...                     # no negative power
for e in effs:   if e <= 0: raise ...                            # no zero or negative factor
... = (p * e for p, e in zip(powers, effs))                      # electric W = input W × factor
PTO_always_on = PTO_always_on / PTO_eff                          # always-on PTO: shaft W ÷ efficiency
```

Worked example (ILLUSTRATIVE fridge): `PTO_always_on = 2000` W at the shaft and `PTO_eff = 0.8` → 2500 W from the battery.
Two gaps are described in the review: the notebook does not check `PTO_always_on < 0` or `PTO_eff <= 0` (a zero efficiency gives `inf`
with only a warning), and NaN passes through unnoticed.

## 5. `SP_power_helper` line by line

VECTO builds the steering-pump power from three parts: **U+F** (unloaded and friction), **B** (banking) and **S** (steering).
The table gives three numbers for each group and mission, for example `290/30/20` for group 2, Regional delivery.

1. Each steered axle has a share per part (`SP-Axles.csv`): the first axle 100/100/100 %, the second 100/70/70 %, the third and fourth 100/50/50 %.
   The shares of all steered axles are **added**.
2. Each steered axle has a technology (`SP-Tech.csv`); each technology has a factor per part. The factors are **averaged** over the axles.
3. Result = Σ over the three parts of (baseline × summed shares ÷ 100 × averaged factor). It is mechanical W; `P_aux` multiplies by 0.7.

Example (ILLUSTRATIVE choice of technology, real table numbers): baseline 290/30/20 W, one axle, "Full electric steering gear" (0 / 0.143 / 1.429):
0 + 30×0.143 + 20×1.429 = 4.29 + 28.58 = 32.87 W; × 0.7 = 23.0 W. That matches the VECTO `.vmod` (23.0 W while moving).

## 6. `pto_engine` line by line

It works on the waypoints, before the driver model.

1. `stop` is the final standing time of each waypoint **including the PTO time** (the parser adds it: standing = stop + PTO duration, as VECTO does).
2. `is_on` says where the PTO is used (1) or not (0). The first waypoint, the depot, is forced to 0.
3. Each profile becomes one power value per second: `np.diff(t)` gives how long each value lasts, `np.repeat` copies it. **This needs whole seconds**
   (fractional seconds are cut off silently).
4. The stop profile is divided by its efficiency, the drive profile by its own efficiency.
5. The stop profile starts in the middle of the stop: `floor((stop − profile length) / 2)`. VECTO does the same (idle `StoppingTime/2`, PTO, idle `StoppingTime/2`).
   If the profile does not fit, it raises an error; the parser must have made the stop longer.

Worked example, VECTO refuse profile: 23 one-second values; energy = (5×8.42 + 4×33.69 + 14×25.92) kJ = 539.74 kJ = **0.14993 kWh** per stop. A 2 s stop becomes
25 s; the PTO starts after floor((25−23)/2) = 1 s, so: 1 s idle, 23 s PTO, 1 s idle. MunicipalUtility has 96 such stops → 14.39 kWh.

## 7. How aux and PTO land on the rows (consumption engine, steps 6–7)

- Each aux is a number (or, for HVAC, one number per weather hour). Per row: `P_aux_row = ES + PS + HVAC + SP×(moving) + Cond×(moving or PTO) + always-on PTO + PTO on this row`.
- Stop PTO: for each waypoint with `is_on = 1`, find the standing rows of that stop (speed 0 and distance equal to the waypoint distance), start `pto_start`
  rows after the first one, and copy the profile there.
- Step 7: battery power = traction power + `P_aux_row`; energy = Σ power × 1 s ÷ 3.6e6 kWh. VECTO's DC/DC converter has efficiency 1.0, so adding is right.

What the notebook does not have yet (the review tests a variant): the drive part, constants, the 0 s marker waypoint, and the overlap check. Also: the
driver rows have **one extra row with speed 0** per stop (the first accelerating second starts at speed 0), so "speed = 0 and distance matches" finds stop + 1 rows;
the review proposes also testing `M == 0`.

## 8. Things worth remembering

- A profile with `[0, 1]` and `[0, 0]` is **not** "no profile": it is a 1 s profile with 0 W. "No profile" is one point (or an empty list).
- Municipal results must include the stop PTO: 14.39 kWh over the 11.2 km cycle with the VECTO profile, and the 96 × 23 s of extra standing time.
- A VECTO battery truck that declares a **mechanical** PTO type gets a constant torque loss on the motor side, on every mission. The review calculates 0.16 kWh/km
  for the oil-pump type (not yet confirmed by a VECTO run; see `reference/vecto/jobs/aux-pto-2026-11/README.md`).
