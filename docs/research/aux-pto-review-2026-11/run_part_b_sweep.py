"""Gate 2 + Part B.2: VECTO aux table sweep.

HDEV side  = notebook SP_power_helper + P_aux (loaded unchanged via _load_notebook) fed with values taken
             from the raw VECTO VAUX csv files by the small "parser" below (this is what defaults.py will do).
VECTO side = vecto_aux_reimpl.py (independent re-implementation of the C#, written from the C# only).

Outputs (deterministic):
  gate2_e2_aux.csv           table value -> HDEV electric W -> .vmod W -> difference, per aux, per E2 mission
  sweep_all_combinations.csv every group x mission x technology a PEV lorry can have (+ HDEV vs VECTO W)
  sweep_empty_or_invalid.csv every group x mission (x technology) the tables cannot answer
Run:  python run_part_b_sweep.py
"""
import csv
import itertools
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _load_notebook import NS, REPO  # noqa: E402
import vecto_aux_reimpl as V  # noqa: E402

P_aux = NS["P_aux"]
SP_power_helper = NS["SP_power_helper"]
VAUX = V.VAUX
VMOD_DIR = os.path.join(REPO, "docs", "research", "vecto")

MISSION_COL = {"Long haul": "long haul", "Regional delivery": "regional delivery", "Urban delivery": "urban delivery",
               "Municipal utility": "municipal utility", "Construction": "construction"}


# --------------------------------------------------------------------------------------------
# "parser" for the HDEV side: raw csv strings -> W numbers (no use of vecto_aux_reimpl arithmetic)
# --------------------------------------------------------------------------------------------
def _rows(fn):
    with open(os.path.join(VAUX, fn), encoding="latin-1", newline="") as fh:
        rows = [[c.strip() for c in r] for r in csv.reader(fh) if r and not r[0].strip().startswith("#") and any(c.strip() for c in r)]
    return [c.lower() for c in rows[0]], rows[1:]


def _col(h, name):
    name = " ".join(name.lower().split())
    for i, c in enumerate(h):
        if " ".join(c.split()) == name:
            return i
    raise KeyError(name)


class HdevParser:
    def __init__(self):
        self.es_h, self.es_rows = _rows("ES-Tech.csv")
        self.esm_h, self.esm_rows = _rows("ES-Tech_Medium.csv")
        self.hv_h, self.hv_rows = _rows("HVAC-Table.csv")
        self.ps_h, self.ps_rows = _rows("PS-Table.csv")
        self.spb_h, self.spb_rows = _rows("SP-Table.csv")
        self.spa_h, self.spa_rows = _rows("SP-Axles.csv")
        self.spt_h, self.spt_rows = _rows("SP-Tech.csv")
        self.cd_h, self.cd_rows = _rows("Cond-Table.csv")

    def es(self, group, mission, tech):
        h, rows = (self.esm_h, self.esm_rows) if str(group) in {"51", "52", "53", "54", "55", "56"} else (self.es_h, self.es_rows)
        c = _col(h, mission)
        for r in rows:
            if r[0] == tech:
                if r[c] in ("---", ""):
                    raise LookupError("ES empty cell")
                return float(r[c])
        raise LookupError("ES tech")

    def hvac(self, group, mission, tech):
        c = _col(self.hv_h, mission)
        for r in self.hv_rows:
            if r[0] == tech and r[1].lower() == str(group).lower():
                if r[c] == "":
                    raise LookupError("HVAC empty cell")
                return float(r[c])
        raise LookupError("HVAC row")

    def ps_el(self, mission, tech):
        pev = _col(self.ps_h, "pev")
        c = _col(self.ps_h, mission + "_el")
        for r in self.ps_rows:
            if r[0] == tech:
                if r[pev] != "1":
                    raise LookupError("PS not PEV")
                if r[c] in ("n.a.", ""):
                    raise LookupError("PS empty _el cell")
                return float(r[c])
        raise LookupError("PS tech")

    def sp(self, group, mission, techs):
        c = _col(self.spb_h, mission)
        base = None
        for r in self.spb_rows:
            if r[0].lower() == str(group).lower():
                if r[c] == "":
                    raise LookupError("SP baseline empty cell")
                base = [float(x) for x in r[c].split("/")]
        if base is None:
            raise LookupError("SP group row")
        shares, facs = [], []
        ca = _col(self.spa_h, mission)
        pev = _col(self.spt_h, "pev")
        for i, t in enumerate(techs, start=1):
            rr = [r for r in self.spt_rows if r[0] == t]
            if not rr:
                raise LookupError("SP tech")
            if rr[0][pev] != "1":
                raise LookupError("SP not PEV")
            facs.append([float(rr[0][_col(self.spt_h, k)]) for k in ("uf", "b", "s")])
            ar = [r for r in self.spa_rows if int(r[0]) == i]
            if not ar or ar[0][ca] == "":
                raise LookupError("SP axle share")
            shares.append([float(x) for x in ar[0][ca].split("/")])
        return SP_power_helper(base, shares, facs)       # mechanical W

    def cond(self, mission):
        return float(self.cd_rows[0][_col(self.cd_h, mission)])


