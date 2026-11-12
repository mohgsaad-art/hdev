# The force engine, explained from scratch

*Written 12 Nov 2026 for Bob. Code of record: `HDEV_NEW_code_of_record_2026-11-12.ipynb`, cell 8 (`force_engine`) and cell 16, steps 1-4 (`consumption_engine`).*
*Every number in a worked example is marked ILLUSTRATIVE: it is there to show the arithmetic, it is not data.*
*VECTO line numbers are from `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`.*

## 1. What problem does it solve?

A truck needs power at its wheels to move. We call this **wheel power** (in watts, W). Wheel power is the sum of four things:

1. **Rolling resistance**: the tyres squash and flex on the road. This costs energy all the time.
2. **Air drag**: the truck pushes the air out of the way. Gets large at high speed.
3. **Slope**: going uphill costs energy, going downhill gives some back.
4. **Inertia**: making a heavy thing go faster costs energy (it is stored as movement energy). Slowing down gives it back.
   Spinning parts (wheels) also store energy, so they count too.

HDEV must compute wheel power for **many** cases of the same route: different payloads, different weather, different days of the year.
The slow part is the *driver model*: it decides, second by second, what speed and acceleration the truck has on the route.
We do not want to run it again for every payload and every hour of weather.

So the code is split in two:

* **`force_engine`** (run once per route and vehicle). It turns each driver row into a few *coefficients* that do **not** know the mass, the temperature or the air-drag area.
* **`consumption_engine`, steps 1-4** (run for every case). It multiplies those coefficients by the mass, the air density and the air-drag area of that case and adds them up. That is only a multiply-add, so it is very fast (about 0.7 ms for a 5 885-second Regional trip on the review machine).

## 2. The inputs of `force_engine`

| name | meaning | unit |
|---|---|---|
| `g` | gravity, 9.80665 (VECTO `DeclarationData.cs` line 72) | m/s² |
| `Crr` | rolling-resistance coefficient. The parser passes `Crr_eff` (see section 6) | - |
| `speed` | speed at the **start** of the row | m/s |
| `accel` | acceleration in the row (constant inside the row) | m/s² |
| `dt_s` | length of the row (1 s today) | s |
| `grade` | slope of the road in this row, in percent (rise ÷ distance × 100) | % |
| `r_dyn` | dynamic tyre radius | m |
| `theta_red` | total spinning inertia of the wheels, J | kg·m² |

## 3. The code, line by line

```python
grade = np.arctan(grade / 100)
```
A grade of 10 % means the road rises 10 m for every 100 m you drive along the ground. We need the angle θ of the road.
`atan(0.10)` gives it in radians. VECTO does exactly the same (`VectoMath.InclinationToAngle`, `VectoMath.cs` line 266-268).

```python
v1 = speed
v2 = np.maximum(speed + accel * dt_s, 0.0)
v_avg = (v1 + v2) / 2
```
`v1` is the speed at the start of the row, `v2` at the end. A truck cannot drive backwards inside a braking row, so `v2` is never below 0.
`v_avg` is the average speed in the row. Because the acceleration is constant inside the row, the average speed is simply the mean of start and end.
(VECTO assumes the same: `Vehicle.cs` line 158 and 163.)

```python
k_lin  = (g * np.sin(grade) + accel) * v_avg
```
Two forces per kilogram of truck: the slope force `g·sin θ` and the force that makes the truck faster `a`. Both are multiplied by the mass later.
Power = force × speed, so each is multiplied by `v_avg`. **Unit: W per kg.** Mass comes later, which is why this is "mass-free".

```python
k_roll = Crr * g * np.cos(grade) * v_avg
```
Rolling resistance per kilogram (of "mass to the power β", see section 6). `cos θ` is there because on a slope only part of the weight presses on the road.

```python
k_rot  = (theta_red / r_dyn**2) * accel * v_avg   # if theta_red > 0, else 0
```
The wheels spin. When the truck speeds up, the wheels must spin faster too, and that takes energy.
`theta_red / r_dyn²` turns the wheel inertia into an *equivalent mass* in kg (VECTO calls it "reduced mass"; `Wheels.cs` line 98).
It does not depend on the payload, so it is already a final number in watts.

```python
L = (v1 + v2) * (v1**2 + v2**2) / 8
```
Air drag power is `½ · ρ · CdxA · v³` (ρ = air density, CdxA = drag area). Inside a row the speed changes, so we need the **average of `½ v³`** over the row.
For constant acceleration this is exactly `(v1+v2)(v1²+v2²)/8`. This is the formula VECTO uses (`CrosswindCorrectionCdxALookup.cs` line 73-77).
Later, air power = `ρ · CdxA · L`.

```python
return k_lin, k_roll, k_rot, L, v_avg
```
`v_avg` is returned so the consumption engine can look up the right `CdxA` (it depends on speed).

### Worked example (ILLUSTRATIVE)

A truck at 10 m/s, accelerating at 1 m/s² for 1 s, on a 2 % slope, `Crr` = 0.0055, wheel inertia 39 kg·m², `r_dyn` = 0.4209 m:

