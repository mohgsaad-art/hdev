### RegionalDelivery

| case | A kWh/km | B kWh/km | error A vs B % | largest single input (err % of A vs B_x: mass / rho / cdxa) | C vs B % | note |
|---|---|---|---|---|---|---|
| mass: 0.5 x m_ref (4795 kg, 24.0 C, 3 m/s) | 0.8477 | 0.8506 | -0.340 | mass (-0.340 / +0.000 / +0.000) | -0.063 | physically impossible for E2 (below empty mass) |
| mass: empty (6570 kg, 24.0 C, 3 m/s) | 0.8944 | 0.8967 | -0.260 | mass (-0.260 / +0.000 / +0.000) | -0.169 |  |
| mass: m_ref (9590 kg, 24.0 C, 3 m/s) | 0.9746 | 0.9746 | +0.000 | none (reference) (+0.000 / +0.000 / +0.000) | -0.186 |  |
| mass: TPMLM (11990 kg, 24.0 C, 3 m/s) | 1.0394 | 1.0430 | -0.344 | mass (-0.344 / +0.000 / +0.000) | -0.704 |  |
| mass: 1.5 x m_ref (14384 kg, 24.0 C, 3 m/s) | 1.1050 | 1.1080 | -0.275 | mass (-0.275 / +0.000 / +0.000) | -0.788 | physically impossible for E2 (above TPMLM) |
| temperature: -10 C (9590 kg, -10.0 C, 3 m/s) | 1.0322 | 1.0326 | -0.034 | rho (+0.000 / -0.034 / +0.000) | -0.167 |  |
| temperature: T_ref (9590 kg, 24.0 C, 3 m/s) | 0.9746 | 0.9746 | +0.000 | none (reference) (+0.000 / +0.000 / +0.000) | -0.186 |  |
| temperature: +30 C (9590 kg, 30.0 C, 3 m/s) | 0.9658 | 0.9658 | +0.001 | rho (+0.000 / +0.001 / +0.000) | -0.193 |  |
| wind: 0 m/s (9590 kg, 24.0 C, 0 m/s) | 0.9395 | 0.9399 | -0.043 | cdxa (+0.000 / +0.000 / -0.043) | -0.276 |  |
| wind: 3 m/s (9590 kg, 24.0 C, 3 m/s) | 0.9746 | 0.9746 | +0.000 | none (reference) (+0.000 / +0.000 / +0.000) | -0.186 |  |
| wind: 8 m/s (9590 kg, 24.0 C, 8 m/s) | 1.0890 | 1.0897 | -0.071 | cdxa (+0.000 / +0.000 / -0.071) | -0.147 |  |

Worst corner (all 16): **0.5 x m_ref / -10 C / 8 m/s** error -0.401 % (A 1.0363, B 1.0405) physically impossible for E2 (below empty mass)
Worst corner among realistic masses (empty, TPMLM): **empty / -10 C / 8 m/s** error -0.388 %

### UrbanDelivery

| case | A kWh/km | B kWh/km | error A vs B % | largest single input (err % of A vs B_x: mass / rho / cdxa) | C vs B % | note |
|---|---|---|---|---|---|---|
| mass: 0.5 x m_ref (4795 kg, 24.0 C, 3 m/s) | 0.6287 | 0.6377 | -1.413 | mass (-1.413 / +0.000 / +0.000) | -0.096 | physically impossible for E2 (below empty mass) |
| mass: empty (6570 kg, 24.0 C, 3 m/s) | 0.7075 | 0.7135 | -0.834 | mass (-0.834 / +0.000 / +0.000) | -0.225 |  |
| mass: m_ref (9590 kg, 24.0 C, 3 m/s) | 0.8498 | 0.8498 | +0.000 | none (reference) (+0.000 / +0.000 / +0.000) | -0.255 |  |
| mass: TPMLM (11990 kg, 24.0 C, 3 m/s) | 0.9712 | 0.9665 | +0.491 | mass (+0.491 / +0.000 / +0.000) | -0.249 |  |
| mass: 1.5 x m_ref (14384 kg, 24.0 C, 3 m/s) | 1.0976 | 1.0847 | +1.187 | mass (+1.187 / +0.000 / +0.000) | +0.092 | physically impossible for E2 (above TPMLM) |
| temperature: -10 C (9590 kg, -10.0 C, 3 m/s) | 0.8718 | 0.8729 | -0.123 | rho (+0.000 / -0.123 / +0.000) | -0.224 |  |
| temperature: T_ref (9590 kg, 24.0 C, 3 m/s) | 0.8498 | 0.8498 | +0.000 | none (reference) (+0.000 / +0.000 / +0.000) | -0.255 |  |
| temperature: +30 C (9590 kg, 30.0 C, 3 m/s) | 0.8464 | 0.8462 | +0.030 | rho (+0.000 / +0.030 / +0.000) | -0.250 |  |
| wind: 0 m/s (9590 kg, 24.0 C, 0 m/s) | 0.8320 | 0.8312 | +0.108 | cdxa (+0.000 / +0.000 / +0.108) | -0.287 |  |
| wind: 3 m/s (9590 kg, 24.0 C, 3 m/s) | 0.8498 | 0.8498 | +0.000 | none (reference) (+0.000 / +0.000 / +0.000) | -0.255 |  |
| wind: 8 m/s (9590 kg, 24.0 C, 8 m/s) | 0.8964 | 0.8985 | -0.240 | cdxa (+0.000 / +0.000 / -0.240) | -0.170 |  |

Worst corner (all 16): **0.5 x m_ref / -10 C / 8 m/s** error -1.888 % (A 0.7039, B 0.7175) physically impossible for E2 (below empty mass)
Worst corner among realistic masses (empty, TPMLM): **empty / -10 C / 8 m/s** error -1.311 %
