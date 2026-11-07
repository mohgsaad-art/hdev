"""Summarise hdev_vs_certified.csv: error distributions per variant / architecture /
mission / certification method, CdxA-range containment, and flag shares. Writes
summary_stats.md and prints the headline numbers."""
import csv
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ["V-A", "V-B", "V-C", "V-D"]


def pct(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    k = max(0, min(len(vals) - 1, int(round(p / 100 * (len(vals) - 1)))))
    return vals[k]


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "hdev_vs_certified.csv"))))
    print("runs:", len(rows))

    # for each variant use the mean of lo/hi grid as the point estimate; the corner range is lo..hi
    def grid_vals(r, v):
        out = []
        for c in ("lo", "hi"):
            x = r["%s_%s_grid" % (v, c)]
            if x not in ("", None):
                try:
                    out.append(float(x))
                except ValueError:
                    pass
        return out

    lines = []
    lines.append("# HDEV vs certified: summary statistics (Job 3)\n")
    lines.append("Error = (HDEV grid-side kWh/km - certified kWh/km) / certified, in %. ")
    lines.append("Each run has two CdxA corners (low/high edge); the point error below uses ")
    lines.append("the mid of the two corners. 'in range' = certified falls between the low and ")
    lines.append("high CdxA HDEV values.\n")

    # overall per variant
    lines.append("## Per variant (all runs)\n")
    lines.append("| variant | n | median % | 10th % | 90th % | within +/-5% | within +/-10% | certified in CdxA range |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for v in VARIANTS:
        errs = []
        w5 = w10 = inrange = tot = 0
        for r in rows:
            gv = grid_vals(r, v)
            if len(gv) < 1:
                continue
            cert = float(r["certified_kwh_km"])
            mid = sum(gv) / len(gv)
            e = 100 * (mid - cert) / cert
            errs.append(e)
            tot += 1
            if abs(e) <= 5:
                w5 += 1
            if abs(e) <= 10:
                w10 += 1
            if min(gv) <= cert <= max(gv):
                inrange += 1
        if not errs:
            continue
        lines.append("| %s | %d | %.1f | %.1f | %.1f | %.0f%% | %.0f%% | %.0f%% |" % (
            v, tot, statistics.median(errs), pct(errs, 10), pct(errs, 90),
            100 * w5 / tot, 100 * w10 / tot, 100 * inrange / tot))

    # per architecture x variant (median error)
    def group_table(key, title):
        lines.append("\n## Median %% error by %s\n" % title)
        groups = sorted({r[key] for r in rows})
        lines.append("| %s | " % title + " | ".join(VARIANTS) + " |")
        lines.append("|---|" + "---|" * len(VARIANTS))
        for g in groups:
            cells = []
            for v in VARIANTS:
                errs = []
                for r in rows:
                    if r[key] != g:
                        continue
                    gv = grid_vals(r, v)
                    if not gv:
                        continue
                    cert = float(r["certified_kwh_km"])
                    mid = sum(gv) / len(gv)
                    errs.append(100 * (mid - cert) / cert)
                cells.append("%.1f (n=%d)" % (statistics.median(errs), len(errs)) if errs else "-")
            lines.append("| %s | " % g + " | ".join(cells) + " |")

    group_table("arch", "architecture")
    group_table("mission", "mission")
    group_table("comp_method", "component certification method")

    # flags: driver fails / skips
    lines.append("\n## Flags\n")
    flagc = defaultdict(int)
    for r in rows:
        for v in VARIANTS:
            for c in ("lo", "hi"):
                f = r.get("%s_%s_flag" % (v, c), "")
                if f and ("fail" in f or "skip" in f):
                    flagc[(v, f.split()[0])] += 1
    if flagc:
        for (v, f), n in sorted(flagc.items()):
            lines.append("- %s: %s x%d" % (v, f, n))
    else:
        lines.append("- no driver failures or skipped runs.")
    rrc_missing = sum(1 for r in rows if r.get("rrc_missing", "0") not in ("0", "", "0.0"))
    lines.append("- runs on vehicles with >=1 axle missing RRC/cert-number: %d" % rrc_missing)

    with open(os.path.join(HERE, "summary_stats.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
