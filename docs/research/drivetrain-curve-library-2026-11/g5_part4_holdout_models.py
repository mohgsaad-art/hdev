"""Part 4: hold out one Group 5 MODEL at a time.

Class P50: model-weighted median parameters across every OTHER model. Best subgroup from Part 3: `make` (it gave
Volvo the narrowest reliable P50 application band: 3.00 pp C / 3.30 pp L4b). For the subgroup case, median
parameters use only other models of the held-out model's make. A result with fewer than 3 donor models is labelled
not_reliable; no donor model is BLOCKED. Target CdxA stays the target config's own fitted CdxA.

Outputs: g5_holdout_model.csv, g5_holdout_model_summary.csv
"""
import csv
import glob
import os
from collections import defaultdict

import numpy as np

import harness as HN
import part3_loo as P3

HERE=os.path.dirname(os.path.abspath(__file__))
ATTR=("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
      "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")
PARAMS={"C":("eta_d","eta_r","F0_N"),"L4b":("a_W","b_perW","c_W_per_mps")}

def read(p): return list(csv.DictReader(ln for ln in open(p) if not ln.startswith('#')))
def write(p,rows):
 with open(p,'w',newline='') as fh:
  fh.write(ATTR+'\n'); f=list(dict.fromkeys(k for r in rows for k in r)); w=csv.DictWriter(fh,fieldnames=f);w.writeheader();w.writerows(rows)
 print('wrote',p)
def records():
 d=defaultdict(list)
 for p in sorted(glob.glob(os.path.join(HN.CACHE,'records_g5_??_range_mid.npz'))):
  rr,_=HN._load_npz(p)
  for r in rr:d[r['config_id']].append(r)
 for x in d.values():x.sort(key=lambda r:(r['mission'],r['payload']))
 return d
def fits():
 out=defaultdict(dict)
 for r in read(os.path.join(HERE,'g5_fits.csv')):
  out[r['method']][r['config_id']]=dict(values=tuple(float(r[p]) for p in PARAMS[r['method']]),cdxa=float(r['cdxa_declared_m2']) if r['cdxa_declared_m2'] else None,model=r['model'],make=r['make'])
 return out
def theta(rec,tag,vals,cdxa):
 m=P3.make(tag,rec);return m,tuple(vals)+((cdxa,) if rec['airdrag_measured'] else ())
def model_params(ft, donors):
 mm=defaultdict(list)
 for cid in donors:mm[ft[cid]['model']].append(ft[cid]['values'])
 if not mm:return None,0
 return np.median(np.array([np.mean(x,axis=0) for x in mm.values()]),axis=0),len(mm)
def main():
 P3.set_bounds();HN.AIRDRAG_MODE='range_mid';by,ft=records(),fits();rows=[]
 for tag in ('C','L4b'):
  d=ft[tag];models=sorted(set(x['model'] for x in d.values()))
  for target in models:
   tc=[c for c in d if d[c]['model']==target]; make=d[tc[0]]['make']
   specs=[('class',[c for c in d if d[c]['model']!=target]),('make_subgroup',[c for c in d if d[c]['model']!=target and d[c]['make']==make])]
   for source,donors in specs:
    vals,nmodels=model_params(d,donors)
    if vals is None:
     rows.append(dict(method=tag,source=source,target_model=target,target_make=make,n_target_configs=len(tc),n_donor_configs=0,n_donor_models=0,reliability='BLOCKED: no donor model',mean_err_pct='',mean_abs_err_pct='',worst_abs_err_pct='',share_too_low='',n_predictions='',params=''));continue
    es=[]
    for cid in tc:
     rr=by[cid];m,th=theta(rr[0],tag,vals,d[cid]['cdxa']);es.extend([m.predict(r,th)/r['cert']-1 for r in rr])
    e=np.array(es)
    rows.append(dict(method=tag,source=source,target_model=target,target_make=make,n_target_configs=len(tc),n_donor_configs=len(donors),n_donor_models=nmodels,reliability='reliable' if nmodels>=3 else 'not_reliable (<3 donor models)',mean_err_pct=round(100*float(e.mean()),3),mean_abs_err_pct=round(100*float(abs(e).mean()),3),worst_abs_err_pct=round(100*float(max(abs(e))),3),share_too_low=round(float(np.mean(e<0)),3),n_predictions=len(e),params=';'.join('%.8g'%x for x in vals)))
 write(os.path.join(HERE,'g5_holdout_model.csv'),rows)
 su=[]
 for tag in ('C','L4b'):
  for source in ('class','make_subgroup'):
   x=[r for r in rows if r['method']==tag and r['source']==source and r['mean_err_pct']!='']
   e=np.array([float(r['mean_err_pct']) for r in x]);w=np.array([float(r['worst_abs_err_pct']) for r in x])
   su.append(dict(method=tag,source=source,n_models=len(x),n_reliable=sum(r['reliability']=='reliable' for r in x),mean_of_model_mean_err_pct=round(float(e.mean()),3),p10_model_mean_err_pct=round(float(np.percentile(e,10)),3),p50_model_mean_err_pct=round(float(np.median(e)),3),p90_model_mean_err_pct=round(float(np.percentile(e,90)),3),width_p90_minus_p10_pp=round(float(np.percentile(e,90)-np.percentile(e,10)),3),worst_model_abs_error_pct=round(float(w.max()),3)))
 write(os.path.join(HERE,'g5_holdout_model_summary.csv'),su)
 for r in su:print(r)
if __name__=='__main__':main()
