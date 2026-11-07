"""Job 4: OEM website third column. Builds three_way.csv.

Each OEM entry was read from the manufacturer's own page / spec sheet (URL + date +
quote stored; PDFs not stored, per the copyright rule). kWh/km derived [D] only when the
same page gives usable kWh AND range under stated conditions: kWh/km = usable_kWh / range_km.

Matching rule (Job 4 point 4): an OEM page is matched to an EEA config only when battery
size and motor/architecture agree. Model name alone is not a match. Where they do not
agree we record "no match" with the reason.
"""
import csv
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

# OEM records: keyed by the EEA config_id we matched. Every value has url/date/quote/tag.
# range_km / usable_kwh / installed_kwh / kwh_km from the OEM page; conditions text verbatim-ish
# (paraphrased, <30 words). "cites_vecto": whether the page says VECTO/certification.
OEM = [
    # Mercedes eActros 600  (config C0153: 642 kWh installed / 549 usable, 601 kW, wheel eAxle)
    dict(config_id="C0153", make="Mercedes-Benz", model_gen="eActros 600 (2024 series)",
         url="https://eactros600.mercedes-benz-trucks.com/int/en/trucks/eactros-600.html",
         date="2026-11-07", installed_kwh=600.0, usable_kwh=None, range_km=500.0,
         oem_kwh_km_stated=1.03, kwh_basis="measured driving (testing tour, 103 kWh/100km)",
         conditions="up to 500 km no recharge; 44 t GCW; eAxle 400 kW cont/600 kW peak; LFP",
         cites_vecto=False,
         quote="range of 500 kilometres without recharging; average driving consumption 103 kWh per 100 km (testing tour)",
         match="battery 600 vs EEA 642 installed close; 600 kW peak matches; architecture e-axle matches"),
    # Volvo FH Electric (config C0582/C0712: 540 kWh installed / 462 usable, 467/312 kW)
    dict(config_id="C0582", make="Volvo", model_gen="FH Electric (540 kWh pack)",
         url="https://www.volvotrucks.com/en-en/trucks/electric/volvo-fh-electric.html",
         date="2026-11-07", installed_kwh=540.0, usable_kwh=540.0, range_km=None,
         oem_kwh_km_stated=1.1, kwh_basis="measured road test (Green Truck route, 1.1 kWh/km)",
         conditions="useable 450-540 kWh; 1.1 kWh/km at 80 km/h avg (road test, not certification)",
         cites_vecto=False,
         quote="useable energy storage of 450-540 kWh; energy consumption of 1.1 kWh per km (road test)",
         match="battery 540 installed matches EEA 540; FH Electric e-axle matches E-IEPC"),
    # DAF XB Electric (config C0002/C0008: 282 kWh installed / 241 usable, 190 kW E3)
    dict(config_id="C0008", make="DAF", model_gen="New Generation XB Electric (190 kW)",
         url="https://www.daf.global/en-us/trucks/new-generation-daf-xb-electric",
         date="2026-11-07", installed_kwh=282.0, usable_kwh=None, range_km=None,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="LFP gross 141-282 kWh; e-motor 190 kW nominal; DC fast charge 150 kW; no range/consumption on page",
         cites_vecto=False,
         quote="lithium iron phosphate high energy battery packs with a gross energy content of 141 up to 282 kWh",
         match="battery 282 gross matches EEA 282 installed; 190 kW matches em_desc"),
    # Scania R 400E B6x2*4NB (config C0420: 624 kWh installed / 440 usable, 410 kW)
    dict(config_id="C0420", make="Scania", model_gen="45 R / regional BEV (624 kWh)",
         url="https://qinfo.scania.com/group/en/home/electrification/e-mobility-hub/stronge-longer-and-even-more-efficient-meet-scanias-new-batter-electric-trucks.html",
         date="2026-11-07", installed_kwh=624.0, usable_kwh=None, range_km=400.0,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="up to 400 km on 624 kWh installed; urban/regional; up to 375 kW charging",
         cites_vecto=False,
         quote="up to 400 km distance on 624 kWh battery power",
         match="battery 624 installed matches EEA 624; regional BEV e-machine matches E-IEPC"),
    # MAN TGX BEV (config C0113: 534 kWh installed / 456 usable, 320 kW)
    dict(config_id="C0113", make="MAN", model_gen="eTGX (current gen, 6 packs 534 kWh)",
         url="https://www.klimafreundliche-nutzfahrzeuge.de/fahrzeugdatenbank/man-etgx/",
         date="2026-11-07", installed_kwh=534.0, usable_kwh=480.0, range_km=400.0,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="gross 534 kWh, net 480 kWh; up to 600 km solo distribution, up to 400 km long haul",
         cites_vecto=False,
         quote="Batteriekapazitaet brutto max. 534 kWh; netto/SOC max. 480 kWh; Reichweite max. 400 km (Fernverkehr)",
         match="battery 534 gross / 480 net ~ EEA 534 installed / 456 usable; eTGX e-axle matches E-IEPC"),
    # Renault E-Tech D/T (config C0218: 376 kWh installed / 324 usable, 200 kW E2)
    dict(config_id="C0218", make="Renault", model_gen="E-Tech D Electric (200-565 kWh range)",
         url="https://www.renault-trucks.pt/product/renault-trucks-e-tech-d-electric",
         date="2026-11-07", installed_kwh=None, usable_kwh=None, range_km=560.0,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="capacity 200-565 kWh; 185 kW peak / 130 kW cont; up to 560 km depending on use",
         cites_vecto=False,
         quote="Capacidade: 200 a 565 kWh; Potencia maxima 185 kW; Potencia continua 130 kW",
         match="PARTIAL: EEA em_desc 200 kW > OEM 185 kW peak; battery 376 within 200-565 band; treat as approximate"),
    # Iveco S-eWay semi (config C0091: 729 kWh installed / 558 usable, 851 kW)
    dict(config_id="C0091", make="Iveco", model_gen="S-eWay tractor (738 kWh, 9 packs)",
         url="https://www.batterydesign.net/iveco-s-eway/",
         date="2026-11-07", installed_kwh=738.0, usable_kwh=635.0, range_km=600.0,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="738 kWh total / ~635 kWh usable (9 packs); tractor; up to 600 km one charge",
         cites_vecto=False,
         quote="9 packs in parallel giving a total of 738kWh total and an estimated 635kWh usable",
         match="battery 738 ~ EEA 729 installed, 635 ~ 558 usable (OEM usable higher); tractor e-axle matches E-IEPC"),
    # Fuso eCanter (config C0059: 123 kWh installed / 105 usable, 132 kW) -> L battery
    dict(config_id="C0059", make="Fuso", model_gen="Next Gen eCanter (L battery 123.9 kWh)",
         url="https://www.mb.vanmossel.nl/vanmossel-trucks/aanbod/fuso-ecanter",
         date="2026-11-07", installed_kwh=123.9, usable_kwh=None, range_km=200.0,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="nominal 123.9 kWh (L), up to 200 km; 110 kW motor",
         cites_vecto=False,
         quote="nominale capaciteit 83,6 kWh (M, tot 140 km) en 123,9 kWh (L, tot 200 km)",
         match="battery 123.9 nominal matches EEA 123 installed; eCanter matches E-IEPC (132 kW ~ eCanter 110-129 kW)"),
    dict(config_id="C0058", make="Fuso", model_gen="Next Gen eCanter (M battery 83.6 kWh)",
         url="https://www.mb.vanmossel.nl/vanmossel-trucks/aanbod/fuso-ecanter",
         date="2026-11-07", installed_kwh=83.6, usable_kwh=None, range_km=140.0,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="nominal 83.6 kWh (M), up to 140 km; 110 kW motor",
         cites_vecto=False,
         quote="nominale capaciteit 83,6 kWh (M, tot 140 km actieradius)",
         match="battery 83.6 nominal matches EEA 82 installed; eCanter matches E-IEPC"),
    # Iveco Daily (eDaily) small van-based (config C0070: 111 kWh installed / 96 usable, 140 kW E3)
    dict(config_id="C0070", make="Iveco", model_gen="eDaily (3x37 kWh ~ 111 kWh)",
         url="https://www.iveco.com/belgium-fr/S-eWay/S-eWay-porteur",
         date="2026-11-07", installed_kwh=None, usable_kwh=None, range_km=None,
         oem_kwh_km_stated=None, kwh_basis=None,
         conditions="NO MATCH: EEA 'Daily NDE' (111 kWh, group 53 van-truck) is eDaily, not S-eWay; eDaily spec page not the same model line as S-eWay",
         cites_vecto=False,
         quote="(no matching S-eWay battery; eDaily is a separate light line)",
         match="NO MATCH: S-eWay battery 280-490 kWh does not match EEA 111 kWh eDaily; recorded as no match"),
]


