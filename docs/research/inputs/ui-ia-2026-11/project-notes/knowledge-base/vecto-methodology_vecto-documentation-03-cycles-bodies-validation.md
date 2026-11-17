# VECTO / HDV CO2 Certification Methodology — Part 3: CO2 Test Cycles, Standard Bodies/Trailers, CFD Aerodynamics, SiCo Validation, Sensitivity Analysis, Proof of Concept

*(Source: same LOT 3 report, Report No. I 07/14/Rex EM, 25.06.2014, Sections 4.3–4.9, pages 42–98 of 170)*

## 4.3. CO2 Test Cycles

VECTO uses **target speed cycles** ("CO2 test cycles") defining the velocity the driver wants to reach over trip distance. **Five HGV mission profiles and five bus mission profiles** were developed, coordinated by ACEA with LOT3 support. Full cycle definitions are in the (separate) Technical Annex.

**Ten mission classes (verbatim list):**
Urban delivery, Regional delivery, Long haul, Construction, Municipal utility (HGV); Citybus heavy urban, Citybus urban, Citybus suburban, Interurban bus, Coach (buses).

### 4.3.1. Development & Validation Approach

- Cycles were developed from extensive analysis of **in-use driving behaviour data**.
- An in-use cycle = short trips (v>1 km/h) + stop sections; short trips were replaced by target-speed sections + corresponding stops.
- Validation: comparison against the **EU part of the WHDC database** (the database underlying the WHDC — World Harmonized Driving Cycle — development).
- Since target-speed cycles are distance-based (1 m resolution) while the in-use database is time-based (1 s resolution), acceleration/deceleration phases were reconstructed using **constant specific acceleration power values (v·a)** with an upper acceleration limit (so acceleration decreases with increasing speed, matching in-use data trends). Sensitivity analysis set the v·a variation range; average acc/dec cases were chosen for comparison.
- This means **acceleration distributions from the target speed cycles are not generalizable** to describe real-world acceleration behaviour — an explicit methodological caveat in the source.
- Road-gradient profiles were checked for altitude balance (start ≈ end altitude) and smoothed if "rippled," but **could not be validated** against real-world data because the WHDC database lacks road-gradient information.

### 4.3.2–4.3.6 Cycle-by-Cycle Validation Findings

**Urban delivery:** WHDC database had 8 rigid trucks + 12 trailer/semi-trailer trucks; 4 rigid trucks assigned to urban delivery. **[Figure 13/14 descriptions]:** cumulative vehicle-speed frequency distributions (time-weighted / distance-weighted) comparing 4 in-use vehicles, their average, and the VECTO urban-delivery cycle — VECTO cycle generally matches average speeds, stop %, and stops/km well; cruise-phase % is notably higher in VECTO than in-use (target-speed concept effect).

**Table 13 (Key parameters, urban delivery)** is referenced but its numeric content was not distinctly OCR-extractable as a standalone table in this pass (its content overlaps with the printed narrative describing "good accordance ... especially average speeds, stop percentages and number of stops per km").

**Regional delivery — Table 14 (Key parameters)** — reproduced:

| Parameter | WHDC database | VECTO cycle |
|---|---|---|
| v_05 [km/h] | 4.0 | 7.9 |
| v_10 [km/h] | 8.3 | 11.7 |
| v_15 [km/h] | 12.4 | 16.0 |
| v_50 [km/h] | 38.0 | 36.4 |
| v_85 [km/h] | 61.0 | 59.0 |
| v_90 [km/h] | 68.0 | 67.0 |
| v_95 [km/h] | 77.0 | 71.1 |
| v_ave w/o stop [km/h] | 38.3 | 38.3 |
| v_ave w/ stop [km/h] | 30.8 | 30.8 |
| p_stop | 19.6% | 19.6% |
| # stops/km | 1.0 | 1.0 |
| time [h] | 35.8 | 0.88 |
| distance [km] | 1,103 | 27.8 |
| a_pos_ave [m/s²] | 0.42 | 0.45 |
| p_acceleration | 34.4% | 22.5% |
| p_cruise | 35.7% | 58.4% |
| p_deceleration | 29.9% | 19.1% |