* θ = atan(0.02) = 0.019997 rad, sin θ = 0.019996, cos θ = 0.99980
* `v2` = 11 m/s, `v_avg` = 10.5 m/s
* `k_lin` = (9.80665 × 0.019996 + 1) × 10.5 = **12.559** W/kg
* `k_roll` = 0.0055 × 9.80665 × 0.99980 × 10.5 = **0.5662** W/kg
* `k_rot` = (39 / 0.4209²) × 1 × 10.5 = 220.14 kg × 10.5 = **2 311.5** W
* `L` = (10+11) × (100+121) / 8 = **580.125** W per (kg/m³ · m²)

## 4. Turning coefficients into wheel power (`consumption_engine`, steps 1-4)

**Step 1: mass of each row.** The payload changes only at stops. `payload_engine` writes the payload on the start row and on every stop row.
`searchsorted(..., side="right") - 1` finds, for each row, the last waypoint at or before it (a row *at* a stop already has the new payload).
Mass = empty vehicle + that payload.

**Step 2: weather hour of each row.** `hour = (t_start + T) // 3600` says which hour of the weather arrays the row belongs to. Weather is held constant inside each hour.

**Step 3: air density and drag area per row.**
Air density: `ρ = p / (R · (T + 273.15))`. It is higher when it is cold (more air molecules in each cubic metre).
The drag area `CdxA_eff` depends on speed and wind. The crosswind engine gives two tables, `W1` and `W2`; `CdxA_eff = CdxA0·W1 + W2` for every weather hour and every speed in the grid (60, 65, … 130 km/h).
The code interpolates in that table at the row's average speed. Below 60 km/h it uses the 60 km/h value; above 130 km/h it uses the 130 km/h value.
(`v_avg * 3.6` converts m/s to km/h because the table is in km/h.)

**Step 4: the sum.**
```python
P_wheel = m_row * k_lin + m_row**beta * k_roll + k_rot + rho_row * cdxa_row * L
```
With our worked row, mass 10 000 kg, β = 1 (the plain form), ρ = 1.188 kg/m³, CdxA = 4.83 m² (all ILLUSTRATIVE):

| part | power |
|---|---|
| slope + inertia: 10 000 × 12.559 | 125 590 W |
| rolling: 10 000 × 0.5662 | 5 662 W |
| wheel inertia | 2 312 W |
| air: 1.188 × 4.83 × 580.125 | 3 329 W |
| **wheel power** | **136 892 W** (about 137 kW, positive = the motor must drive) |

Double the mass to 20 000 kg and only the first two lines change: no need to run the driver or `force_engine` again.

## 5. Why split it this way?

* Slow part (driver) once. Cheap part many times. A full year (365 days × 3 payloads) of steps 1-4 took 0.73 s in the review test.
* Anything that depends on mass sits in `consumption_engine` (it knows the mass). Anything that depends on weather sits there too.
* `force_engine` stays pure maths: every number is an argument, nothing is looked up, nothing is converted.
  Checks and defaults belong in the parser.

## 6. Two small things that are easy to miss

**β (beta) = 0.9.** VECTO's rolling resistance is not exactly proportional to mass: `F_roll = Crr_total(m) · m · g`, where the total coefficient itself depends on the mass through each tyre's load
(`VehicleData.cs` lines 292-311, exponent 0.9 in `Physics.cs` line 51). Written out, this is **exactly** `Crr_eff · g · m^0.9 · cos θ` with a constant `Crr_eff`,
as long as the share of weight carried by each axle stays fixed (it does: it comes from the segment table, not from the payload).
So the parser computes `Crr_eff` once per vehicle and the engine uses `m**beta`.
The review checked this on all six VECTO runs, including the trailer for LongHaul: the rolling energy matches VECTO to better than 0.002 %.

**Why the grade is an angle.** A 20 % slope has `sin θ` = 0.196, not 0.200. VECTO uses the angle, so HDEV does too.

## 7. Where each piece stands in VECTO

| HDEV | VECTO (commit b8d6126) |
|---|---|
| slope `m·g·sin θ·v_avg` | `Vehicle.cs` 232-237 (force), 198 (power) |
| rolling `Crr_eff·g·m^β·cos θ·v_avg` | `Vehicle.cs` 214-223, `VehicleData.cs` 292-311 |
| inertia `m·a·v_avg` | `Vehicle.cs` 225-230, 195 |
| wheel inertia `θ_red/r²·a·v_avg` | `Wheels.cs` 72-95, `Formulas.cs` 65-75 |
| air `ρ·CdxA·L` | `CrosswindCorrectionCdxALookup.cs` 68-78, `Vehicle.cs` 241-256 |
| `CdxA_eff` table | `AirdragDataAdapter.cs` 20-90, `Constants.cs` 353-365 |
| speed in the output file | `Vehicle.cs` 189-199 and `ModalData1HzFilter.cs` 46-180 |

## 8. What it does **not** include (and VECTO does, or physics does)

* Spinning inertia of the **motor rotor**. VECTO adds it at the motor shaft (`ElectricMotor.cs` 97-98, 186-196). On the E2 truck it is about as large as the wheel inertia.
* Cold tyres, wet or snowy roads, humidity, altitude. See the review report, Part F.

Full numbers, tests and the list of open questions: `docs/research/force-engine-review-2026-11.md`.
