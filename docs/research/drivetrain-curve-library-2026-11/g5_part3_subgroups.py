"""Part 3: Group 5 subgroup class bands, using the same application test as Part 2.

Groupings: architecture, IEPC gear count, IEPC maximum-continuous power bins, make. All Group 5 configs are E-IEPC;
"IEPC" is the normalized architecture label. Continuous power comes from EEA `vehicles_xev.csv` column
`iepc_max_cont_kw` for the same median-mass vehicle selected by harness.config_runs(). It is never imputed.

[ASSUMPTION] Bins: <200, 200–<300, 300–<400, 400–<500, >=500 kW. They are fixed 100 kW bands, chosen before
examining errors. Model-weighted and config-unweighted versions are both written. A subgroup with <3 distinct model
names is flagged `not_reliable`.

Outputs: g5_subgroups.csv, g5_subgroups_config_errors.csv, g5_subgroup_widths.csv
"""
import csv
import glob
import os
from collections import defaultdict

import numpy as np

import harness as HN
import part3_loo as P3

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
PARAMS = {"C": ("eta_d", "eta_r", "F0_N"), "L4b": ("a_W", "b_perW", "c_W_per_mps")}


def read(path): return list(csv.DictReader(ln for ln in open(path) if not ln.startswith("#")))
def write(path, rows):
    with open(path, "w", newline="") as fh:
        fh.write(ATTR + "\n")
        fields = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print("wrote", path)


def get_records():
    by = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(HN.CACHE, "records_g5_??_range_mid.npz"))):
        rr, _ = HN._load_npz(p)
        for r in rr: by[r["config_id"]].append(r)
    for rr in by.values(): rr.sort(key=lambda r: (r["mission"],r["payload"]))
    return by


def get_fits():
    d=defaultdict(dict)
    for r in read(os.path.join(HERE,"g5_fits.csv")):
        vals=tuple(float(r[p]) for p in PARAMS[r["method"]])
        d[r["method"]][r["config_id"]]=dict(values=vals, cdxa=float(r["cdxa_declared_m2"]) if r["cdxa_declared_m2"] else None,
                                                model=r["model"], make=r["make"], gears=int(r["gears"]))
    return d


def kw_continuous(cid):
    vid, _ = HN.config_runs(cid)
    x=HN._state()["veh_extra"].get(vid,{ }).get("iepc_max_cont_kw","")
    try: return float(x)
    except (TypeError,ValueError): return None


def kw_bin(x):
    if x is None: return "BLOCKED: missing IEPC continuous kW"
    if x < 200: return "<200"
    if x < 300: return "200–<300"
    if x < 400: return "300–<400"
    if x < 500: return "400–<500"
    return "≥500"


def theta(rec, tag, vals, own_cdxa):
    m=P3.make(tag,rec)
    return m, tuple(vals)+((own_cdxa,) if rec["airdrag_measured"] else ())


def main():
    P3.set_bounds(); HN.AIRDRAG_MODE="range_mid"
    by, fits=get_records(),get_fits()
    labels={}
    for cid,rr in by.items():
        f=fits["C"][cid]
        labels[cid]=dict(architecture="IEPC", gears="g%d"%f["gears"], continuous_kw=kw_continuous(cid),
                         continuous_kw_bin=kw_bin(kw_continuous(cid)), make=f["make"], model=f["model"])
    rows=[]; errors=[]; widths=[]
    for tag in ("C","L4b"):
      for grouping, labelkey in (("architecture","architecture"),("gears","gears"),("continuous_kw_bin","continuous_kw_bin"),("make","make")):
        members=defaultdict(list)
        for cid in by: members[labels[cid][labelkey]].append(cid)
        for subgroup,cids in sorted(members.items()):
          nmodels=len(set(labels[c]["model"] for c in cids)); reliable=nmodels>=3
          if subgroup.startswith("BLOCKED"):
            rows.append(dict(method=tag,grouping=grouping,subgroup=subgroup,n_configs=len(cids),n_models=nmodels,reliability="BLOCKED",reason=subgroup)); continue
          for weighting in ("config_unweighted","model_weighted"):
            if weighting=="config_unweighted": vals=np.array([fits[tag][c]["values"] for c in cids])
            else:
              mm=defaultdict(list)
              for c in cids:mm[labels[c]["model"]].append(fits[tag][c]["values"])
              vals=np.array([np.mean(x,axis=0) for x in mm.values()])
            qs={q:np.percentile(vals,q,axis=0) for q in (10,50,90)}
            for q,v in qs.items():
              ce=[]
              for cid in cids:
                rr=by[cid]; m,th=theta(rr[0],tag,v,fits[tag][cid]["cdxa"])
                e=np.array([m.predict(r,th)/r["cert"]-1 for r in rr])
                mean=100*float(np.mean(e)); ce.append(mean)
                errors.append(dict(method=tag,grouping=grouping,subgroup=subgroup,weighting=weighting,percentile="P%d"%q,
                                   config_id=cid,model=labels[cid]["model"],mean_err_pct=round(mean,3),worst_abs_err_pct=round(100*float(max(abs(e))),3)))
              ce=np.array(ce)
              row=dict(method=tag,grouping=grouping,subgroup=subgroup,weighting=weighting,percentile="P%d"%q,n_configs=len(cids),n_models=nmodels,
                       reliability="reliable" if reliable else "not_reliable (<3 models)", mean_config_error_pct=round(float(ce.mean()),3),
                       p10_config_error_pct=round(float(np.percentile(ce,10)),3),p50_config_error_pct=round(float(np.median(ce)),3),
                       p90_config_error_pct=round(float(np.percentile(ce,90)),3),width_p90_minus_p10_pp=round(float(np.percentile(ce,90)-np.percentile(ce,10)),3),
                       worst_config_mean_error_pct=round(float(max(abs(ce))),3))
              row.update({p:round(x,9) for p,x in zip(PARAMS[tag],v)}); rows.append(row)
              if q==50 and weighting=="model_weighted": widths.append(dict(method=tag,grouping=grouping,subgroup=subgroup,n_configs=len(cids),n_models=nmodels,
                                                                                reliability=row["reliability"],width_p90_minus_p10_pp=row["width_p90_minus_p10_pp"],worst_config_mean_error_pct=row["worst_config_mean_error_pct"]))
    write(os.path.join(HERE,"g5_subgroups.csv"),rows); write(os.path.join(HERE,"g5_subgroups_config_errors.csv"),errors); write(os.path.join(HERE,"g5_subgroup_widths.csv"),widths)
    for tag in ("C","L4b"):
        best=sorted([r for r in widths if r["method"]==tag and r["reliability"]=="reliable"], key=lambda r:r["width_p90_minus_p10_pp"])
        print(tag,"narrowest reliable:",best[0] if best else "none")

if __name__=="__main__": main()
