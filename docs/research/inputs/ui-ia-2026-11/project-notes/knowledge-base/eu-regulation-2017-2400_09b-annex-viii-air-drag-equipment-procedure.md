# Annex VIII — Verifying Air Drag Data: Measurement Equipment, Constant Speed Test Procedure, Misalignment Calibration, Testing Template, Data Processing

**Source document:** Commission Regulation (EU) 2017/2400 (consolidated text, EUR-Lex)
**CELEX number:** 02017R2400
**Consolidation date:** 01.01.2026 (consolidated version 007.001)
**Range covered in this file:** Annex VIII, Sections 3.4–3.8 (source lines 13765–14209; page markers 334–344)
**Amendment markers:** ►B = original 2017 baseline; ►M1 = Reg (EU) 2019/318; ►M2 = Reg (EU) 2020/1181; ►M3 = Reg (EU) 2022/1379; ►M4 = Reg (EU) 2025/258.

---

## 3.4 Measurement equipment (▼B)

The calibration laboratory shall comply with the requirements of either **►M3 IATF ◄ 16949**, **ISO 9000 series**, or **ISO/IEC 17025**. All laboratory reference measurement equipment used for calibration and/or verification shall be traceable to national (international) standards.

### 3.4.1 Torque

**3.4.1.1.** Direct torque at all driven axles shall be measured with one of the following systems:
a. Hub torque meter
b. Rim torque meter
c. Half shaft torque meter

**3.4.1.2. System requirements for a single torque meter, by calibration (▼M3):**

| Requirement | Heavy lorries & heavy buses | Medium lorries |
|---|---|---|
| (i) Non-linearity | < ± 6 Nm | < ± 5 Nm |
| (ii) Repeatability | < ± 6 Nm | < ± 5 Nm |
| (iii) Crosstalk (rim torque meters only) | < ± 10 Nm | < ± 8 Nm |
| (iv) Measurement rate | ≥ 20 Hz | ≥ 20 Hz |

Definitions:
- **'Non-linearity'** means the maximum deviation between ideal and actual output signal characteristics in relation to the measurand in a specific measuring range.
- **'Repeatability'** means closeness of the agreement between the results of successive measurements of the same measurand carried out under the same conditions of measurement.
- **'Crosstalk'** means signal at the main output of a sensor (My), produced by a measurand (Fz) acting on the sensor, which is different from the measurand assigned to this output. Coordinate system assignment is defined in accordance with **ISO 4130**.

The recorded torque data shall be **corrected for the instrument error** determined by the supplier.

### 3.4.2 Vehicle speed (▼B)

Vehicle speed is determined by the air drag pre-processing tool based on the **CAN-bus front axle signal**, calibrated using either:

- **Option (a):** a reference speed calculated by a delta-time from two fixed opto-electronic barriers (see 3.4.4) and the known length(s) of the measurement section(s); or
- **Option (b):** a delta-time-determined speed signal from the position signal of a DGPS and the known length(s) of the measurement section(s), derived by the DGPS coordinates.

For vehicle speed calibration, the data recorded during the **high speed test** are used.

### 3.4.3 Reference signal for rotational speed of wheels at the driven axle (▼M3)

One of three options shall be selected:

**Option 1: Engine speed based**
The CAN engine speed signal together with transmission ratios (gears for low speed test and high speed test, axle ratio) shall be made available. It must be demonstrated that the CAN engine speed signal fed to the pre-processing tool is **identical** to the signal used for in-service testing under Annex I to **Regulation (EU) 582/2011**.

For vehicles with a torque converter unable to drive the low speed test with closed lock-up clutch under Option 1, additionally the cardan shaft speed signal and axle ratio, or the average wheel speed signal for the driven axle, shall be provided. It must be demonstrated that the engine speed calculated from this additional signal is within **1 %** of the CAN engine speed, for the average value over a measurement section driven at the lowest possible speed in torque-converter-locked mode and at the applicable high-speed-test speed.

**Option 2: Wheel speed based**
The average of the CAN signals for rotational speed of left and right wheel at the driven axle shall be made available. External sensors may alternatively be used. Any method shall fulfil the requirements in **Table 2 of Annex Xa** (external cross-reference — not in this extraction range).

Following Option 2, the input parameters for gear ratios and axle ratio shall be set to **1**, independent of powertrain configuration.

**Option 3: Electric motor speed based**
For hybrid and fully electric vehicles, the CAN electric motor speed signal together with transmission ratios (gears for low and high speed test, and axle ratio if applicable) shall be made available. It must be demonstrated that the driven-axle wheel speed in the low and high speed tests is defined **solely** by these powertrain configuration specifications.