def hdev_total(P, group, mission, es_t, hv_t, ps_t, sp_ts):
    es = P.es(group, mission, es_t)
    hv = P.hvac(group, mission, hv_t)
    ps = P.ps_el(mission, ps_t)
    sp = P.sp(group, mission, sp_ts)
    cd = P.cond(mission)
    out = P_aux(es, ps, hv, sp, cd, 0.0)         # default factors of the notebook: 0.7 / 1.0 / 1.25 / 0.7 / 1.0
    return dict(zip(["ES", "PS", "HVAC", "SP", "COND", "PTO"], [float(x) for x in out]))


def vecto_total(group, mission, es_t, hv_t, ps_t, sp_ts):
    return dict(ES=V.es_electric_W(group, mission, es_t), PS=V.ps_electric_W(mission, ps_t),
                HVAC=V.hvac_electric_W(group, mission, hv_t), SP=V.sp_electric_W(group, mission, sp_ts),
                COND=V.cond_electric_W(mission))


# --------------------------------------------------------------------------------------------
# Gate 2
# --------------------------------------------------------------------------------------------
E2 = dict(group="2", es="Standard technology", hv="Default", ps="Vacuum pump + elec. driven", sp=["Full electric steering gear"])
E2_VMOD = {"Long haul": "LongHaul", "Regional delivery": "RegionalDelivery", "Urban delivery": "UrbanDelivery"}


def gate2(P, written):
    rows = []
    for mission, vname in E2_VMOD.items():
        f = os.path.join(VMOD_DIR, f"BEV_E2_{vname}_ReferenceLoad_1Hz.vmod")
        d = pd.read_csv(f, skiprows=1, encoding="utf-8-sig")
        vm = {"ES": d["P_aux_ES_el [kW]"].max() * 1000, "HVAC": d["P_aux_AC_el [kW]"].max() * 1000,
              "PS": d["P_aux_PS_el [kW]"].max() * 1000, "SP": d["P_aux_STP_el [kW]"].max() * 1000,
              "COND": d["P_aux_COND_el [kW]"].max() * 1000}
        tab = dict(ES=P.es("2", mission, E2["es"]), HVAC=P.hvac("2", mission, E2["hv"]), PS=P.ps_el(mission, E2["ps"]),
                   SP=P.sp("2", mission, E2["sp"]), COND=P.cond(mission))
        h = hdev_total(P, "2", mission, E2["es"], E2["hv"], E2["ps"], E2["sp"])
        for a in ["ES", "HVAC", "PS", "SP", "COND"]:
            rows.append(dict(mission=vname, aux=a, table_value_W=round(tab[a], 4), table_meaning="mechanical W" if a in ("ES", "SP") else
                             ("HVAC-Table W (mech-equivalent, x1/0.8)" if a == "HVAC" else "electric W as is"),
                             hdev_electric_W=round(h[a], 4), vmod_W_max_over_rows=round(vm[a], 4),
                             diff_W=round(h[a] - vm[a], 4), vmod_file=os.path.basename(f)))
    df = pd.DataFrame(rows)
    p = os.path.join(HERE, "gate2_e2_aux.csv")
    df.to_csv(p, index=False)
    written.append(p)
    return df


# --------------------------------------------------------------------------------------------
# Sweep
# --------------------------------------------------------------------------------------------
def segment_groups():
    """Valid groups and their missions straight from SegmentTable.csv (mission column != '-')."""
    with open(os.path.join(V.RES, "SegmentTable.csv"), encoding="latin-1", newline="") as fh:
        rows = [r for r in csv.reader(fh)]
    h = [c.strip() for c in rows[0]]
    cols = {m: h.index(m) for m in ["Long haul", "Long haul EMS", "Regional delivery", "Regional delivery EMS", "Urban delivery",
                                    "Municipal utility", "Construction"]}
    out = {}
    for r in rows[1:]:
        if len(r) < len(h) or not r[0].strip() or r[0].strip().startswith("#"):
            continue
        g, valid = r[0].strip(), r[2].strip() == "1"
        ms = out.setdefault(g, dict(valid=valid, veh=set(), missions=set()))
        ms["valid"] = ms["valid"] or valid
        ms["veh"].add(r[3].strip())
        for m, i in cols.items():
            if r[i].strip() not in ("-", ""):
                ms["missions"].add(m.replace(" EMS", ""))
    return out


