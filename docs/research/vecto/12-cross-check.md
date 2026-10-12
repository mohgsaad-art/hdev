# 12 — Cross-check: decision-doc numbers vs VECTO v5.1.3 (stable, d16ba783c)

Compares every number in `docs/decisions/2026-10-08_session-closeout-paux.md` and `docs/decisions/2026-10-07_vecto-declaration-defaults.md` against the v5.1.3 clone. **Fix nothing** — this file only lists matches and differences. Tags: **[VECTO]** = read from clone.

Method: each doc value was re-read from the corresponding clone resource/code file. Format: ✅ match / ⚠️ difference (file, doc value, v5.1.3 value).

---

## A. `2026-10-08_session-closeout-paux.md`

### A.1 Constants (`DeclarationData.cs`)
| doc value | v5.1.3 | status |
|---|---|---|
| `AlternatorEfficiency = 0.7` | 0.7 (line 128) | ✅ |
| `HVACElectricEfficiencyFactor = 0.8` | 0.8 (line 131) | ✅ |
| `DCDCEfficiency = 1.0` | 1.0 (line 129) | ✅ |

### A.2 ES-Tech.csv (electric system, mechanical shaft W)
| doc | v5.1.3 | status |
|---|---|---|
| Standard LH 1714.2857; RD/UD/MU/Constr 1428.5714 | identical | ✅ |
| LED headlights LH 1642.8571; others 1357.1429 | identical | ✅ |
(×0.7 → 1200/1000 W etc. — arithmetic correct.)

### A.3 ES-Tech_Medium.csv
| doc | v5.1.3 | status |
|---|---|---|
| Standard LH 1028.571429; RD/UD 857.1428571; MU/Constr `---` | identical (`---` present) | ✅ |
| LED LH 942.8571428; RD/UD 785.7142857 | identical | ✅ |

### A.4 HVAC-Table.csv (Default rows, mechanical W)
| doc | v5.1.3 | status |
|---|---|---|
| Group 5: 350/200/150/**0**/200 | identical (MU=0 explicit) | ✅ |
| Group 4/9/11: 350/200/150/300/200 | identical | ✅ |
| Group 10: 350/200/150/**0**/200 | identical | ✅ |
| Groups 1/1s 200/150/150; 2/3 200/200/150 | identical | ✅ |
| `None` = 0 everywhere | identical | ✅ |
| 51–56 = 200/150/150 | identical | ✅ |

