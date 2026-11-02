# VECTO runs for the driver-model review (Nov 2026)

**For Bob to run. Kiro cannot run VECTO in the sandbox.** These runs produce the
`.vmod` / `.vsum` files that Parts D, E and F of the review need. Without them those
parts are **BLOCKED** (see the review document's BLOCKED list).

- **VECTO version:** 5.1.6 (the version your earlier `.vmod` runs used). The review
  source audit was done against v5.1.3 (`d16ba783c`) because no 5.1.6 tag exists in
  `mohgsaad-art/VECTO`; re-confirm the driver constants haven't changed between the two
  (they were identical in every file checked, but 5.1.6 was not available to read).
- **Vehicle:** generic E2 PEV, from
  `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/` in the VECTO install.
  The ready-made job there is `BEV_E2.vecto` (declaration mode, Overspeed on,
  MinSpeed 50 km/h, OverSpeed 2.5 km/h — confirmed in the file).

## What each run is for

| Run | Purpose (which review part) | How to set it up |
|---|---|---|
| **R1 LongHaul, reference load** | more overspeed/coast coverage than Regional/Urban (Part D, hypotheses h1–h7) | declaration run of `BEV_E2.vecto`; keep the LongHaul mission result |
| **R2 Construction, reference load** | steep-grade coasting + the over-.vacc downhill coast finding (Part A new finding, Part D) | same job; keep the Construction mission result |
| **R3 Regional, LowLoading** | fixed-mass effect (Part E) — a second mass point to compare the "wrong-mass trace" error against | declaration run; keep the RegionalDelivery **Low Loading** result rows |
| **R4 Urban, LowLoading** | same, urban (Part E) | keep the UrbanDelivery Low Loading result rows |
| **R5 look-ahead coasting OFF** | isolate the coasting feature (Part D h-ranking) | **engineering mode** copy of the E2 job, Driver → LAC disabled |
| **R6 overspeed OFF** | isolate the overspeed feature (Part D) | engineering-mode copy, Driver → Overspeed disabled |

R5 and R6 need **engineering mode** because declaration mode fixes the driver options.
Build an engineering job from the same component files (`.vveh`, `.vgbx`,
`GenericDrag_125kW_485Nm.vemd`, `Gear_1.vtlm`, `Gear_2.vtlm`, the axle `.vtlm`,
`Truck.vacc`) and the declaration cycle `.vdri` files, then toggle one driver option.
If 5.1.6 does not allow toggling LAC/overspeed independently in engineering mode, say so
and skip R5/R6 — do not fake them.

## `.vmod` columns that MUST be written

In VECTO Options → Output, make sure the modal (`.vmod`) file includes at least:

- `time`, `dist`, `v_act` (actual speed), `v_targ` (target), `acc`, `grad`, `altitude`
- **`DriverAction`** — the per-row driver action code. This is the column Parts C/D
  need to map modes. VECTO codes (`Driver.cs` line 50, v5.1.3): `Halt=0, Roll=2,
  Coast=4, Accelerate=6, Brake=-5`.
- Per-component losses: `P_gbx_loss`, `P_axle_loss`, electric-motor drag power, and
  brake power — needed to measure the real coasting drag force (Part D h1/h6) and the
  wheel-energy split (Part D metric 7).
- `P_wheel` / `P_trac`, `P_air`, `P_roll`, `P_slope` if available — for the
  wheel-energy cross-check.

## Where to put the results

Copy the resulting files into `reference/vecto/runs/` with these exact names
(the review harness and Part D script expect them):

```
reference/vecto/runs/BEV_E2_RegionalDelivery_ReferenceLoad_1Hz.vmod
reference/vecto/runs/BEV_E2_UrbanDelivery_ReferenceLoad_1Hz.vmod
reference/vecto/runs/BEV_E2_LongHaul_ReferenceLoad_1Hz.vmod
reference/vecto/runs/BEV_E2_Construction_ReferenceLoad_1Hz.vmod
reference/vecto/runs/BEV_E2_RegionalDelivery_LowLoading_1Hz.vmod
reference/vecto/runs/BEV_E2_UrbanDelivery_LowLoading_1Hz.vmod
reference/vecto/runs/*.vsum
```

Set the modal output to **1 Hz** (one row per second) so it lines up with HDEV's
default `dt = 1.0`.

## Exact GUI steps (VECTO 5.1.6)

1. Open VECTO. **File → Open** the job `BEV_E2.vecto` from the GenericVehicleE2 folder.
2. **Options → Output:** tick "Write modal results (.vmod)", set the modal output to
   1 Hz, and enable the extra columns listed above (DriverAction, component losses).
3. For the **reference-load** runs (R1, R2): run the job as-is (declaration mode runs
   all mission profiles; keep LongHaul and Construction results).
4. For the **LowLoading** runs (R3, R4): declaration mode already produces a Low
   Loading result alongside Reference Load for each mission — keep the Regional and
   Urban Low Loading `.vmod`.
5. For **R5/R6**: save a copy of the job, switch to engineering mode, load the same
   components and the single `.vdri` cycle, and disable LAC (R5) or Overspeed (R6)
   under the Driver settings. Run each cycle you care about.
6. Copy the `.vmod`/`.vsum` into `reference/vecto/runs/` with the names above.