### 3.4.4 Opto-electronic barriers (▼B)

The barrier signal shall be made available to the pre-processing tool for triggering the begin/end of the measurement section and calibrating the vehicle speed signal. Trigger signal measurement rate: **≥ 100 Hz**. Alternatively a DGPS system can be used.

### 3.4.5 (D)GPS system (▼B)

**Option a) — position measurement only: GPS**
Required accuracy:
i. Position: **< 3 m, 95 % Circular Error Probable**
ii. Update rate: **≥ 4 Hz**

**Option b) — vehicle speed calibration and position measurement: Differential GPS (DGPS)**
Required accuracy:
i. Position: **0,15 m, 95 % Circular Error Probable**
ii. Update rate: **≥ 100 Hz**

### 3.4.6 Stationary weather station (▼B)

Ambient pressure and humidity are determined from a stationary weather station, positioned:
- at a distance **< 2 000 m** from one of the measurement areas, and
- at an altitude **≥** that of the measurement areas.

Required accuracy:
i. Temperature: **± 1 °C**
ii. Humidity: **± 5 % RH**
iii. Pressure: **± 1 mbar**
iv. Update rate: **≤ 6 minutes**

### 3.4.7 Mobile anemometer (▼B)

A mobile anemometer measures air flow conditions: air flow velocity and yaw angle (β) between total air flow and vehicle longitudinal axis.

**3.4.7.1. Accuracy requirements (▼M3)**

The anemometer shall be calibrated in a facility according to **ISO 16622**.

**Table 1 — Anemometer accuracy requirements**

| Air speed range [m/s] | Accuracy air speed [m/s] | Accuracy yaw angle in yaw angle range of 180 ± 7 degrees [degrees] |
|---|---|---|
| 20 ± 1 | ± 0,7 | ± 1,0 |
| 27 ± 1 | ± 0,9 | ± 1,0 |
| 35 ± 1 | ± 1,2 | ± 1,0 |

**3.4.7.2. Installation position (▼M3)**

(i) **X position:**
- Medium and heavy rigid lorries and tractors: front face **± 0,3 m** of the semi-trailer or box-body.
- Heavy buses: between the end of the front quarter of the vehicle and the rear end of the vehicle.
- Medium van lorries: between B-pillar up to the rear end of the vehicle.

(ii) **Y position:** plane of symmetry within a tolerance **± 0,1 m**.

(iii) **Z position:** installation height above the vehicle = **one third of total vehicle height** measured from the ground, tolerance **0,0 m to + 0,2 m**. For vehicles with total height above 4 m, on manufacturer's request the installation height above the vehicle can be limited to **1,3 m**, tolerance **0,0 m to + 0,2 m**.

The instrumentation shall be done as accurately as possible using geometrical or optical aids. Any remaining misalignment is subject to the misalignment calibration in 3.6.

**3.4.7.3. (▼B)** Anemometer update rate: **4 Hz or higher**.

### 3.4.8 Temperature transducer for ambient temperature on vehicle (▼B)

Ambient air temperature shall be measured on the pole of the mobile anemometer. Installation height: maximum **600 mm** below the mobile anemometer. Sensor shall be shielded from the sun.
Required accuracy: **± 1 °C**. Update rate: **≥ 1 Hz**.

### 3.4.9 Proving ground temperature (▼B)

Proving ground temperature shall be recorded on the vehicle via a contactless **IR sensor**, wideband **8 to 14 μm**. For tarmac and concrete, an **emissivity factor of 0,90** shall be used.

**►M3** The IR sensor shall be calibrated in accordance with **ASTM E2847** or **VDI/VDE 3511**. ◄

Required accuracy at calibration: Temperature **± 2,5 °C**. Update rate: **≥ 1 Hz**.

---

## 3.5 Constant speed test procedure (▼B)

On each applicable combination of measurement section and driving direction, the constant speed test procedure (low speed, high speed, low speed sequence as specified below) shall be performed **in the same direction**.

### 3.5.1 Low speed test target
Average speed within a measurement section: **10 to 15 km/h**.

### 3.5.2 High speed test target (▼M4)

| | Medium & heavy lorries | Heavy buses |
|---|---|---|
| Maximum speed | 92 km/h | 102 km/h |
| Minimum speed | 87 km/h | 97 km/h |

If the vehicle cannot reach this speed, the minimum speed shall equal **3 km/h less than the maximum vehicle speed the vehicle can be operated at on the test track**.

### 3.5.3 Testing sequence (▼B)

The testing shall be performed strictly according to the sequence in 3.5.3.1 to 3.5.3.9.