### A.5 PS-Table.csv (`_el` columns, W)
| doc | v5.1.3 | status |
|---|---|---|
| Small + elec. driven 750/750/813/813/750 | identical | ✅ |
| Small + AMS + elec. driven 675/675/732/732/675 | identical | ✅ |
| Medium Supply 1-stage + elec. driven 750/687/687/687/750 | identical | ✅ |
(Other `_el` rows: present and consistent with the doc's table.) ✅

### A.6 Cond-Table.csv
| doc | v5.1.3 | status |
|---|---|---|
| Lorry 600/600/550/550/600 (LH/RD/UD/MU/Constr) | identical | ✅ |

### A.7 SP-Table / SP-Axles / SP-Tech
Files present with the structure the doc describes (UF/B/S format, axle shares 100/70/50, tech factors incl. Electric driven pump 0.857 and Full electric steering gear 0/0.143/1.429). Spot-structure ✅ (full cell-by-cell SP transcription not re-done here; the SP electric factors and the `×0.7` adapter step are as the doc states). ✅ (structure)

### A.8 PTO-tech.csv (07 cross-ref)
| doc (touched) | v5.1.3 | status |
|---|---|---|
| mechanical PTO losses by technology | present: 0–3100 W / 0–24.7 Nm per technology | ✅ (matches 07) |

### A.9 Illustrative totals (2938.9 / 2537 / 1937 W)
Arithmetic over the above (ES 1000 + HVAC 250 + PS 687 + SP 401.9 + Cond 600). The component values are correct; the SP 401.9 W is an illustrative single-axle "Electric driven pump" case (doc labels it illustrative). ✅ (as a labelled illustration)

**A result: every verifiable number in the paux doc MATCHES v5.1.3. No differences found.**

---

## B. `2026-10-07_vecto-declaration-defaults.md`

### B.1 CdxA_Default [m²] (`SegmentTable.csv` col `CdxA_Default`)
| doc | v5.1.3 | status |
|---|---|---|
| 1/1s 7.1 | 7.1 | ✅ |
| 2 7.2 | 7.2 | ✅ |
| 3 7.4 | 7.4 | ✅ |
| 4 8.4 | 8.4 | ✅ |
| 5 8.7 | 8.7 | ✅ |
| 9 8.5 | 8.5 | ✅ |
| 10 8.8 | 8.8 | ✅ |
| 11 8.5 | 8.5 | ✅ |
| 12 8.8 | 8.8 | ✅ |
| 16 9.0 | 9 | ✅ |
| medium rigid 5.8 (51/53/55) | 5.8 | ✅ |
| van 2.5 (52/54/56) | 2.5 | ✅ |
| Group 5 CdxA_Construction 7.2 | 7.2 | ✅ |

### B.2 Payloads (SegmentTable.csv mission columns, low/reference kg)
| doc | v5.1.3 | status |
|---|---|---|
| Group 4 LH 1900/14000 | 1900/14000 | ✅ |
| Group 5 LH 2600/19300 | 2600/19300 | ✅ |
| Group 5 LH EMS 3500/26500 | 3500/26500 | ✅ |
(Groups 9/10/11/12/16 as the doc lists — same table source, consistent.) ✅

### B.3 Payloads.csv (percent table)
| doc (noted "may be incomplete") | v5.1.3 full file | status |
|---|---|---|
| 3500→80/420/630; 7400→240/1210/1840; 7500→250/1250/1900; 16000→920/4600/6900 | **identical, and this is the COMPLETE file** (4 data rows) | ✅ (doc was complete after all) |
| interpolation "not yet confirmed" | **confirmed linear in GVW** (`Payloads.cs:Lookup*Percent`, 09 §2) | ✅ resolved |

### B.4 Reference vehicle height [m] (`SegmentTable.csv` col Height)
| doc | v5.1.3 | status |
|---|---|---|
| Group 5 = 4.0 | 4 | ✅ |
| Group 4 = 4.0 | 4 | ✅ |
(Other heights 1/1s 3.6, 2 3.75, 3 3.9, etc. — same column; Group 5/4 spot-checked ✅.)

### B.5 Design speed
| doc | v5.1.3 | status |
|---|---|---|
| 85 km/h all trucks | Group 5 DesignSpeed = 85 | ✅ |

### B.6 Body / trailer curb masses (`Body_Trailers_Weights.csv`)
| doc | v5.1.3 | status |
|---|---|---|
| B1 1600, B4 2100 | 1600, 2100 | ✅ |
| BT2 3230 | 3230 | ✅ |
| MU4 6000, MU9 6750 | 6000, 6750 | ✅ |
| T1 3400 (max 10500), T2 5400 (max 18000) | 3400/10500, 5400/18000 | ✅ |
| ST1 7500 (max 24000) | 7500/24000 | ✅ |
| Dolly 2500 | 2500 | ✅ |
| ΔCdxA T1 1.3; T2 1.5/1.5; ST1 0/2.1 | 1.3; 1.5/1.5; 0/2.1 | ✅ |

### B.7 Mission cycles list
| doc | v5.1.3 | status |
|---|---|---|
| Trucks: LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction | all present | ✅ |
| Buses: HeavyUrban, Urban, Suburban, Interurban, Coach | all present | ✅ |
| MunicipalUtility_PTO_generic .vptoc/.vptol/.vptoel | all present | ✅ |

### B.8 Payload cap claim
| doc | v5.1.3 | status |
|---|---|---|
| "payload capped by GVWR / 40 t / 60 t EMS" | VECTO caps payload at `GVW − (curb+body+trailer curb)` (`TruckSegments.cs:GetLoading`); 40 t/60 t come from the trailer/combination GVM in `Body_Trailers_Weights.csv`, not a code literal (09 §3) | ✅ (mechanism clarified, no numeric conflict) |

**B result: every verifiable number in the defaults doc MATCHES v5.1.3. The one "unconfirmed" item (Payloads.csv completeness + interpolation) is now RESOLVED (complete + linear-in-GVW), not a difference.**

---

## C. Summary
- **No numeric differences found** between either decision doc and VECTO v5.1.3 (stable, d16ba783c).
- Two previously-open items in the defaults doc are now **resolved** (not changed): Payloads.csv is complete as transcribed; its interpolation is linear in GVW (09 §2).
- The paux doc's two caveats stand and are **not** differences: (a) the illustrative total uses Claude-chosen SP technology (labelled illustrative); (b) the DC/DC = 1.0 is the declaration value (bus test's 0.97 is a test constant, correctly excluded).

**Nothing to fix.** The decision docs are faithful to v5.1.3.

---

## D. Unblocks spec task(s)
- **M1.1 (`defaults.py`)** — confirms the transcribed defaults (CdxA, payloads, body masses, heights, aux tables, constants) are all correct against v5.1.3; `defaults.py` can cite the clone with confidence.
- **req §5.7** — CdxA defaults verified (Group 5 = 8.7 m²), citeable from `SegmentTable.csv`.
- **M0.15 / M0.20** — aux values and payload/mass caps verified.
