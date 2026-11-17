"""Build prototype/ev-scope-prototype.html from inputs_ux.csv, results_ux.csv and tools/prototype_template.html."""
import csv, json, re
from pathlib import Path
here = Path(__file__).resolve().parent.parent

def ctype(c):
    for k, v in [("Typeable precise value","num"),("Visible radio group","radio"),("Visible source radio group","src"),
                 ("Editable grid","table"),("Searchable structured picker","pick"),("Read-only calculated","ro"),
                 ("Visible checkbox","cb"),("File upload","file"),("Map search","map"),("Authoritative editable point grid","profile"),
                 ("Typeable 24-hour","time"),("Persistent-label text","text"),("PARKED","parked"),("Grouped exact ratio","num"),
                 ("Reusable fleet-group","fleet"),("Checkboxes for independent","cb")]:
        if c.startswith(k): return v
    return "text"

def opts(s):
    p = [x.strip(" ;,.") for x in re.split(r"\s*\(([A-Za-z0-9]{1,2})\)\s*", s)[0::2] if x.strip(" ;,.")]
    if len(p) < 2: p = [x.strip() for x in re.split(r"\s*/\s*|\s*;\s*", s) if x.strip()]
    out = []
    for x in p[:7]:
        x = re.sub(r"\[[^\]]*\]", "", x); x = re.sub(r"\s+", " ", x).strip(" ,;")
        out.append(x[:70] + ("…" if len(x) > 70 else ""))
    return out

def rules(text, verb):
    found = set()
    for sent in re.split(r"(?<=[.;])\s+", text):
        m = re.match(r"Rules? ([\d–\-, and]+)", sent)
        if not m or verb not in sent[:60]: continue
        for part in re.split(r",|and", m.group(1)):
            part = part.strip()
            if not part: continue
            if re.match(r"^\d+[–-]\d+$", part):
                a, b = map(int, re.split(r"[–-]", part)); found.update(range(a, b + 1))
            elif part.isdigit(): found.add(int(part))
    return sorted(found)

TIER = {"always visible":"sheet","one step away":"more","expert view":"expert","never shown; available in Inputs and sources ledger":"ledger"}
inp = list(csv.DictReader(open(here/"inputs_ux.csv", encoding="utf-8")))
res = list(csv.DictReader(open(here/"results_ux.csv", encoding="utf-8")))
I = []
for x in inp:
    t = ctype(x["control"])
    o = opts(x["options"]) if t in ("radio","src","cb") else []
    if t in ("radio","src") and len(o) < 2: t = "num" if x["unit_ui"] not in ("none","") else "text"
    v = x["views"]
    I.append({"id":x["id"],"page":x["page"],"sec":x["section"],"tier":TIER.get(x["tier"],"sheet"),"label":x["label"],
              "t":t,"o":o,"unit":"" if x["unit_ui"]=="none" else x["unit_ui"],"st":x["map_status"],"req":x["required"],
              "def":x["default_behaviour"],"help":x["help_text"],"optsRaw":x["options"],"open":x["appears_when"],"close":x["closes_when"],
              "valid":x["validation"],"views":"all" if v.startswith("client |") else ("oem" if v.startswith("OEM") else "ledger"),
              "ar":rules(x["appears_when"],"appear") if re.match(r"^Rules? \d", x["appears_when"]) else [],
              "cr":[r for r in rules(x["closes_when"],"close") if r not in (46,47)]})
GATE={"rt.saved":["rt.source",[5]],"pto.drive_eff":["pto.drive_kind",[1,2]],"aux.sp_axles":["aux.sp_mode",[0]],"aux.sp_tech":["aux.sp_mode",[0]],
 "chg.power":["chg.chargers",[1]],"chg.count":["chg.chargers",[1]],"chg.type":["chg.chargers",[1]],"chg.caps":["chg.chargers",[1]],
 "chg.strategy":["chg.mode",[1]],"chg.share_rule":["chg.mode",[1]],"chg.step":["chg.mode",[1]]}
for x in I:
    if x["id"] in GATE: x["gate"]=GATE[x["id"]]
R = [{"id":x["id"],"page":x["page"],"lvl":x["level"],"label":x["result"],"unit":x["unit"],"now":x["available"]=="now",
      "form":x["form"],"q":x["question_it_answers"],"cmp":x["compare_with"]} for x in res]
tpl = (here/"tools"/"prototype_template.html").read_text(encoding="utf-8")
out = tpl.replace("/*__INPUTS__*/[]", json.dumps(I, ensure_ascii=False)).replace("/*__RESULTS__*/[]", json.dumps(R, ensure_ascii=False))
(here/"prototype"/"ev-scope-prototype.html").write_text(out, encoding="utf-8")
print(len(I), "inputs", len(R), "results", sum(1 for x in I if x["ar"]), "rule-gated", sum(1 for x in I if x["cr"]), "closable")