def main():
    written = []
    P = HdevParser()
    g2 = gate2(P, written)
    print("\nGATE 2 (E2, group 2)")
    print(g2[["mission", "aux", "table_value_W", "hdev_electric_W", "vmod_W_max_over_rows", "diff_W"]].to_string(index=False))

    seg = segment_groups()
    es_techs = [r[0] for r in P.es_rows]
    hv_techs = ["None", "Default"]
    ps_techs = [r[0] for r in P.ps_rows if r[_col(P.ps_h, "pev")] == "1"]
    sp_pev = [r[0] for r in P.spt_rows if r[_col(P.spt_h, "pev")] == "1"]

    # ---- (1) per-component sweep: every group x mission x technology, one row per lookup -------------
    comp_rows, err = [], {}

    def rec(component, g, mission, tech, fh, fv):
        eh = ev = ""
        h = v = float("nan")
        try:
            h = fh()
        except (LookupError, KeyError, ValueError) as e:
            eh = f"{type(e).__name__}: {e}"
        try:
            v = fv()
        except LookupError as e:
            ev = str(e)
        info = seg[g]
        comp_rows.append(dict(component=component, group=g, valid_group=info["valid"],
                              mission_in_segment_table=mission in info["missions"], mission=mission, technology=tech,
                              hdev_electric_W=h, vecto_electric_W=v, diff_W=(h - v) if not (eh or ev) else float("nan"),
                              hdev_error=eh, vecto_error=ev))

    for g in sorted(seg, key=lambda x: (len(x), x)):
        for mission in V.MISSIONS:
            for t in es_techs:
                rec("ES", g, mission, t, lambda: P_aux(P.es(g, mission, t), 0, 0, 0, 0, 0)[0], lambda: V.es_electric_W(g, mission, t))
            for t in hv_techs:
                rec("HVAC", g, mission, t, lambda: P_aux(0, 0, P.hvac(g, mission, t), 0, 0, 0)[2], lambda: V.hvac_electric_W(g, mission, t))
            for t in ps_techs:
                rec("PS", g, mission, t, lambda: P_aux(0, P.ps_el(mission, t), 0, 0, 0, 0)[1], lambda: V.ps_electric_W(mission, t))
            for n_ax in (1, 2, 3, 4):
                for sp_ts in itertools.product(sp_pev, repeat=n_ax):
                    rec("SP", g, mission, f"{n_ax} axle(s): " + " | ".join(sp_ts),
                        lambda: P_aux(0, 0, 0, P.sp(g, mission, sp_ts), 0, 0)[3], lambda: V.sp_electric_W(g, mission, list(sp_ts)))
            rec("COND", g, mission, "Lorry", lambda: P_aux(0, 0, 0, 0, P.cond(mission), 0)[4], lambda: V.cond_electric_W(mission))
    comp = pd.DataFrame(comp_rows)
    answered = comp[(comp["hdev_error"] == "") & (comp["vecto_error"] == "")]
    failed = comp[(comp["hdev_error"] != "") | (comp["vecto_error"] != "")]
    p1 = os.path.join(HERE, "sweep_components.csv")
    comp.to_csv(p1, index=False, float_format="%.6f")
    # ---- (2) compact list of what the tables cannot answer ---------------------------------------
    cl = []
    for (c, g, m), sub in failed.groupby(["component", "group", "mission"], sort=False):
        cl.append(dict(component=c, group=g, valid_group=sub["valid_group"].iloc[0],
                       mission_in_segment_table=sub["mission_in_segment_table"].iloc[0], mission=m,
                       n_technology_rows_failing=len(sub), vecto_error=sub["vecto_error"].iloc[0],
                       hdev_error=sub["hdev_error"].iloc[0],
                       disagree=int(((sub["hdev_error"] == "") != (sub["vecto_error"] == "")).sum())))
    p3 = os.path.join(HERE, "sweep_empty_or_invalid.csv")
    pd.DataFrame(cl).to_csv(p3, index=False)
    written += [p1, p3]
    # ---- (3) full cross-product (all five aux at once), kept in memory: totals must match too --------------
    n_full, max_full = 0, 0.0
    for g in sorted(seg, key=lambda x: (len(x), x)):
        for mission in V.MISSIONS:
            for n_ax in (1, 2, 3, 4):
                for sp_ts in itertools.product(sp_pev, repeat=n_ax):
                    for es_t, hv_t, ps_t in itertools.product(es_techs, hv_techs, ps_techs):
                        try:
                            a = hdev_total(P, g, mission, es_t, hv_t, ps_t, sp_ts)
                            b = vecto_total(g, mission, es_t, hv_t, ps_t, sp_ts)
                        except (LookupError, KeyError, ValueError):
                            continue
                        n_full += 1
                        max_full = max(max_full, max(abs(a[k] - b[k]) for k in b))
    print(f"\nper-component lookups: {len(comp)}; both answered: {len(answered)}; at least one failed: {len(failed)}")
    print(f"max |HDEV - VECTO| over answered component lookups: {answered['diff_W'].abs().max():.3e} W")
    dis = int(((failed['hdev_error'] == '') != (failed['vecto_error'] == '')).sum())
    print(f"lookups where only one side fails (HDEV vs VECTO disagree on validity): {dis}")
    print(f"full cross-product (all 5 aux together, every group x mission x ES x HVAC x PS x SP-axle-tech combination): "
          f"{n_full} answered combinations, max |diff| per aux = {max_full:.3e} W")
    ins = answered[answered["mission_in_segment_table"] & answered["valid_group"]]
    print(f"of the per-component answers, those for a mission that exists for a valid group: {len(ins)}")
    print("\nfiles written:")
    for w in written:
        print("  ", os.path.relpath(w, REPO))


if __name__ == "__main__":
    main()
