# Links for Bob to fetch: data library, combined (pass 1 + pass 2 + Gemini), 6 Nov 2026

**How:**
- **Colab**: big public file. Download in Colab with `!wget` (like the EEA zip) and send me the header and a sample.
- **Upload**: open it in your browser, save the PDF or page, and attach it here (or put it in Kiro's `docs/research/inputs/`).
- **Ask**: needs an email, login or contract.
- **Buy**: paid.

**Need:**
- **MUST**: research could not open it, so the question stays open until you fetch it.
- **COPY**: research read it. Keep a copy so Kiro and I can cite page numbers.

Found in: P1 = my pass 1, P2 = my pass 2, G = Gemini.

## A. EU / EEA / regulation

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| A1 | EEA HDV, Reporting Period 2024–25 (2.5 GB) | https://sdi.eea.europa.eu/data/1e44df1d-6a56-41e4-9d67-aeae0ab909c9 ; direct: https://sdi.eea.europa.eu/datashare/s/xE4XwYDKjpWAaRS/download | Colab | MUST | Column list + 5 rows. Is it your 139-column file? Are there kWh/range/battery fields? | P1, P2 |
| A2 | EEA HDV, Reporting Period 2023–24 | https://sdi.eea.europa.eu/data/450fe389-2c77-4e62-a57b-b2b66356e796 | Colab | MUST | Same | P1, P2 |
| A3 | Parent record for both (record 13f5615a) | https://www.eea.europa.eu/en/datahub/datahubitem-view/13f5615a-0524-4a18-9666-7165e55c11ba | Upload (save page) | COPY | Release list, revision notes | P2, G |
| A4 | EEA HDV viewer (2023+) | https://discomap.eea.europa.eu/App/CO2HDV_2023/ | Upload (screenshot fields) | MUST | Field list as a cross-check | P1, P2 |
| A5 | Statistical metadata PDF, 2024–25 release | https://sdi.eea.europa.eu/catalogue/srv/api/records/1e44df1d-6a56-41e4-9d67-aeae0ab909c9/attachments/CO2%20from%20heavy%20duty%20vehicles_Statistical%20metadata_2024.pdf | Upload | MUST (server error for me) | ZEV field definitions | P1, P2 |
| A6 | Attachments list, 2024–25 release (look for a table definition) | https://sdi.eea.europa.eu/catalogue/srv/api/records/1e44df1d-6a56-41e4-9d67-aeae0ab909c9/attachments | Upload | MUST | Table definition xlsx | P1 |
| A7 | EEA vans CO2 monitoring | https://www.eea.europa.eu/en/datahub/datahubitem-view/9636827c-bd0c-40f5-814e-c4065c11c9a0 | Colab | MUST | BEV rows: Z (Wh/km), Zr (range), masses, power | P1 |
| A8 | EEA cars CO2 monitoring | https://www.eea.europa.eu/data-and-maps/data/co2-cars-emission-22 | Colab | MUST | Same for cars | P1 |
| A9 | EEA real-world OBFCM (cars/vans) | https://www.eea.europa.eu/en/datahub/datahubitem-view/1c1ffad2-34c3-471b-bd69-dd013cdd7b80 | Colab | MUST | Are there BEV electric-energy columns? | P1 |
| A10 | VECTO repo, generic BEV vehicles + LICENCE file | https://code.europa.eu/vecto/vecto (you already have `mohgsaad-art/VECTO`) | Kiro | MUST | E2/E3/E4/IEPC generic component files; EUPL 1.2 text | P1, P2, G |
| A11 | Reg. 2017/2400 consolidated (Annex Xb standard values; CIF fields) | https://eur-lex.europa.eu/eli/reg/2017/2400/2024-01-01/eng | Upload | COPY | Annex Xb App. 8–10; CIF point 2.6.4 | P1 |
| A12 | Reg. 2018/956 Annex I (CdxA bins; monitoring fields) | https://www.legislation.gov.uk/eur/2018/956/annex/I/part/3 ; https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32018R0956 | Upload | COPY | Part C table (already transcribed) | P1, G |
| A13 | COM(2025) 589 amended proposal (CO2 emission classes, CIF 2.6.4) | https://transport.ec.europa.eu/document/download/ac9c6064-08b0-40d9-a7ac-a12065784453_en?filename=COM_2025_589_F1_AMENDED_PROPOSAL_FOR_A_DIRECTIVE_EN_V9_P1_4252465.PDF | Upload | COPY | Which CIF values feed tolls | P1 |
| A14 | EU weights & dimensions revision status | https://www.europarl.europa.eu/legislative-train/theme-a-european-green-deal/file-revision-of-the-weights-and-dimensions-directive | Upload | COPY | +4 t ZEV is still a proposal | P1 |
| A15 | ISO 24162:2022 (refuse trucks only) | https://www.iso.org/standard/77958.html ; free preview: https://cdn.standards.iteh.ai/samples/77958/47a4ca63f4f64d51a4281df1a4092c80/ISO-FDIS-24162.pdf | Buy (preview: Upload) | MUST if we want the method | Test cycle, energy per run | P1, P2, G |
| A16 | EPREL tyre database (API) | https://eprel.ec.europa.eu | Ask (API key) | MUST | C3 truck tyre RRC class by size; licence | P1, G |

## B. Danish rules and registers

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| B1 | BEK 1447/2025 (weights and dimensions; **settles the dates**: 20 t two-axle from 1 Jan 2026, 58 t from 1 Jan 2027) | https://www.lovtidende.dk/api/pdf/253937 | Upload | COPY | § 14–16, § 21, § 23, § 38 | P2 |
| B2 | BEK 1415/2023 (ZEV +2 t) | https://www.retsinformation.dk/eli/lta/2023/1415 | Upload | MUST | Does ZEV +2 t still apply on top of the new 20 t? (overlap not verified) | P1, P2 |
| B3 | Færdselsstyrelsen Meddelelse 2042 | https://cdn.fstyr.dk/faerdselsstyrelsen/Media/638454153820835110/Meddelelse%20nr%202042%20-%20For%C3%B8gede%20v%C3%A6gte%20og%20l%C3%A6ngder%20p%C3%A5%20lastbil%20og%20p%C3%A5h%C3%A6ngsk%C3%B8-ret%C3%B8j%20samt%20godkendelse%20af%20lastbil%20med%20%C3%B8get%20vogntogs-v%C3%A6gt%20til%20brug%20i%20dobbelttrailer-vogntog%20-%20Om%20k%C3%B8ret%C3%B8jers%20indretning%20og%20udstyr%20mv.pdf | Upload | COPY | ZEV type-approval details | P1 |
| B4 | DTL overview of weights and dimensions (Jan 2026) | https://landtrafik.dk/wp-content/uploads/2026/07/hsl20260112_DTL_Oversigt-vaegtogdimen-12012026.pdf | Upload | COPY | Practical table; 57.5 t drive-axle note | P2 |
| B5 | DMR bulk extract (weekly XML, public FTP, ~75 GB unzipped) | ftp://5.44.137.84/ESStatistikListeModtag/ | Colab (FTP) | MUST | Header and electric fields. **No licence found** | P2 |
| B6 | Motorstyrelsen data reuse terms | https://info.skat.dk/data.aspx?oid=2179562 | Ask | MUST | Commercial reuse of DMR | P1, P2, G |
| B7 | Renodjurs alternative fuels appendix (Bilag 9) | https://renodjurs.dk/sites/default/files/2021-06/Bilag%209_Alternative%20drivmidler.pdf | Upload | COPY | ~2 kWh per tonne collected (compactor + lift) | P2 |
| B8 | Frederiksberg PVI e-refuse truck | https://varebilogtransport.dk/frederiksberg-klar-med-elektrisk-skraldebil/ and https://varebilogtransport.dk/skraldebiler-i-stoedet/ | Upload | COPY | 1.7 vs 2.25 kWh/km (conflict) | P2 |
| B9 | Unicon / Scania DK e-mixer | Source article: https://thedriven.io/2026/05/11/scania-unveils-fully-battery-electric-concrete-mixer-truck-that-powers-the-mixer-system-too/ | Ask (Unicon / Scania DK) | MUST | Drum kW, duty cycle, measured kWh | P1 |

## C. Other national registers

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| C1 | Norway, Statens vegvesen API schema | https://autosys-kjoretoy-api.atlas.vegvesen.no/swagger-ui/index-enkeltoppslag.html ; https://akfell-datautlevering.atlas.vegvesen.no/swagger-ui/index.html?configUrl=/v3/api-docs/swagger-config#/enkelt-oppslag-resource | Upload (save the schema JSON) | MUST | Battery / range / energy fields? Commercial terms | P1, P2 |
| C2 | Sweden, Transportstyrelsen register extracts (paid) | https://www.transportstyrelsen.se/sv/vagtrafik/fordon/fordons-agaruppgift/uttag-av-fordonsdata-pa-fil/fordonsdata-fran-vagtrafikregistret/ | Ask | MUST | Field list and price | P2 |
| C3 | Finland, Traficom open data (202 MB zip, CC BY 4.0) | https://opendata.traficom.fi/Content/Ajoneuvorekisteri.zip | Colab | MUST | Header + electric N1/N2/N3 rows | P1 |
| C4 | Finland, Traficom technical product (paid) | https://www.traficom.fi/sites/default/files/media/file/TPERAP009%20Ajoneuvon%20tekniset%20tiedot.pdf | Upload | COPY | Axle/tyre fields on offer | P1 |
| C5 | Netherlands, RDW (CC-0) | Fuel/WLTP: https://opendata.rdw.nl/api/v3/views/8ys7-d773/export.csv?accessType=DOWNLOAD ; vehicles: https://opendata.rdw.nl/api/views/m9d7-ebf2 | Colab | MUST | Electric vans/trucks: Wh/km, range, masses, axles | P1 |

## D. OEM documents

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| D1 | Volvo FM Electric page | https://www.volvotrucks.com/en-en/trucks/electric/volvo-fm-electric.html | Upload | MUST (blocked in pass 2) | 30/60/90 kW ePTO, ≤460 kWh usable | P1, P2 |
| D2 | Volvo FH Electric page | https://www.volvotrucks.com/en-en/trucks/electric/volvo-fh-electric.html | Upload | COPY | Same | P2 |
| D3 | Volvo FH Aero Electric page | https://www.volvotrucks.com/en-en/trucks/electric/volvo-fh-aero-electric.html | Upload | MUST | 725 kWh usable; AC-ePTO 43/22 kW | P2 |
| D4 | Volvo FL Electric page (global) + UK page | https://www.volvotrucks.com/en-en/trucks/electric/volvo-fl-electric.html ; https://www.volvotrucks.co.uk/en-gb/trucks/electric/volvo-fl-electric.html | Upload | COPY | 175–565 vs 280–565 kWh (conflict) | P2 |
| D5 | Volvo electromobility product guide | https://www.volvotrucks.com/content/dam/volvo-trucks/markets/master/home/trucks/brochure-gallery/Volvo-trucks-volvo-electromobility-product-guide-brochure.pdf | Upload | MUST | Page for FL/FE ePTO 100/70 kW | P2 |
| D6 | Volvo FL battery fact sheet | https://stpi.it.volvo.com/STPIFiles/Volvo/FactSheet/2BATT170_Eng_05_331735919.pdf | Upload | MUST | 94 kWh per pack, ESS565K | P2 |
| D7 | Volvo FH 80 t (Sep 2026) | https://www.volvotrucks.com/en-en/news-stories/press-releases/2026/sep/volvo-trucks-launches-new-80-tonne-electric-truck-with-longer-ra.html | Upload | COPY | MCS 680 kW, ePTO reefers | P2 |
| D8 | Volvo VNR Electric BBI (US) | https://www.volvotrucks.us/media/vtna/files/shared/body-builder/manuals/2025/vnr-electric-final.pdf | Upload | COPY | 600 V, ePTO chapter | P1 |
| D9 | Volvo NA PTO BBI | https://www.volvotrucks.us/media/vtna/files/shared/body-builder/manuals/2025/section-9-power-take-off-pto.pdf | Upload | COPY | PTO formulas | P1 |
| D10 | Volvo VNR ePTO press (2026) | https://www.volvotrucks.us/news-and-stories/press-releases/2026/may/volvo-trucks-expands-what-electric-trucks-can-do-in-north-america/ | Upload | COPY | 69.5 kW at 271 Nm | P2 |
| D11 | Volvo EU body builder instructions (Electric range) | **URL not found.** Search Volvo Trucks body builder portal | Ask / Upload | MUST | EU ePTO limits | P1 |
| D12 | Scania BEV body-builder booklet | https://bodybuilder.scania.com/content/dam/bodybuilder/tbb-files/factory-fitted-options/booklets/new-en/BEV_BATTERY_ELECTRIC_VEHICLE.pdf | Upload | MUST | PTO EL / PTO EM kW and voltage, 250 A supply | P1, G |
| D13 | Scania BEV pages (current, 1st gen) | https://www.scania.com/uk/en/home/products/trucks/battery-electric-truck.html ; https://www.scania.com/ke/en/home/products/trucks/battery-electric-truck.html | Upload | COPY | 240–560 kWh usable, motors, CCS/MCS | P1 |
| D14 | Mercedes eActros 600 product sheet | https://www.mercedes-benz-trucks.com/content/dam/brandhub/markets/gb/files/product-sheets/eActros-600-product-sheet.pdf.coredownload.pdf | Upload | COPY | 621/600 kWh, LFP, 800 V, ePTO | P1, G |
| D15 | Mercedes eEconic product sheet | https://special.mercedes-benz-trucks.com/fileadmin/user_upload/Documents/eEconic/E_Produktblatt_eEconic_ENG_screen.pdf | Upload | COPY | 336 kWh, ePTO ~30/~52 kW at 50 % SoC | P2 |
| D16 | eEconic waste page (ZF eWorX) | https://special.mercedes-benz-trucks.com/en/the-e-econic/general/applications/waste-disposal.html | Upload | COPY | 33/58 kW | P2 |
| D17 | eEconic international page | https://www.mercedes-benz-trucks.com/int/en/trucks/eeconic.html | Upload | COPY | 31/55 kW mechanical, 290 Nm | P2 |
| D18 | ZF eWorX | https://www.zf.com/products/en/cv/products_73024.html | Upload | COPY | 50 kW e-motor | P2 |
| D19 | DAF XD Electric infosheet | https://www.daf.com/-/media/files/document-library/infosheets/electric/daf-xd-electric-infosheet-xde-en-556205.pdf?h=900&w=1600&rev=51d4ad90873a4d6bb99aa6b94f0d53eb&sc_lang=en&hash=3F7690F7F8801919CAC572042A210C77 | Upload | MUST | Page numbers; ePTO 25/90 kW (60/100 kW added?) | P2 |
| D20 | DAF XD Electric global page | https://www.daf.global/en-us/trucks/daf-xd-electric | Upload | COPY | Torque 930/1,370 Nm (conflict) | P2 |
| D21 | MAN eTruck press releases | https://press.mantruckandbus.com/corporate/man-is-entering-a-new-electric-era/ ; https://press.mantruckandbus.com/corporate/man-etruck-leads-the-way-with-electric-trucks/ | Upload | COPY | 534/480 kWh, NMC, 330 kW, 4 gears | P2 |
| D22 | MAN body builder guide (eTGX/eTGS/eTGL) | **URL not found.** MANTED portal | Ask (login?) | MUST | ePTO limits | P1 |
| D23 | Renault E-Tech, IVECO S-eWay/eDaily, Fuso eCanter, Ford E-Transit + van OEMs | Not found yet (Kiro) | — | — | — | P1, P2 |
| D24 | Solaris Urbino 12 electric (2025 and 2022 sheets) | https://www.solarisbus.com/public/assets/Biuro_prasowe/2025_10_03_Premiera_E105_na_Busworld/Technical_data_Urbino_12_electric.pdf ; https://www.solarisbus.com/public/assets/Biuro_prasowe/2022_10_12_Transexpo/Technical_Details_Urbino_12_electric_Transexpo_EN.pdf | Upload | COPY | Motor, battery, GVW | P2 |
| D25 | STOAG e-bus fleet data | https://www.stoag.de/en/stoag/elektromobilitaet/technische-daten.html | Upload | COPY | AC 24 kW, PTC heater 25 kW | P2 |

## E. Body equipment and PTO

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| E1 | Liebherr ETM e-mixer brochure | https://www-assets.liebherr.com/media/bu-media/lhbu-lmt/documents/truck-mixer/electric-truck-mixer-etm.pdf | Upload | COPY | 60/125 kW, 32 kWh, 650 V (120 vs 125 conflict) | P2 |
| E2 | Dennis Eagle eCollect | https://www.dennis-eagle.co.uk/products/ecollect/ | Upload | COPY | 180/300 kWh, separate e-pump | P1 |
| E3 | Carrier Vector eCool datasheet | https://frimag.si/wp-content/uploads/2022/03/Carrier_Transicold_Vector_eCool_ENG.pdf | Upload | COPY | 19.2 kWh, 19 kW continuous | P1 |
| E4 | Carrier Vector 1550 E City | https://www.carrier.com/truck-trailer/es/es/products/es-truck-trailer/trailer/vector-1550-e-city/ | Upload | COPY | Cooling W (electrical input missing) | P1 |
| E5 | Carrier [R]eCool | https://www.carrier.com/truck-trailer/en/eu/products/eu-truck-trailer/Electric_and_sustainable_cold_chain/recool.html | Upload | COPY | 38.5 kWh | P1 |
| E6 | CEC electric refuse truck report | https://www.energy.ca.gov/sites/default/files/2024-03/CEC-600-2024-010.pdf | Upload | COPY | kWh/mile with and without ePTO | P1 |
| E7 | Geesinknorba, FAUN, Zoeller, Joab, HIAB eHiPro, Palfinger, Thermo King, Schmitz S.KOe COOL, Bucher, Aebi Schmidt, Boschung | Not found yet (Kiro) | — | — | Electrical kW, energy per cycle | P1, P2, G |

## F. Real-world consumption and datasets

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| F1 | KsNI evaluation (BMV) | https://www.bmv.de/SharedDocs/DE/Anlage/G/abschlussbericht-ksni-evaluation.pdf?__blob=publicationFile | Upload | COPY | Table 2-5 medians | P1 |
| F2 | Öko-Institut ELV-Live (report 1) | https://www.oeko.de/fileadmin/oekodoc/ELV-Live_Pilotbetrieb-Skalierung-batterieelektrischer-Lkw.pdf | Upload | COPY | Mass and temperature slopes | P1 |
| F3 | Öko-Institut ELV-Live (report 2, 2025) | https://www.oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks.pdf | Upload | MUST | Page numbers, licence | P2 |
| F4 | NOW e-bus final report (heating chapter) | https://www.now-gmbh.de/wp-content/uploads/2022/04/NOW_Abschlussbericht_Begleitforschung-Bus.pdf | Upload | MUST | HVAC kW / kWh by heating type | P1 |
| F5 | NOW heavy-truck market report 2024 | https://www.now-gmbh.de/wp-content/uploads/2024/11/Marktentwicklung-klimafreundlicher-Technologien-im-schweren-Strassengueterverkehr-2024.pdf | Upload | COPY | Projections (label as such) | P1 |
| F6 | NOW e-vehicle handbook (2020) | https://www.now-gmbh.de/wp-content/uploads/2020/09/now_handbuch_elektrofahrzeuge_web.pdf | Upload | COPY | Older trials | P1 |
| F7 | ZEHID annual report 2026, pp. 21–36 | https://iuk-business-connect.org.uk/wp-content/uploads/2026/10/ZEHID-annual-report-2026-pages-23.pdf | Upload | MUST (truncated) | Early insights, Appendix A | P2 |
| F8 | ZEHID BIFA deck + Cenex Expo deck | https://bifa.org/wp-content/uploads/2025/12/ZEHID-BIFA.pdf ; https://cenex-expo.s3-eu-west-2.amazonaws.com/presentations/2025/isabella-panovic.pdf | Upload | COPY | km and kWh totals | P2 |
| F9 | eFREIGHT 2030 reports | https://es.catapult.org.uk/project/efreight-2030/ | Upload | MUST | Report list | P2 |
| F10 | ICCT real-world ZE truck use cases (Aug 2025) | https://theicct.org/wp-content/uploads/2025/08/ID-359-%E2%80%93-EU-goods-transport_report_final.pdf | Upload | MUST | 107–116 kWh/100 km; unit check | P2 |
| F11 | ICCT HDV targets report (CdxA mid-points) | https://theicct.org/wp-content/uploads/2025/09/ID-456-%E2%80%93-EU-HDV-Targets_report_final.pdf | Upload | COPY | Method | P1 |
| F12 | ICCT spatiotemporal charging (Sep 2026) | https://theicct.org/wp-content/uploads/2026/09/ID-649-%E2%80%93-EU-spatiotemporal-analysis_report_final-1.pdf | Upload | COPY | Battery/consumption assumptions | P1 |
| F13 | TNO 2022 R10409 (cars real-world vs WLTP) | https://publications.tno.nl/publication/34639300/erZOUs/TNO-2022-R10409.pdf | Upload | COPY | 1.19 × WLTP | P2 |
| F14 | US DOE VGI assessment (Jan 2025) | https://www.energy.gov/sites/default/files/2025-01/Vehicle_Grid_Integration_Asseessment_Report_01162025.pdf | Upload | COPY | kWh/mile by class | P1 |
| F15 | Argonne MD/HD estimates (OSTI 2311852) | https://www.osti.gov/dataexplorer/biblio/dataset/2311852 | Colab | MUST | Dataset + licence | P1 |
| F16 | NREL Fleet DNA (CC BY 4.0) + data dictionary | https://data.nrel.gov/submissions/42 ; https://docs.nrel.gov/docs/fy14osti/62572.pdf | Colab / Upload | MUST | Licence page, fields | P2 |

## G. Aggregators and licences

| # | What | Link | How | Need | What to get | Found in |
|---|---|---|---|---|---|---|
| G1 | ZETI (CALSTART) | https://globaldrivetozero.org/tools/ | Ask | MUST | Fields, export, commercial licence | P1 |
| G2 | EV Database API | https://ev-database.org/data-services-api | Ask (quote) | MUST | Price and terms | G |
| G3 | Open EV Data | https://open-ev-data.github.io/1.4.x/governance/ | Upload (licence file) | MUST | Actual licence (Gemini: ODbL / CC-BY-SA) | G |
| G4 | Nature Sci Data 2025 EV dataset | https://www.nature.com/articles/s41597-025-05770-7 | Upload | MUST | Dataset licence | P1 |
| G5 | Synsbasen API (paid DMR reseller) | https://api.synsbasen.dk/v1/docs | Ask | optional | Fields and price | P1, P2 |

## H. Gemini claims: status after pass 2

| Gemini claim | Verdict |
|---|---|
| CdxA table A1–A24 | **Correct** |
| Volvo ePTO 100 kW continuous / 150 kW peak | **False.** FH/FM: 30/60/90 kW. 150 kW is the mechanical transmission PTO; 100 kW is the older FL/FE large-variant peak |
| Volvo 360–565 kWh | **Mixed models.** FH/FM 360–540 kWh; 565 kWh is the FL |
| DMR free open bulk REST API, free commercial reuse | **Partly false.** Weekly XML on public FTP; no licence found |
| EEA record 13f5615a has PEVArchitecture for ~46 % | **Record exists** (parent collection); the field and the 46 % are unverified (46 % is our own number from your file) |
| eEconic 336 kWh, 330/400 kW, eWorX 33/58 kW | **Mostly correct.** Also ~30/~52 kW electrical at 50 % SoC; 31/55 kW mechanical; 3 × ~105 kWh conflicts with 336 |
| ePTO efficiency 0.82–0.88 | **No source.** Don't use |
| Fixed transmission drag 1.5–2.5 % | **No source**, and not how VECTO works. Don't use |
| Geesinknorba kWh per bin lift | **Not found** |
| TNO open CC-BY CSVs | **Not found** (PDF reports only) |
| ISO 24162 covers cranes/tippers | **False.** Refuse collection vehicles only (EN 1501) |
| Danish 58 t in 2027 | **Correct** (BEK 1447/2025 § 38). 20 t two-axle from 1 Jan 2026 |