#### 3.5.3.1 Preparation of vehicle and measurement systems

(i) Installation of torque meters on driven axles; check installation and signal data against manufacturer specification.
(ii) Documentation of relevant general vehicle data for the official testing template (see 3.7).
(iii) For the acceleration correction calculation by the pre-processing tool, the actual vehicle weight shall be determined before the test within **± 500 kg**.
(iv) Check tyres for maximum allowable inflation pressure; document tyre pressure values.
(v) Prepare opto-electronic barriers at the measurement section(s), or check proper function of the DGPS system.
(vi) Install mobile anemometer on the vehicle and/or control installation, position and orientation. **►M3** A misalignment calibration test must be performed every time the anemometer is newly mounted or adjusted. ◄
**▼M3** (vii) Check vehicle setup regarding height and geometry, in standard ride height position:
- **▼B** Medium and heavy rigid lorries and tractors: maximum height determined by measuring at the four corners of the box body/semi-trailer.
- **▼M4** Heavy buses and medium lorries of van chassis configuration: maximum height measured in accordance with the technical requirements of **Regulation (EU) 2021/535**, excluding devices and equipment referred to in Appendix 1.
(viii) Adjust the semi-trailer height to the target value and redo the maximum-vehicle-height determination if necessary.
(ix) Mirrors or optical systems, roof fairing or other aerodynamic devices shall be in their regular driving condition.

#### 3.5.3.2 Warm-up phase (▼B, with ▼M1 addition)

Drive the vehicle a minimum of **90 minutes** at the high-speed-test target speed to warm up the system. A repeated warm-up (e.g. after a configuration change or an invalid test) shall be at least as long as the standstill time. The warm-up phase can be used to perform the misalignment calibration test (3.6).

**▼M1**
If it is not possible to maintain high speed for a complete round (e.g. curves too narrow), deviation from the target speed is allowed during curves, including the nearby straight portions needed for slowing down/accelerating. Deviations shall be minimised as far as possible.

Alternatively, the warm-up phase may be performed on a nearby road if the target speed is maintained within **± 10 km/h for 90 % of the warm-up time**. The portion of warm-up spent driving from the road to the standstill area for zeroing the torque meters shall be included in the warm-up phase described in point 3.5.3.4, and shall **not exceed 20 minutes**. Speed and time during warm-up shall be recorded by the measurement equipment.

#### 3.5.3.3 Zeroing of torque meters (▼B)

i. Bring the vehicle to a standstill.
ii. Lift the instrumented wheels off the ground.
iii. Perform zeroing of the amplifier reading of the torque meters.

**▼M3** The standstill phase shall not exceed **15 minutes**.

#### 3.5.3.4 Second warm-up phase (▼M1)

Drive another warm-up phase of **minimum 10 minutes**, plus (if applicable) the driving time from the road to the standstill area for torque meter zeroing, at the high-speed-test target speed. **►M3** This warm-up phase shall not be shorter than the standstill phase and shall **not exceed 30 minutes**. ◄

**▼M3**
Any use of the mechanical service brake during the parts of the test set out in this point and in 3.5.3.5 **invalidates the whole test**. If specific vehicle settings are required to avoid service brake activation during these parts, the manufacturer shall, upon request, provide the approval authority, the Commission, a market surveillance authority, or a third party complying with **Regulation (EU) 2022/163**, with the details of these settings so the test can be reproduced independently of the manufacturer.

#### 3.5.3.5 First low speed test (▼B)

Perform the first measurement at low speed, ensuring:
i. The vehicle is driven through the measurement section along a straight line as straight as possible.
ii. Average driving speed is per 3.5.1 for the measurement section and preceding stabilisation section.
iii. Driving speed stability inside measurement/stabilisation sections per 3.10.1.1 item vii.
iv. Measured torque stability inside measurement/stabilisation sections per 3.10.1.1 item viii.
v. Beginning and end of measurement sections clearly recognisable via a recorded trigger signal (opto-electronic barriers + recorded GPS data) or via DGPS.
vi. Driving outside the measurement/stabilisation sections performed without delay; unnecessary manoeuvres (e.g. sinuous driving lines) avoided.

**▼M4**
vii. The maximum time for the low speed test shall **not exceed 25 minutes**, to prevent tyre cool-down.

#### 3.5.3.6 Another warm-up (▼B)

Drive another warm-up phase of **minimum 5 minutes** at the high-speed-test target speed.

#### 3.5.3.7 High speed test (▼B, with ▼M4 addition)

