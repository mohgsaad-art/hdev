# Charger standards & protocols (pass 4)

Plain English. These are the standards that govern charger behaviour — the
connectors, the vehicle↔charger handshake, and the charger↔backend link. Every
value has a source. `[V]` = opened the primary datasheet; `[C]` = secondary/snippet.

## 1. Connectors and power classes

| Connector | Typical power | Voltage | Classes | Note |
|---|---|---|---|---|
| Type 2 (IEC 62196) AC | 3.7–22 kW | 230/400 V AC | cars, vans | home/destination; onboard charger limits the real rate |
| CCS2 (Combo 2) DC | 50–400 kW (up to ~500) | up to ~1000 VDC | cars, vans, trucks | Europe DC standard; up to 500 A (600 A boost) |
| CHAdeMO DC | 50–200 kW | up to ~500 VDC | legacy | being phased out in EU |
| NACS / Tesla DC | up to 500 kW (V4) | 400–1000 V | cars, vans | Tesla standard, now opening up |
| **MCS (SAE J3271)** DC | **440 kW–3.75 MW** | **up to 1250 VDC** | **trucks, buses** | **3000 A actively cooled** `[C]` (Argonne FAQ, CharIN) |

Key MCS figure `[C]`: the MCS standard is designed "from 440kW (350A/1250vdc
non-cooled) up to 3.75MW (3000A/1250vdc actively cooled)" — Argonne National Lab
MCS FAQ (2023). CharIN (via InsideEVs 2022) states "maximum current of 3,000 A
(3 kA) at up to 1,250 V". MCS is still finalising; products in 2025–26 run
~1 MW–1.2 MW, not the full 3.75 MW.

## 2. Vehicle ↔ charger communication (how power is negotiated)

- **DIN 70121 / DIN SPEC 70121** — the older DC handshake; basic charge loop.
- **ISO 15118-2** — modern DC/AC; enables **Plug & Charge** (the car authenticates
  by cable, no card/app) and smart charging. This is what most current DC
  chargers implement. Confirmed on Kempower, Tritium, ABB (prep), Alpitronic. `[V]`
- **ISO 15118-20** — the newest; adds **bidirectional** power (V2G), better smart
  charging, and is what MCS relies on. Tritium RTM75 is "ISO 15118-20 ready". `[V]`

Important for modelling: the **ramp and curve shape are negotiated here, driven by
the vehicle's BMS**, not fixed by the charger. The charger supplies up to its
ceiling; the car decides how fast it pulls. So session time comes from pairing the
charger's max power with the vehicle's accept curve (from the pass-3 vehicle data).

## 3. Charger ↔ backend communication (OCPP)

Publisher: **Open Charge Alliance (OCA)**, since 2009. `[C]`

| Version | Released | What it added | Standard |
|---|---|---|---|
| OCPP 1.6 (1.6J = JSON) | 2015 | smart-charging profiles, OCPP-J over WebSocket | — |
| OCPP 2.0.1 | 2020 | device model, 3 security profiles, mutual TLS, **ISO 15118-2 Plug & Charge**, transaction events | **IEC 63584:2024** |
| OCPP 2.1 | 23 Jan 2025 | **bidirectional charging**, DER control, advanced smart charging, **ISO 15118-20**, battery swap, payments | **IEC 63584-210:2025** |

Sources `[C]`: episensor (versions table), codibly and carcody (IEC numbers and
2.1 release date). Confirm exact wording from openchargealliance.org directly.

Field reality `[C]`: as of 2026, **most deployed chargers speak OCPP 1.6**; a
growing share ship **2.0.1**; **2.1** is just entering the field. On the
datasheets I opened: ABB Terra 360 = OCPP 1.6J; Alpitronic HYC400 = 1.6J ready
for 2.0; Tritium RTM75 = 1.6J, 2.0.1 ready; Kempower = OCPP (1.6J + 2.0 per its
NEVI page).

## 4. "OCPP or not?"

For your question directly: **OCPP is near-universal on commercial DC chargers and
most networked AC wallboxes.** It's the backend protocol, so any charger you'd put
on a managed network supports it. The variation is the *version* (1.6 vs 2.0.1 vs
2.1), which decides whether you get native Plug & Charge, strong security, and true
dynamic smart charging "for free". Cheap, non-networked home units may omit OCPP.

## 5. Ramp / response times — the honest gap

Neither a clean max-power figure nor a ramp-rate figure is the same thing:
- **Max power** is on every datasheet (reliable).
- **Ramp time** (0→full power) and **setpoint-response time** (how fast the
  charger obeys a smart-charging command) are **almost never on datasheets**. The
  standards define *required* response windows (ISO 15118 / OCPP smart-charging),
  not a given model's measured speed. For real numbers you need independent test
  reports or manufacturer application notes. Logged as `[BOB]` in the catalogue.
