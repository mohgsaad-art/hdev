# The consumption engine, in simple words

This text explains `consumption_engine`: the step that turns "how the truck drives" into "how much energy leaves the battery".
All numbers in the examples are **ILLUSTRATIVE**. They are not model inputs. Written for Bob, 13 Nov 2026.

## The idea in one sentence

For every second of a trip, find the power the **wheels** need. Then find the power the **battery** must give to make that. Add the power for the extra equipment. Add up all the seconds.

## Words you need

* **Row.** One second of the trip. The driver model gives one row per second: time, distance, speed, mode.
* **Mode (`M`).** What the driver does in this row: 0 standing, 1 accelerating, 2 cruising, 3 coasting (no power), 4 braking.
* **Wheel power.** The power the wheels must deliver to the road to move the truck. Plus = the truck needs energy. Minus = the truck gives energy back (slowing down, going downhill).
* **Efficiency.** The part of the power that arrives. An efficiency of 0.9 means 10 % is lost as heat.
* **Regeneration ("regen").** The motor works as a generator when the truck slows down and charges the battery.
* **Terminal power.** The power at the battery's connectors. Plus (in HDEV) = the battery gives power. Minus = the battery is charged.
* **Rotor inertia.** The motor's rotating part has weight too. When the truck speeds up, the rotor must speed up as well. That costs energy. It is given back when the truck slows down.
* **Aux.** Everything except driving: lights and electronics (ES), air system (PS), cabin air (HVAC), steering pump (SP), cooling of the battery and motor (Cond).
* **PTO.** A power take-off: the body of the truck takes power from the vehicle (a refuse compactor lifting bins, a road sweeper).

## The seven steps

1. **Mass.** Each row gets the mass of the empty truck plus the payload. The payload is only written at the start and at every stop, so each row takes the last value before it.
2. **Hour.** Each row gets the number of its weather hour (`(start time + row time) // 3600`). One hour = one temperature and one wind table.
3. **Air.** From the hour's temperature we get the air density. From the hour's wind table and the speed we get the "air drag area" (CdxA). Wind at an angle makes more drag.
4. **Wheel power.** Add four parts: accelerating, rolling, rotating wheels, and air. Accelerating and rolling depend on the mass. Air depends on the density and CdxA. That is why mass and air density **must be known before step 5**: they can change the sign of the wheel power in a slow row (see the example below).
5. **Wheel to battery.** Follow the power through the drivetrain. Details below.
6. **Aux and PTO.** Add the power of the extra equipment, row by row.
7. **Battery.** Battery power = traction power + aux power. Energy = sum of power × time ÷ 3,600,000 (joule to kWh).

## Step 5 in detail: from wheel to battery

Think of a chain: **wheels → axle and gearbox → motor → inverter → battery**.