def main():
    # HDEV V-C mid per config (mean over that config's runs, both corners)
    rows = list(csv.DictReader(open(os.path.join(HERE, "hdev_vs_certified.csv"))))
    vc_by_cfg = defaultdict(list)
    cert_by_cfg = defaultdict(list)
    for r in rows:
        for c in ("lo", "hi"):
            try:
                vc_by_cfg[r["config_id"]].append(float(r["V-C_%s_grid" % c]))
            except (ValueError, KeyError):
                pass
        try:
            cert_by_cfg[r["config_id"]].append(float(r["certified_kwh_km"]))
        except ValueError:
            pass

    out = []
    for o in OEM:
        cid = o["config_id"]
        # OEM-derived kWh/km [D]: usable_kwh / range_km if both present; else stated; else blank
        derived = None
        tag = ""
        if o["oem_kwh_km_stated"] is not None:
            derived = o["oem_kwh_km_stated"]
            tag = "[V] OEM-stated (" + (o["kwh_basis"] or "") + ")"
        elif o["usable_kwh"] and o["range_km"]:
            derived = round(o["usable_kwh"] / o["range_km"], 3)
            tag = "[D] usable_kWh/range = %.1f/%.0f (usable basis)" % (o["usable_kwh"], o["range_km"])
        elif o["installed_kwh"] and o["range_km"]:
            derived = round(o["installed_kwh"] / o["range_km"], 3)
            tag = "[D] installed_kWh/range = %.1f/%.0f (installed basis, overstates)" % (o["installed_kwh"], o["range_km"])
        else:
            tag = "[BOB] OEM page gives no usable kWh + range together; cannot derive"

        vc = vc_by_cfg.get(cid, [])
        certs = cert_by_cfg.get(cid, [])
        out.append(dict(
            config_id=cid, make=o["make"], oem_model_gen=o["model_gen"],
            certified_kwh_km=round(statistics.median(certs), 4) if certs else "",
            hdev_VC_lo=round(min(vc), 3) if vc else "", hdev_VC_hi=round(max(vc), 3) if vc else "",
            hdev_VC_mid=round(statistics.median(vc), 3) if vc else "",
            oem_kwh_km=derived if derived is not None else "",
            oem_installed_kwh=o["installed_kwh"] or "", oem_usable_kwh=o["usable_kwh"] or "",
            oem_range_km=o["range_km"] or "", oem_conditions=o["conditions"],
            oem_cites_vecto="yes" if o["cites_vecto"] else "no",
            oem_url=o["url"], oem_date=o["date"], oem_quote=o["quote"],
            match_note=o["match"], tags=tag))

    cols = ["config_id", "make", "oem_model_gen", "certified_kwh_km", "hdev_VC_lo",
            "hdev_VC_mid", "hdev_VC_hi", "oem_kwh_km", "oem_installed_kwh", "oem_usable_kwh",
            "oem_range_km", "oem_conditions", "oem_cites_vecto", "oem_url", "oem_date",
            "oem_quote", "match_note", "tags"]
    with open(os.path.join(HERE, "three_way.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("wrote three_way.csv with", len(out), "OEM entries")
    for r in out:
        print(" ", r["make"], r["config_id"], "cert=", r["certified_kwh_km"],
              "HDEV V-C=", r["hdev_VC_mid"], "OEM=", r["oem_kwh_km"], "|", r["tags"][:40])


if __name__ == "__main__":
    main()
