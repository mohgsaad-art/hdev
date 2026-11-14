# Files Bob needs to fetch (Kiro / Claude could not open them) — 2 Nov 2026

Priority: **1** = blocks a decision now, **2** = needed for validation or defaults, **3** = library / later.
"Search" = no verified direct link; search the title.

## HVAC (`HVAC_thermal`, `ssm_total_w`, `climate_lookup`)
| P | What | Link | What I need from it |
|---|---|---|---|
| 1 | NREL CoolCab reports TP-5400-52452 and TP-5400-66860 | Search the numbers on https://www.osti.gov | Cab area, U/UA, volume, window area (day cab, sleeper); **how U/UA was measured (ventilation on or off)** |
| 1 | NREL sleeper cab thermal management (OSTI 1055379) | https://www.osti.gov/biblio/1055379 | Same as above; measured heating/cooling loads |
| 1 | CoolCab test + CoolCalc development (DOE) | https://www.energy.gov/eere/vehicles/articles/coolcab-test-and-evaluation-and-coolcalc-hvac-tool-development | Links to the test reports; test method |
| 2 | CoolCalc SAE paper 2011-01-0656 (paywalled) | https://saemobilus.sae.org/content/2011-01-0656 · https://research-hub.nrel.gov/en/publications/coolcalc-a-long-haul-truck-thermal-load-estimation-tool-paper-no-/ | Model inputs, validation data |
| 1 | Dvorak et al. 2025 (AIT), electric truck cabin HVAC, measured | Search (MDPI / preprints.org) | Confirm 100 m3/h fresh air for 2 occupants at 1000 ppm CO2; cab HVAC W vs ambient |
| 2 | Ramesh Babu 2025 (Chalmers), truck cabin HVAC, simulated | Search on research.chalmers.se | Cab parameters, W vs ambient |
| 2 | 1D truck cabin thermal model (MDPI, from Kiro's search) | Search | Cab parameters |
| 2 | JRC133756, heating vs cooling energy | Probably https://publications.jrc.ec.europa.eu/repository/handle/JRC133756 (not opened) | -7 C heating vs 35 C cooling figure, conditions |
| 2 | Mercedes eActros winter claim (+20-25 %) | Search Mercedes-Benz Trucks press | Exact figure, temperatures, route, payload, heat pump |
| 2 | Oko-Institut ELV-LIVE (eActros fleet) | Search; related report: https://www.oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks-operating-in-Germany.pdf | Monthly / temperature-binned kWh/km |
| 3 | ICCT 2023, real-world HDV BEVs | Search | HVAC / winter data |
| 3 | SAE J2765_201707 (MAC COP bench test) | Search SAE Mobilus | Only if we cite it for user COP data |
| 3 | Kiro's HVAC doc | `hdev` repo PR #20: `docs/research/hvac-thermal-parameters-2026-11.md` | Paste so I can see all its links |

## Battery / winter (consumption + battery engine)
| P | What | Link | What I need |
|---|---|---|---|
| 2 | Dollinger & Fischerauer 2021, battery heating | https://www.mdpi.com/1996-1073/14/18/5804 | Battery heating share, method |
| 2 | Stanford drayage study | https://pangea.stanford.edu/ERE/pdf/OnoriPDF/Journals/128.pdf | Battery heater power vs temperature |
| 2 | Source for battery Ri vs temperature | None found yet | — |
| 3 | E-bus door openings, MDPI 2021 (simulated) | https://www.mdpi.com/2076-3417/11/24/11761 | Method, if adapted to truck cabs |

## Fridge truck (TRU helper, planned)
| P | What | Link | What I need |
|---|---|---|---|
| 3 | USDA TB-1375 (door openings, refrigerated trucks) | Search | Infiltration per door opening |
| 3 | Int. J. Refrigeration 2015 (door openings) | Search | Same |
| 3 | Brunel thesis (~34 % door load) | Search | Method, conditions |

## PTO profile library
| P | What | Link | What I need |
|---|---|---|---|
| 3 | Ban & Stipetic, IEEE ACEMP-OPTIM 2019 | Search title (Rudjer Boskovic Institute / ResearchGate) | kW-vs-time cycles (simulated) |
| 3 | MDPI Appl. Sci. 2021, refuse compactor electric pump (CC BY) | https://www.mdpi.com/2076-3417/11/7/3033 · https://iris.unicas.it/retrieve/bb5794fc-405d-4731-ab75-52fdcaa22ff1/applsci-11-03033.pdf | Measured power curve, if any |
| 3 | Eaton Bezares ePTO, Danfoss ED3, Dulevo sweeper datasheets | Search | Ratings (verify; came from search text) |
| 3 | Liebherr ETM mixer | https://www-assets.liebherr.com/media/bu-media/lhbu-lmt/documents/truck-mixer/electric-truck-mixer-etm.pdf | Rating confirmation |
| 3 | Caltrans task 4137 sweeper | https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-notes/task4137-rns-05-26-a11y.pdf | Numbers once published |
| 3 | Springer 2025 concrete mixer, HECTOR, Zemo 2021, Warwick 2022 | Links in Kiro's file | — |
| 3 | Kiro's PTO findings | `/projects/sandbox/epto_research/epto_findings_for_Bob.md` | Paste it |

## Payload / weights law (parser)
| P | What | Link | What I need |
|---|---|---|---|
| 2 | Directive 96/53/EC consolidated, Art. 10b + Annex I 2.3 | https://eur-lex.europa.eu/eli/dir/1996/53 | Settle 1 t vs 2 t ZEV allowance |
| 2 | Reg. (EU) 2019/1242 Art. 20 (amends 96/53) | https://eur-lex.europa.eu/eli/reg/2019/1242/oj | Same |
| 2 | Current Danish dimension order (successor of BEK 1663/2023) | https://www.retsinformation.dk — search "Bekendtgørelse om køretøjers største bredde, længde, højde, vægt og akseltryk" (status "Gældende") | BEK no., limits, ZEV allowance |
| 3 | Danish modulvogntog (60 t) order | retsinformation.dk — search "modulvogntog" | BEK no., network rules |

## VECTO runs Bob has to make (no file exists in the repo)
| P | What | What I need |
|---|---|---|
| 2 | BEV `.vmod` with per-aux columns (incl. steering pump) | Confirm SP = 0 at standstill in output |
| 2 | LowLoading `.vmod` (E2, Regional + Urban) | Payload-slope split vs VECTO |
| 3 | Engineering-mode Municipal + PTO run | Refuse cycle validation |

## Already in the project (no fetch needed)
- Reg. 2017/2400 consolidated PDF (`CELEX_02017R2400-20260101_EN_TXT.pdf`): Claude can read the OCR-garbled formulas (e.g. Annex VII App. 3 axle) from the PDF pages directly.
