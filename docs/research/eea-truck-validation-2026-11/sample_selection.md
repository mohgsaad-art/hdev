# Job 3 sample selection

52 complete, non-flagged configs picked by `select_sample.py`, spread across make,
architecture, vehicle group, component certification method and battery size. The machine
rationale per config is in `sample_configs.csv` column `pick_reason`; the runs are in
`sample_runs.csv`.

## Why these 52

Greedy stratified pick: every make and every architecture must appear at least once; then
spread across vehicle group, battery bucket and certification method, preferring configs
with more vehicles (more real registrations behind them). Soft caps stop any one make or
architecture dominating.

Resulting coverage:

- **Architecture:** E-IEPC 17, E3 13, E2 12, E-IEPC-wheel 10 (all four present, incl.
  wheel-motor).
- **Make:** Mercedes-Benz 10, Iveco 8, Renault 8, Volvo 7, DAF 5, Scania 5, MAN 4, Fuso 4,
  Designwerk 1 (all 9 makes, including the single-vehicle Designwerk outlier).
- **Vehicle group:** 4 (15), 5 (12), 9 (7), 53 (7), 3 (3), 1 (2), 1s (2), 10/11/12/16 (1
  each) — small rigids through heavy tractors and the van-truck group 53.
- **Component certification method:** measured 19, standard 33 (so the measured-vs-standard
  split in the results is well populated both sides).
- **Battery size:** small <150 kWh 11, mid 150-400 20, large 400-700 20, xl ≥700 1.

## Runs

1,274 runs = config × representative vehicle × mission × payload. For each config we ran the
vehicle with **median** `TotalVehicleMass` on a reference mission, plus the **min** and
**max** mass vehicles (so mass spread within a config is covered). Each run is executed on
every certified mission for that vehicle, both payloads, at the vehicle's own
`TotalVehicleMass` (from `missions_xev.csv`). Each is run at two CdxA corners and four
drivetrain variants.

## Tyres / RRC check (section 4.7)

Per-axle `SpecificRRC` and `TyreDimension` come from `axle_xev.csv`. Across the 143 sampled
vehicles (319 axle rows): **0 rows with blank `SpecificRRC`, 0 with `CertificationNumber`
= N/A**. So no sampled vehicle needed the RRC fallback and none is flagged `[BOB]` for
tyres. Per-axle RRC was combined as a mean (the EEA data does not carry the mission axle-load
shares VECTO uses for the weighted sum; `force_engine` then applies the load exponent via
`m^β`, β = 0.9). r_dyn is taken from the driven axle's `TyreDimension` via VECTO
`Wheels.csv` (`d·f/2π`). Trailer tyres are not in the table; for tractors the generic VECTO
trailer values would be used (none of the sampled runs hit a missing trailer-tyre case
because `TotalVehicleMass` and RRC are taken as given).