*(Note: this table, headed "urban delivery" in the source layout, appears immediately before the regional-delivery narrative — its exact cycle attribution as printed is ambiguous in the source's page layout; reproduced as it appears.)*

**Regional delivery — second table (labelled "regional delivery" explicitly in source)** — reproduced:

| Parameter | WHDC database | VECTO cycle |
|---|---|---|
| v_05 [km/h] | 11.0 | 16.9 |
| v_10 [km/h] | 19.0 | 26.8 |
| v_15 [km/h] | 27.0 | 34.1 |
| v_50 [km/h] | 65.8 | 68.0 |
| v_85 [km/h] | 86.3 | 85.0 |
| v_90 [km/h] | 88.3 | 85.0 |
| v_95 [km/h] | 90.0 | 85.0 |
| v_ave w/o stop [km/h] | 60.5 | 63.1 |
| v_ave w/ stop [km/h] | 56.3 | 58.7 |
| p_stop | 6.9% | 7.1% |
| # stops/km | 0.23 | 0.23 |
| time [h] | 50.4 | 0.44 |
| distance [km] | 2,836 | 25.8 |
| a_pos_ave [m/s²] | 0.24 | 0.26 |
| p_acceleration | 30.9% | 20.7% |
| p_cruise | 42.7% | 71.0% |
| p_deceleration | 26.4% | 8.3% |

Finding: VECTO regional-delivery cycle's urban→rural (52–63 km/h) and rural→motorway (74–84 km/h) transitions were judged **too abrupt** vs. in-use data; motorway share overestimated vs. WHDC average (though report notes the WHDC database is old and real-world motorway share may have risen). VECTO's max speed (85 km/h) is "quite frequently exceeded" in real operation (up to 90+ km/h).

**Long haul — Table 15 (Key parameters)** — reproduced:

| Parameter | WHDC database | VECTO cycle |
|---|---|---|
| v_05 [km/h] | 24.5 | 34.7 |
| v_10 [km/h] | 46.8 | 53.8 |
| v_15 [km/h] | 58.3 | 60.0 |
| v_50 [km/h] | 81.7 | 85.0 |
| v_85 [km/h] | 88.5 | 85.0 |
| v_90 [km/h] | 88.5 | 85.0 |
| v_95 [km/h] | 89.8 | 85.0 |
| v_ave w/o stop [km/h] | 74.6 | 77.5 |
| v_ave w/ stop [km/h] | 72.0 | 73.9 |
| p_stop | 3.5% | 4.6% |
| # stops/km | 0.050 | 0.055 |
| time [h] | 721.4 | 1.46 |
| distance [km] | 51,937.9 | 108.2 |
| a_pos_ave [m/s²] | 0.16 | 0.18 |
| p_acceleration | 30.1% | 9.0% |
| p_cruise | 42.8% | 85.7% |
| p_deceleration | 27.1% | 5.3% |

Long-haul WHDC data: 7 vehicles (2 real-operation-monitored [#17,#18], 5 fully laden 40t semitrailers driven Finland→Spain on the same route/time for OEM monitoring [#31–35]). VECTO's rural→motorway transition judged too abrupt (60–84 km/h underrepresented vs WHDC). If VECTO's Eco-Roll function is active, vehicle speed can exceed target speed on downhill sections (relevant since high-speed segments in the WHDC data corresponded mostly to downhill driving). Stop %: VECTO 4.6% vs WHDC range 1.7–4.2% (avg 3.5%).

**Bus cycles (heavy urban, urban, suburban, interurban):** based on extensive European in-use data (WHDC bus database limited: Germany + Switzerland only). **[Figure 19/20 descriptions]:** cumulative speed-frequency distributions (time/distance weighted) for citybus heavy urban / urban / suburban / interurban bus vs. WHDC in-use vehicles. Heavy urban cycle close to upper (low-speed) envelope of in-use data; urban cycle near center; suburban tends to lower (higher-speed) envelope; interurban bus cycle **outside** the WHDC range (no such in-use bus data existed in WHDC).

**Table 16 (Key parameters, bus missions)** — reproduced:

| Parameter | Heavy urban (WHDC) | Heavy urban (VECTO) | Urban (WHDC) | Urban (VECTO) | Suburban (WHDC) | Suburban (VECTO) | Interurban (WHDC, n/a) | Interurban (VECTO) |
|---|---|---|---|---|---|---|---|---|
| v_05 [km/h] | 2.0 | 3.6 | 2.8 | 5.2 | 4.8 | 6.4 | — | 10.2 |
| v_10 [km/h] | 4.8 | 5.8 | 6.0 | 8.0 | 9.4 | 10.2 | — | 16.8 |
| v_15 [km/h] | 6.9 | 8.0 | 9.0 | 11.1 | 12.9 | 14.2 | — | 18.0 |
| v_50 [km/h] | 19.5 | 21.9 | 25.0 | 26.5 | 31.9 | 31.2 | — | 34.7 |
| v_85 [km/h] | 32.6 | 34.7 | 39.5 | 38.3 | 47.0 | 46.0 | — | 69.7 |
| v_90 [km/h] | 35.8 | 37.5 | 42.8 | 42.4 | 53.0 | 49.3 | — | 74.0 |
| v_95 [km/h] | 40.8 | 40.9 | 47.2 | 47.3 | 59.4 | 53.9 | — | 79.0 |
| v_ave w/o stop [km/h] | 20.7 | 22.2 | 25.4 | 26.3 | 32.5 | 30.7 | — | 40.3 |
| v_ave w/ stop [km/h] | 13.5 | 12.4 | 17.3 | 17.4 | 25.7 | 25.7 | — | 34.9 |
| p_stop | 35.0% | 44.3% | 31.9% | 33.9% | 20.7% | 16.4% | — | 13.4% |
| # stops/km | 4.9 | 5.1 | 3.2 | 3.1 | 1.8 | 2.0 | — | 0.72 |
| time [h] | 5.63 | 2.5 | 13.1 | 2.3 | 12.4 | 0.9 | — | 3.5 |
| distance [km] | 79.8 | 30.5 | 225.7 | 39.6 | 300.8 | 23.5 | — | 123.6 |
| a_pos_ave [m/s²] | 0.61 | 0.68 | 0.62 | 0.58 | 0.54 | 0.64 | — | 0.50 |
| p_acceleration | 30.4% | 34.8% | 34.8% | 33.4% | 38.3% | 39.0% | — | 23.6% |
| p_cruise | 37.2% | 34.5% | 29.7% | 40.0% | 29.4% | 26.8% | — | 58.9% |
| p_deceleration | 32.3% | 30.7% | 35.5% | 26.6% | 32.3% | 34.2% | — | 17.5% |

**Municipal utility, Construction, Coach:** could not be validated against in-use data (no representative vehicles in the WHDC database), except one coach example (insufficient for statistical validation).

**Table 17 (Key parameters — coach, municipal utility, construction)** — reproduced:

| Parameter | Coach | Municipal utility | Construction |
|---|---|---|---|
| v_05 [km/h] | 18.0 | 3.9 | 12.1 |
| v_10 [km/h] | 20.0 | 5.8 | 20.1 |
| v_15 [km/h] | 23.0 | 9.0 | 26.0 |
| v_50 [km/h] | 74.0 | 20.8 | 45.5 |
| v_85 [km/h] | 100.0 | 58.8 | 62.0 |
| v_90 [km/h] | 100.0 | 65.9 | 64.0 |
| v_95 [km/h] | 100.0 | 84.1 | 82.0 |
| v_ave w/o stop [km/h] | 68.2 | 30.0 | 46.3 |
| v_ave w/ stop [km/h] | 66.4 | 8.2 | 33.2 |
| p_stop | 2.7% | 72.8% | 28.2% |
| # stops/km | 0.04 | 5.8 | 1.1 |
| time [h] | 4.1 | 1.2 | 0.6 |
| distance [km] | 275.2 | 10.0 | 21.2 |
| a_pos_ave [m/s²] | 0.57 | 0.42 | 0.42 |
| p_acceleration | 4.0% | 34.5% | 35.4% |
| p_cruise | 94.0% | 51.3% | 47.0% |
| p_deceleration | 2.0% | 14.2% | 17.6% |

Findings: municipal utility & construction VECTO cycles show too-abrupt rural→motorway transitions; no reason found for the construction cycle's max speed being 3 km/h lower than other cycles with motorway sections; the VECTO coach cycle differs significantly from the single available WHDC coach vehicle (very high cruise % — plausibility questioned).

## 4.4. Standard Bodies and Trailers for VECTO

**Table 18 (Overview of standard body types)** — reproduced:

| Truck configuration | Reference body |
|---|---|
| 2-axle 4x2 rigid truck | Hard shell box: B1, B2, B3, B4 |
| 2-axle 4x2 rigid truck, tipper (sand/cement) | B5 (²) |
| 3-axle 6x2 rigid truck | Hard shell box: B6 |
| 3-axle 6x4/6x6 | Tipper (sand/cement): B7 (²) |
| 4-axle 8x2 rigid, construction | B8 (²) |
| 4-axle 8x4/8x6 | Tipper (sand/cement): B9 (²) |
| Semi-trailer | Hard shell box: S1; tipper sand/cement: S2 (²) |
| Trailer | Box body: T1 |
| EMS box body | Not defined yet |

Footnote (²): suggested **not** to require Cd×A tests for construction trucks (bodies vary greatly, low speeds mean minor aero impact) — instead use a generic Cd value + generic body/payload mass; "still under discussion."

### 4.4.2. Reference Standard Body Dimensions

**Table 19 (Main specifications of reference Box bodies, source VDA/CLCCR)** — reproduced:

| Parameter | Unit | B1 | B2 | B3 | B4 | B6 | ST1 | T2 |
|---|---|---|---|---|---|---|---|---|
| Body length | mm | 6200 | 7400 | 7450 | 7450 | 7820 | 13685 | 7820 |
| Width | mm | 2550 (all) | | | | | | |
| Height | mm | 2680 | 2760 | 2880 | 2980 | 2980 | 2850 | 2730 |
| # of pallets | — | 15 | 18 | 18 | 18 | 19 | 34 | 19 |
| Mass | kg | 1600 | 1900 | 2000 | 2100 | 2200 | 7500* | 5400* |

*Total mass including chassis and axles. Standard tipper bodies (B7, B9, ST2) were investigated but **not standardized** — variation deemed too large; two categories (half-pipe cross-section vs. square shape) identified; CFD used instead for a representative tipper body from two large manufacturers.

### 4.4.3. Mass of Tipper Bodies (Netherlands WIM study)

Method: Weighing-In-Motion (WIM) data from ~10 Netherlands motorway locations; vehicle configuration identified by axle phase-shift; empty mass cross-referenced via license plates against road-authority database. WIM accuracy: **±500 kg** per measurement, improved by averaging across 10 sites.

**Table 20 (tractor tipper semi-trailers)** — reproduced:

| Parameter | Value |
|---|---|
| Empty mass | 15,500 kg |
| Laden mass | 35,650 kg |
| # measurements | 11,394 |
| % of total measurements | 1.54% |

Average cargo load ≈ 20 tons.

**Table 21 (rigid tipper trucks)** — reproduced:

| | 2-axle | 3-axle | 4-axle |
|---|---|---|---|
| Empty mass | 8,600 kg | 12,450 kg | 17,500 kg |
| Laden mass | 13,900 kg | 20,600 kg | 24,600 kg |
| # measurements | 152 | 624 | 860 |
| % of total measurements | 0.02% | 0.08% | 0.12% |

Average cargo mass: 2-axle ≈5.3t, 3-axle ≈8t, 4-axle ≈7t (lower 4-axle load attributed to different usage profile). Note: 5-axle tipper trucks more common in the Netherlands but not included.

### 4.4.4. CFD Analysis of Standard Bodies/Trailers (FAT Semi-Trailer Study)

Purpose: (a) identify which construction details materially affect Cd×A (to standardize only what matters); (b) compute yaw-angle influence on aero drag for the cross-wind correction function used in VECTO; (c) participate in an ACEA CFD "round robin" for repeatability experience.

**CFD code:** commercial ANSYS Fluent (among others named as available: ANSYS CFX, AVL-Fire, Star-CD, PowerFlow, OpenFOAM).

**Base geometry:** a generic semi-trailer truck ("FAT-vehicle") provided by "Forschungsvereinigung Automobiltechnik" (FAT), CAD-modeled to represent common features across participating OEMs; a "cabover" tractor configuration.

**[Figure 23 description]:** multiple views of the FAT-vehicle geometry (tractor + box trailer), showing cabover cab, 2 tractor axles, mirrors, fuel tank, air reservoir, spare wheel, 3-axle box trailer with tool box and trailer legs.

**Mesh settings (per ACEA CFD working group recommendations):**
- Core mesh cell size: 160mm, halved per refinement level down to finest surface resolution 2.5mm (mirrors, cabin faces); max recommended surface cell size 30mm.
- 8 prism layers, max height 20mm, near-wall cell 1mm, targeting **y+ 30–300** wall-function range.
- Final mesh: ~133 million cells. **[Figure 24 description]:** refinement regions and cell sizes (80/40/20/10/160mm bands). **[Figure 25 description]:** symmetry-plane cut through the mesh.

**Table 22 (Simulation settings)** — reproduced:

| # | Description | Input |
|---|---|---|
| 1 | Simulation type | Steady-state |
| 2 | Turbulence model | k-epsilon Realizable |
| 3 | Wall function | Non-Equilibrium WF |

**Table 23 (Initial/boundary conditions)** — reproduced:

| # | Description | Input |
|---|---|---|
| 1 | Inlet BC – velocity | 90 km/h |
| 2 | Outlet BC – pressure | 101,325 Pa |
| 3 | Floor BC – sliding wall | 90 km/h |
| 4 | Wheels BC | Rotating walls, calculated velocity |
| 5 | Inlet turbulence degree | 1% |
| 6 | Inlet turbulence char. length | 10mm |
| — | Air density | 1.184 kg/m³ |
| — | Viscosity | 1.49×10⁻⁵ m²/s |
| — | Initial pressure (first run only) | 101,325 Pa |
| — | Initial velocity (first run only) | 0 m/s |

A coarse mesh (~5.5 million cells) was first solved to seed initial conditions for the fine-mesh runs (reduces convergence iterations).

**Nine investigated variants:** (1) original FAT vehicle (reference); (2) truck mirror modification; (3) trailer tool-box modification; (4) trailer wear-plate closed; (5) trailer box radius modification; (6) trailer under-floor closed; (7)-(9) cross-flow yaw angles β = 1.5°, 3°, 4.5° (vehicle speed 25 m/s constant; side-velocity per Table 24).

**Table 24 (Cross-flow input data)** — reproduced:

| Yaw angle [°] | 1.5 | 3.0 | 4.5 |
|---|---|---|---|
| x-velocity [m/s] | 25.0 | 25.0 | 25.0 |
| y-velocity [m/s] | 0.655 | 1.310 | 1.968 |
| Velocity magnitude [m/s] | 25.008 | 25.034 | 25.077 |

**Drag coefficient formula (Equation 1, also used in section 4.5.3):**
```
C_D = F_D / (0.5 × ρ × v² × A)
```
where F_D = drag force, ρ = air density, v = free-stream velocity, A = reference (frontal) area.

**[Figure 26–30 descriptions]:** side-by-side comparisons of original vs. modified geometry for: alternative mirror position (rotated ~90° near the window, creating a flat front surface — non-aerodynamic); reduced-height (by ~50%) trailer tool box; closed (joined) trailer wear-plate (originally two separate plates); box-corner radius increased from 50mm to ~80mm; closed trailer under-floor.

**[Figure 31 description]:** Bar chart of Δ Cd (absolute and %) for each design variant relative to the original FAT geometry: mirror +0.0167 (+3.84%); tool box −0.0029 (−0.66%); wear-plate −0.0068 (−1.56%); radius −0.0009 (−0.20%); under-floor −0.0046 (−1.06%).

**[Figure 32 description]:** Pressure-contour + velocity-streamline comparison, original vs. modified mirror position — shows a larger recirculation zone behind the modified mirror, explaining the drag increase.

**[Figure 33/34 descriptions]:** Cd ratio and Cd difference vs. yaw angle β — parabolic increase: β=1.5° → Cd/Cd0 = 1.0260 (+2.6%); β=3.0° → 1.1029 (+10.3%); β=4.5° → 1.2007 (+20.1%).

**Findings summary (verbatim conclusions):**
- Mirror position strongly affects Cd — original mirror position must be mandated for Cd×A tests.
- 50%-reduced tool-box height: −0.66% Cd — recommend defining tool-box position/size with e.g. ±10% tolerance (limited influence).
- Closed wear-plate: −1.56% Cd, second-largest effect after mirrors — recommend **closed wear-plate as standard** (easier to define "closed" than "open").
- Box-corner radius (50→80mm): minor influence — no detailed specification needed if within usual dimensions (<80mm); suggests further evaluation at 20mm radius.
- Under-floor: closed reduces Cd by 1.05% — since open under-floor is the typical/standard configuration, **open under-floor recommended as the standard**; detailed steel-frame definition deemed unnecessary.
- Cross-flow: ~20% Cd increase at β=4.5° vs. β=0° — confirms strong yaw sensitivity, supporting the need for a generic yaw-angle correction function in VECTO (see Part 4, Equations 4–8).

## 4.5. Alternative Bodies and Trailers (Tanker Semi-Trailers)

Alternative body types distinguished for both semi-trailer and rigid-truck configurations: swap body (incl. container), dry bulk tanker, wet bulk tanker, other (e.g., flat bed).

### 4.5.1. Identifying a Representative Alternative Group

From LOT 2 CO2 projections: ~60% of HDV energy consumption is from tractor-semi-trailer configs, dominated (80%) by 4x2 tractors. **[Figure 35 description]:** bar/pie chart of new semi-trailer registrations in EU27 (2008) by body type — curtain-siders and box vans dominate. Refrigerated/container/most swap-body trailers geometrically resemble the standard box body (not separately studied). Tipper already covered as a standard body; "other" too heterogeneous to generalize. → **Dry bulk and wet bulk tanker semi-trailers** selected for CFD comparison (geometrically very different from box bodies).

### 4.5.2. Tanker Dimensions and Mass

**Table 25 (WIM mass data, tanker semi-trailers, NL)** — reproduced:

| Parameter | Value |
|---|---|
| Empty mass | 15,500 kg |
| Laden mass | 32,400 kg |
| # measurements | 58,403 |
| % of total measurements | 7.90% |

(Dry and wet bulk not separable in this dataset.) Average cargo load ≈17 tons.

**Table 26 (Dry bulk tanker semi-trailer dimensions)** — reproduced:

| Parameter | Unit | External |
|---|---|---|
| Length | mm | 13,150 |
| Vessel diameter | mm | 2,550 |
| Height, unloaded | mm | 3,990 |
| 5th-wheel height, loaded | mm | 1,150–1,200 |
| Distance mid-axle to trailer end | mm | 4,125 |
| Axle distance | mm | 1,310 |
| Volume | m³ | 60 |
| GVM | kg | 40,000 |
| Axle load | kg | 27,000 |
| Empty mass | kg | ±8,000 (range 5,700–10,000 per Dutch registrations) |

**Table 27 (Wet bulk tanker semi-trailer dimensions)** — reproduced:

| Parameter | Unit | External |
|---|---|---|
| Length | mm | 11,000 |
| Vessel diameter | mm | 2,550 |
| Height, unloaded | mm | 3,800 |
| 5th-wheel height, loaded | mm | 1,150–1,200 |
| Distance mid-axle to trailer end | mm | 3,350 |
| Axle distance | mm | 1,310 |
| Volume | liter | 38,000 |
| GVM | kg | 39,000 |
| Axle load | kg | 27,000 |
| Payload | kg | ±8,000 (range 5,700–10,000) |

Both tanker models were mated to the same FAT tractor as the box-body reference for controlled comparison. Dry bulk trailer set at ±1.2° tilt, 230mm cab-to-trailer gap ("rather optimal," per one large fleet owner). Wet bulk trailer set at ±1.0° tilt, ~1000mm cab-to-trailer gap (larger due to mass distribution/axle-load constraints).

### 4.5.3. CFD Results for Tanker Trailers

Mesh/BC settings identical methodology to section 4.4.4 (Tables 28/29 mirror Tables 22/23). Six variants: Trailer A (dry bulk) and Trailer B (wet bulk), each at yaw angles 0°, 1.5°, 3.0° (Table 30 mirrors Table 24 for two angles).

**[Figure 41/42 descriptions]:** vehicle-surface pressure contours, dry bulk (Trailer A) vs. wet bulk (Trailer B).
**[Figure 43/44 descriptions]:** velocity-contour domain cuts — larger tractor-to-trailer gap visible for Trailer B (wet bulk) vs. Trailer A (dry bulk), explaining B's higher drag.
**[Figure 45/46 descriptions]:** Cd ratio and Cd×A ratio vs. yaw angle, tanker trailers relative to the FAT standard box semi-trailer — same parabolic trend as the box-body case; Cd×A ratio slightly smaller than Cd ratio because tanker frontal area is slightly smaller than box-body frontal area.

**Conclusions (verbatim, numbered):**
1. Dry and wet bulk tanker Cd×A is **~11–13% higher** than the standard box semi-trailer.
2. Same parabolic yaw-angle behaviour as box-body configuration.
3. Higher tanker drag attributed to (a) brackets/accessories (boxes, hoses, manholes, railings) and (b) larger tractor-cab-to-trailer-front gap.
4. Wet bulk tanker Cd×A is ~1.3% higher than dry bulk (larger cab-trailer gap).
5. The tanker-vs-box difference narrows to ~10% at the highest yaw angle (roundish tank-front shape recaptures some of the gap-induced loss at higher yaw).
6. A **first default Cd×A value of +12%** (vs. standard box semi-trailers) can be derived, pending validation with different CFD codes and/or road measurements before legislative use.

### 4.5.3.5. Recommendations for Alternative-Body Handling in Future Legislation

Proposed option (verbatim structure): alternative bodies/trailers optionally tested via the standard Cd×A test procedure (default values available to limit small-builder test burden); body builder can test just their body/trailer if a same-vehicle-configuration standard-body Cd×A result is available from the vehicle manufacturer; percent change in Cd×A vs. standard is computed; a **generic look-up table** (built from VECTO simulation runs across HDV classes) converts % change in Cd×A and % mass change into % change in fuel consumption/CO2 — incentivizing more aerodynamic, lighter bodies/trailers.

## 4.6. Aggregated Vehicle Validation Procedure (SiCo Test)

**Purpose:** an independent, lower-burden check of a certified vehicle's declared CO2 result **without requiring access to proprietary component test data** (e.g., manufacturer engine maps), which independent labs / type approval authorities typically cannot access.

**Concept:** VECTO's declaration mode simulates, in parallel to the CO2 test cycle, a **"SiCo" (Simplified Constant Speed) test** — target speeds strung together per HDV class. The predicted wheel power and fuel consumption at these constant speeds are exported by VECTO. The vehicle is then physically driven at these same constant speeds (test track, or optionally chassis dyno for checking engine/transmission efficiency), and results compared to VECTO's SiCo predictions — flagging large deviations for further investigation, **without exposing proprietary component data.**

**Table 31 (Constant speed phases for SiCo per CO2 test cycle)** — reproduced (✕ = phase included):

| Mission profile | 0 (idle) | 30 | 50 | 60 | 85 | 100 |
|---|---|---|---|---|---|---|
| Long haul | | | | ✕ | ✕ | |
| Regional delivery | | | | ✕ | ✕ | |
| Urban delivery | | | | ✕ | ✕ | |
| Municipal | | | | ✕ | ✕ | |
| Construction | | | | ✕ | ✕ | |
| City bus | | | | ✕ | ✕ | |
| Coach | | | | ✕ | ✕ | |

*(Note: exact ✕ placement per column in the OCR'd source table was ambiguous — reproduced with the general structure; the source explicitly notes idling is included for indicator purposes despite auxiliary-driven inaccuracy at idle, and all details were "open yet" pending the proof-of-concept phase.)*

**Table 32 (Example SiCo output table)** — reproduced as printed:

| Phase | Gear | P-wheel [kW] | FC [g/h] | FC [g/kWh] | Time [s] |
|---|---|---|---|---|---|
| Idling | — | 0 | 0.0 | 1808.6 | — |
| 60 const | 6 | 51.0 | 12413.6 | 243.4 | — |
| 85/0% const | 8 | 101.5 | 22557.2 | 222.2 | — |
| 85/0.5% const | 7 | 140.8 | 29802.2 | 211.7 | — |
| accel 60–85 | start in 6 | 250.7 | — | — | 28 |
| accel 30–85 | start in 3 | 251.2 | — | — | 53 |
| **Total** | | **41.8** | **15938.9** | **381.4** | **626** |

Footnotes: acceleration phases only included if test track/equipment permit; higher accuracy expected for single constant-speed phases than the total-cycle result; overall FC value affected by test-tire RRC, wind, temperature — applicability "needs further evaluation."

### 4.6.2–4.6.3. SiCo Field Test & Evaluation

Test conditions (verbatim, several with placeholders marked "open"): HDV equipped as declared; total mileage between placeholder values "aa and bb" km; tire tread depth ≥80% of new; no added aero-affecting equipment. Test setup follows the Cd×A test procedure (chapter 4.2.3) with extensions: on-board FC measurement; clearly marked distance points for target-speed changes; full-load acceleration or defined braking (−0.5 or −1 m/s²) between speed levels; wind/gradient recording and calibration per aero-test standards.

**Evaluation formulas:**
```
P_wheel [kW] = Md × Rotational_speed × 2π / 1000
FC [g/h] = FC [g/s] × 3600
FC [g/kWh] = FC [g/h] / P_wheel [kW]
```
Md = average torque over 10–60s window, starting ≥15s after reaching each target speed. Time = timestamp target speed first reached within 2% minus timestamp previous target speed left by >2% (thresholds noted as placeholders).

**Table 33 (Tolerances, all noted as "placeholders")** — reproduced:

| Phase | P-wheel | FC [g/h] | FC [g/kWh] | Time |
|---|---|---|---|---|
| Idling | – | – | – | – |
| 60 const | 7% | – | 4% | – |
| 85/0% const | 7% | – | 4% | – |
| 85/0.5% const | 7% | – | 4% | – |
| accel 60–85 | – | – | – | 10% |
| accel 30–85 | – | – | – | 10% |
| Total | – | – | 7% | – |

**Deviation-response logic (verbatim):** if P-wheel tolerance exceeded → check tires match certification, wind/gradient boundary conditions, aero condition (body/trailer/accessories); repeat test if error found; else escalate Cd×A / tire-RRC component tests for a quality check. If FC [g/kWh] tolerance exceeded → check gear usage, auxiliary status/battery charge, repeat; else escalate gearbox/axle/engine component tests for a quality check.

Status at report date: SiCo test in "early development phase" — a planned autumn 2013 bus application failed due to a damaged wheel-rim torque meter; repeated end of March 2014, evaluation ongoing. Recommended for further development in a follow-up project.

## 4.7. Sensitivity Analysis for Input Data

Purpose: quantify how measurement-procedure accuracy for each vehicle-specific input parameter propagates into overall fuel-consumption uncertainty. Auxiliary parameters were **not** varied (generic-only at this stage). Driver-assistance systems (eco-roll, engine stop-start) flagged for future sensitivity work once parameters agreed with industry.

### 4.7.1. Reference Vehicles

**Table 34 (Reference vehicles for sensitivity analysis)** — reproduced:

| Vehicle | Rated power [kW] | Total weight [t] | Cd×A [m²] | RRC [kg/kg] |
|---|---|---|---|---|
| 4x2 Rigid Truck, 12t max GVW | 185 | 9.9 | 5.28 | 0.0094 |
| 4x2 Tractor & Semitrailer, 40t max GVW | 350 | 33.9 | 6.30 | 0.0055 |
| 6x2 Coach, 24t max GVW | 350 | 19.0 | 3.26 | 0.0064 |

Mission profiles tested: 12t rigid — long haul, regional delivery, urban delivery; 40t tractor — long haul, regional delivery; coach — coach cycle. These reference vehicle input datasets were slated for distribution with the VECTO code itself (with OEM-identifying details anonymized).

### 4.7.2. Parameter Variation Ranges

- **Cd×A:** ±3% (baseline 6.30 m² → range 6.11–6.49 m²), based on the aero-test repeatability/reproducibility analysis plus expectation that OEMs will retest/select best result.
- **Rolling resistance:** ±0.3 [kg/t] absolute (per COP tolerance in EC 1235/2011).
- **Fuel consumption map**, two scenarios:
  - (a) "Worst case" per ECE R49.06 linearity tolerances: engine speed ×1.02, engine torque ×1.02, fuel flow ×0.98 or (reference − 0.3% max fuel flow), whichever higher (mirrored for "high FC" version); full-load torque/drag curve adjusted accordingly.
  - (b) TUG test-equipment standards: engine speed tolerance neglected (rotation-angle sensor); torque = 0.3% of full scale; fuel flow = 0.12% of full scale.
- **Transmission/axle loss maps:** ±0.3 [Nm], varied in separate scenarios.

### 4.7.3. Results

**[Figures 48–50 descriptions]:** FC change (%) for ±3% Cd×A, for the 12t rigid, 40t tractor, and 24t coach respectively, across their mission profiles.
- Highest sensitivity: 12t rigid truck, long-haul mission, **±1.4%** FC change.
- Coach: low sensitivity despite high average speed, due to lower baseline Cd×A and higher baseline auxiliary load.
- 40t truck, Regional Delivery: **non-linear** (+0.3%/−0.7%) due to gear-shift-behaviour changes triggered by the parameter change.

**[Figures 51–53 descriptions]:** FC change for ±0.3 kg/t RRC. Highest sensitivity: **40t truck, ±1.5%**; lower for the lighter vehicles (RRC effect scales with weight). 40t truck again shows non-linearity in Regional Delivery from gear-shift effects.

**[Figures 54–56 descriptions]:** FC map variation scenarios (350kW engine, 40t truck & 24t coach only). "Test equipment tolerances" scenario: overall FC variation **±1%** (coach ±1.2%, long-haul truck ±0.8%) — attributed to different load-point distributions in the engine map between applications. "ECE R49 worst case" scenario (40t long-haul truck): FC variation up to **±4.5%** — explicitly called "not appropriate for the HDV CO2 certification," motivating a push for stricter accuracy provisions than EURO VI/ECE R49.06.

**[Figures 57–59 descriptions]:** FC change for ±0.3 Nm transmission/axle loss torque — impact on overall FC "nearly negligible" across all three vehicles.

### 4.7.4. Conclusions

- ECE R49.06 accuracy provisions for engine speed/torque/FC are **not sufficient** as the basis for HDV CO2 legislation; stricter test-equipment standards already exist and should be adopted; broad tolerances "might be misused by OEMs to cheat" (verbatim characterization of the risk).
- Aero (Cd×A) accuracy of ±3% judged sufficient for the overall FC result given method complexity, pending confirmation from ongoing measurements.
- Rolling resistance: OEM-independent factors (road surface, rain, snow) create larger real-world variability than the RRC test-procedure tolerance (0.3 kg/ton), which the report says "has to be accepted at the time being," though it may not suffice for precise tire ranking.
- Transmission/axle test tolerances have negligible influence on overall CO2 result.
- ACEA announced (2014) a parallel sensitivity study; early industry feedback suggested **larger** uncertainty ranges than found here.

## 4.8. Proof of Concept

Five vehicles investigated: (1) class 5 long-haul truck (40t GVW); (2) class 4 rigid truck (18t GVW); (3) class 2 rigid truck (12t GVW); (4)+(5) coach and citybus (analysis not finalized at report date).

**Constant-speed test-track comparisons:** wheel power simulated by VECTO to within **<1%** deviation when actual test conditions (wind, tire-specific RRC) were input; up to **±5%** deviation if generic/nominal conditions used instead. FC/CO2 simulated within **±1%** when auxiliary operation was also specified precisely.

**Real-world on-road comparisons (rural + motorway):** driver-model refinements were identified from discrepancies (subsequently implemented in VECTO). After correction, simulated FC vs. real-world measurement was within **±3%** (often ±1.5%), compared against a real-world measurement variability of σ≈2% and the precedent that EU passenger-car CO2 declaration already accepts a ±3% margin — used to justify that "a future certification scheme can be based on the proposed approach."

**Chassis dynamometer comparisons:** WHVC and FIGE cycles (baseline speed profiles for WHTC/ETC transient engine cycles) plus the draft regional-delivery CO2 cycle were run on the JRC HDV chassis dyno. Full-cycle deviations: **±3%** (within measurement uncertainty). Sub-cycle deviations: **±5%**. Regional-delivery cycle: markedly worse, **±10%**, attributed to uncertain wheel-load conditions on the dyno and auxiliary operation uncertainty.

**Vehicle 3 (12t delivery truck), preliminary 2014 result:** VECTO **underestimated** measured urban real-world FC by **5%**.

**Vehicles 4/5 (coach, citybus):** no comparison data available yet — the VECTO Automatic Transmission (AT) model was not due until June 2014, and bus-specific auxiliary models were being developed in a parallel project.

## 4.9. Test Program in LOT 3

**Table 35 (Tests performed by TUG within LOT3)** — reproduced:

| Test days | Test procedure | Tasks | Dates |
|---|---|---|---|
| 8 | On-board measurements | Cd×A test procedure and SiCo test, with Daimler and EvoBus | 28–30 Nov 2013 (aborted, torquemeter failure); 31 Mar–4 Apr 2014 (valid tests) |
| 4 | Engine test procedure | Fuel flow map and WHTC on a EURO VI HDE | 11–14 Feb 2013 |
| 2 | Anemometer calibration | Chassis-dyno test of on-board anemometer calibration options | 27–28 Jun 2013 (found: anemometer position cannot be accurately calibrated on the test stand) |
| 6 | Chassis dyno tests | Measure auxiliary engagement | 16–18 Jan 2013 (add-on to another project's emission-factor tests; data used for generic database/vehicle models) |

A planned "pilot phase" involving type approval authorities was **not started** within LOT3, since OEM/supply-industry/technical-service/type-approval responsibilities had not yet been legally settled. Remaining budget was redirected to further developing the generic Automatic Transmission (AT) model (only a manufacturer-specific option had existed before).

---

*(Continued in Part 4: VECTO Software Architecture and Simulation Equations, and VECTO-CSE Evaluation Tool)*
