"""Fills report_template.md with the generated tables -> ../drivetrain-shape-direct-daf-2026-11.md"""
import json
import os

import build_report_tables as B
import lib_g5 as L

HERE = L.HERE


def main():
    B.main()
    T = json.load(open(os.path.join(HERE, "report_tables.json")))
    boot = L.read(os.path.join(HERE, "final_bootstrap.csv"))
    rows = [r for r in boot if r["universe"].startswith("all") and r["method"].startswith("DIFF") and r["method"].endswith("minus C [CdxA own]")
            and any(k in r["method"] for k in ("L4b [", "L1[S3b", "L1b[S3b", "L1[S2_busIEPC_ASM", "L1[S3a", "L1[S2_busIEPC_PSM", "B0", "B1"))]
    rows += [r for r in boot if r["universe"].startswith("without") and r["method"].startswith("DIFF") and r["method"].endswith("minus class-P50 C [CdxA own]")
             and any(k in r["method"] for k in ("L4b [", "L1[S3b", "L1b[S3b"))]
    T["DIFF1"] = B.md([dict(u=r["universe"], m=r["method"].replace("DIFF ", "").replace(" minus ", " **minus** "), d=B.f(r["width_pp"], 1, True),
                            ci="%s to %s" % (B.f(r["width_ci95_lo"], 1, True), B.f(r["width_ci95_hi"], 1, True))) for r in rows],
                       ["u", "m", "d", "ci"], ["models", "comparison", "width difference pp", "95 % interval"])
    pw = L.read(os.path.join(HERE, "p3_pairwise.csv"))
    sel = [r for r in pw if "(CdxA mid)" in r["physics"] and "L4b" not in r["physics"]]
    T["PAIR"] = B.md([dict(u=r["universe"], p=r["physics"].replace("class-P50 ", ""), b=r["baseline"], a=r["physics_median_abs_model_err_pct"], c=r["baseline_median_abs_model_err_pct"],
                           am=r["physics_mean_abs_model_err_pct"], cm=r["baseline_mean_abs_model_err_pct"], w="%s / %s" % (r["models_where_physics_is_closer"], r["n_models"])) for r in sel],
                     ["u", "p", "b", "a", "c", "am", "cm", "w"],
                     ["models", "physics", "baseline", "physics median abs model err %", "baseline median", "physics mean abs model err %", "baseline mean", "physics closer on"])
    s = open(os.path.join(HERE, "report_template.md")).read()
    for k, v in T.items():
        s = s.replace("{{%s}}" % k, v)
    assert "{{" not in s, [x for x in s.split("{{")[1:3]]
    out = os.path.abspath(os.path.join(HERE, "..", "drivetrain-shape-direct-daf-2026-11.md"))
    open(out, "w").write(s)
    print("wrote", out, len(s.splitlines()), "lines")


if __name__ == "__main__":
    main()