* **Driving (plus).** To get 100 kW at the wheels, the battery must give *more* than 100 kW, because every part loses some. We **divide** by the efficiency.
* **Regen (minus).** When the truck gives 100 kW back, the battery gets *less* than 100 kW. We **multiply** by the efficiency.
* **Each part decides for itself.** The gearbox looks at the sign of the power at the gearbox. The motor looks at the sign of the power at the motor. (VECTO does the same, `ElectricMotor.cs` 186–188, 297.) The old version decided once, at the wheel.
* **The rotor is added at the motor.** After the gearbox, before the motor. The rotor sits on the motor shaft, and its power goes through the motor's losses. A row where the wheels give a *little* back, but the rotor still needs more, is a **driving** row for the motor.
* **Coasting (`M` = 3).** The motor is off. No traction power. (VECTO: `BatteryElectricMotorController.cs` 44–47.)
* **Slow braking.** Below a speed (10 km/h for the E2 truck, VECTO's source code), the friction brakes do all the work. No regen. (Same file, 62–70.)
* **Limit.** The generator can only take so much power. The rest goes to the friction brakes.

### A tiny worked example (ILLUSTRATIVE)

One row: truck 9,500 kg, speed 10 m/s, accelerating at 0.5 m/s², flat road, air density 1.2 kg/m³, CdxA 5 m².

| Part | Wheel power |
|---|---|
| accelerating the truck | 48,688 W |
| rolling resistance (Crr 0.006) | 5,730 W |
| rotating wheels | 1,162 W |
| air drag | 3,233 W |
| **wheel power** | **58,812 W** |

* Old way, one number: 58,812 ÷ (0.98 × 0.95 × 0.95) = **66,495 W** of traction power.
* New way: gearbox first: 58,812 ÷ 0.98 = 60,012 W at the motor shaft. Add the rotor (0.45 kg·m², total ratio 10): +1,307 W → 61,319 W. Then motor and inverter: 61,319 ÷ (0.95 × 0.95) = **67,944 W**.
* Aux in this row (illustrative): 2,000 W. Battery power = 67,944 + 2,000 = **69,944 W**. In one second that is 69,944 J = 0.0194 Wh.

Why order matters: take a gentle downhill, wheel power −1,000 W, and a rotor term of +3,000 W (the truck speeds up a little). The old way sees a *negative* wheel power and says "regen": −884 W back to the battery. The new way adds the rotor first: (−1,000 × 0.98 + 3,000) ÷ 0.9025 = **+2,238 W**, the battery gives power. The sign flips.

## Step 6 in detail: aux and PTO

* **Always on:** ES, PS, HVAC. Also while the truck stands. (No aux while charging at the depot: decided 13 Oct.)
* **SP (steering pump):** only when the truck moves. VECTO checks the speed at the start of the second (`ElectricAuxiliaries.cs` 105–116, `Vehicle.cs` 326).
* **Cond (cooling):** on when a motor is on or a PTO runs (`Conditioning.cs` 83–91). Not while standing or coasting.
* **PTO at a stop:** the stop gets longer by the PTO time. The PTO profile sits in the middle of the stop. Standing rows are found with `M == 0`, not `V == 0` (the first row of accelerating also has speed 0 at its start).
* **PTO while driving:** starts after the stop and may run past the next stop. A new drive PTO while one runs is an error (VECTO throws).
* **Mechanical or electric body.** The question "does the body have its own electric motor?"
  * *No:* the PTO power is taken from the truck motor. It is added in step 5 at the motor shaft, before the motor losses.
  * *Yes:* the body takes electric power straight from the battery. It is added in step 6.

## What the checks showed

* If you give the engine VECTO's own efficiency in each row, it matches VECTO's battery energy within 0.3 % on six E2 runs. The way the steps are put together is right.
* The fixed efficiencies (0.95 / 0.95 / 0.98) are the big problem: results are 23–33 % too low. The real axle and gearbox lose a fixed amount of power even at low load, so a single multiplication is not enough. The engine is ready for loss maps (an efficiency can be one number **or** one number per row).

## Which VECTO lines each piece stands in for

| Piece | VECTO |
|---|---|
| rotor inertia at the motor | `ElectricMotor.cs` 186–188, 297, 304–308; `.vmod` column `P_E2-em_inertia_loss` |
| coasting: motor off | `BatteryElectricMotorController.cs` 44–47 |
| slow braking: no regen | same file 62–70; `GearboxData.cs` 90–99; `Constants.cs` 321 (AMT), 323 (AT) |
| aux straight to the battery | `DeclarationData.cs` 124 (DC/DC efficiency 1.0) |
| SP only when moving | `ElectricAuxiliaries.cs` 105–116 |
| Cond when a motor is on | `Conditioning.cs` 83–91 |
| drive PTO error when overlapping | `PTODriveAuxiliary.cs` 38–41 |
| mechanical PTO at the motor | `PowertrainBuilderBase.cs` 339–350, `PEVPTO.cs` 54–85 |