Perform the measurement at high speed, ensuring:
i. Vehicle driven through the measurement section along a straight line as straight as possible.
ii. Average driving speed per 3.5.2.
iii. Driving speed stability per 3.10.1.1 item vii.
iv. Measured torque stability per 3.10.1.1 item viii.
v. Beginning/end of measurement sections clearly recognisable (trigger signal + GPS, or DGPS).
vi. Unnecessary manoeuvres avoided outside measurement/stabilisation sections (sinuous lines, unneeded accel/decel).
vii. Distance between the measured vehicle and another driven vehicle on the test track: **at least 500 m**.
viii. **At least 10 valid passings per heading** are recorded.

The high speed test can also be used to determine anemometer misalignment if the provisions in 3.6 are fulfilled.

#### 3.5.3.8 Second low speed test (▼M4)

Perform the second low-speed measurement **directly after** the high speed test. The same provisions as the first low speed test apply.

#### 3.5.3.9 Drift check of torque meters (▼B)

Directly after finalising the second low speed test:
1. Bring the vehicle to standstill.
2. Lift the instrumented wheels off the ground.
3. The drift of each torque meter, calculated from the average of the minimum sequence of **10 seconds**, shall be **less than 25 Nm**. Exceeding this limit invalidates the test.

---

## 3.6 Misalignment calibration test (▼B)

The anemometer's misalignment shall be determined by a dedicated test on the test track.

**3.6.1.** At least **5 valid passings** of a **250 ± 3 m** straight section, driven in each direction at high vehicle speed, shall be performed.

**3.6.2.** The wind-condition validity criteria of 3.2.5 and the track criteria of 3.1 apply.

**3.6.3.** The recorded data is used by the pre-processing tool to calculate the misalignment error and perform the corresponding correction. **►M3** The signals for wheel torques and engine/cardan/average wheel speed are **not used** in this evaluation. ◄

**3.6.4.** The misalignment calibration test can be performed independently of the constant speed test procedure. If performed separately:
i. Prepare the opto-electronic barriers at the 250 ± 3 m section, or check DGPS function.
ii. Check vehicle setup (height/geometry) per 3.5.3.1; adjust semi-trailer height per Appendix 4 if necessary.
iii. No warm-up prescriptions apply.
iv. Perform the test by at least 5 valid passings as described above.

**3.6.5.** A new misalignment test shall be performed in the following cases:
a. The anemometer has been dismounted from the vehicle.
b. The anemometer has been moved.
**▼M3** c. A different tractor or rigid lorry is used.
**▼M1** d. The air drag family has been changed.

---

## 3.7 Testing Template (▼B)

In addition to recording modal measurement data, the testing shall be documented in a template containing at least:
i. General vehicle description (per Appendix 2 — Information Document).
ii. Actual maximum vehicle height per 3.5.3.1 item vii.
iii. Start time and date of the test.
iv. Vehicle mass within a range of **± 500 kg**.
v. Tyre pressures.
vi. Filenames of measurement data.
vii. Documentation of extraordinary events (with time and measurement-section number), e.g.:
 - close passing of another vehicle
 - manoeuvres to avoid accidents, driving errors
 - technical errors
 - measurement errors

---

## 3.8 Data processing (▼B)

**3.8.1.** Recorded data shall be synchronised and aligned to **100 Hz** temporal resolution, by arithmetical average, nearest neighbour, or linear interpolation.

**3.8.2.** All recorded data shall be checked for errors. Measurement data shall be **excluded** from further consideration in the following cases:
- Datasets became invalid due to events during measurement (see 3.7 item vii).
- Instrument saturation during measurement sections (e.g. high wind gusts causing anemometer signal saturation).
- Measurements where the permitted torque meter drift limits were exceeded.

**3.8.3.** Evaluation of constant speed tests shall use the **latest available version** of the air drag pre-processing tool. Besides the data processing above, all evaluation steps including validity checks (with the exception of the list above) are performed by the pre-processing tool.

---

## Cross-references used in this section

- Annex Xa, Table 2 — requirements for alternative wheel-speed measurement methods (external, not in this extraction range)
- Regulation (EU) 582/2011, Annex I — in-service testing engine speed signal requirements (external)
- Regulation (EU) 2021/535 — technical requirements for vehicle height measurement, buses/vans (external)
- Regulation (EU) 2022/163 — market surveillance / third-party test reproduction (external)
- ISO 4130, ISO 9000 series, ISO/IEC 17025, ISO 16622, IATF 16949, ASTM E2847, VDI/VDE 3511 — referenced standards (external, not reproduced)
- Appendix 1, 2, 4 — see files `09d`/`09f`

## Figures referenced but not visually extracted

None identified as explicit figure callouts in this file's range (no "Figure X" labels appear in sections 3.4–3.8).
