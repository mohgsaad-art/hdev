"""Build wireframes/input-map.html: every sheet with every input and result, from inputs_ux.csv and results_ux.csv."""
import csv, json, re, html
from pathlib import Path
here = Path(__file__).resolve().parent.parent

CTRL = [
 ("Typeable precise value", "Number field with unit"),
 ("Visible radio group", "Radio choice (opens/closes fields)"),
 ("Visible source radio group", "Source choice + value"),
 ("Editable grid", "Table"),
 ("Searchable structured picker", "Searchable picker"),
 ("Read-only calculated", "Read-only (calculated)"),
 ("Visible checkbox", "Checkbox"),
 ("File upload", "File upload"),
 ("Map search", "Map + ordered list"),
 ("Authoritative editable point grid", "Profile table + preview chart"),
 ("Typeable 24-hour", "Time field (hh:mm)"),
 ("Persistent-label text", "Text field"),
 ("PARKED", "Parked: equipment form"),
 ("Grouped exact ratio", "Grouped number fields"),
 ("Reusable fleet-group", "Fleet group card"),
 ("Checkboxes for independent", "Checkboxes + number fields"),
]
def ctrl(s):
    for k, v in CTRL:
        if s.startswith(k): return v
    return re.split(r" \(DP", s)[0]

TIER = {"always visible": "On the sheet", "one step away": "One step away",
        "expert view": "Expert view", "never shown; available in Inputs and sources ledger": "Never shown as a field"}

def short_default(s):
    s = s.replace("Pre-filled only by Python with Default/Assumption mark; ", "").replace("Empty; ", "")
    return s

inp = list(csv.DictReader(open(here/"inputs_ux.csv", encoding="utf-8")))
res = list(csv.DictReader(open(here/"results_ux.csv", encoding="utf-8")))
rows = [{"k":"in","id":x["id"],"page":x["page"],"sec":x["section"],"tier":TIER.get(x["tier"],x["tier"]),
         "label":x["label"],"ctrl":ctrl(x["control"]),"unit":"" if x["unit_ui"]=="none" else x["unit_ui"],
         "st":x["map_status"],"req":x["required"],"opt":x["options"],"def":short_default(x["default_behaviour"]),
         "open":x["appears_when"],"close":x["closes_when"],"views":x["views"],"help":x["help_text"]} for x in inp]
rows += [{"k":"out","id":x["id"],"page":x["page"],"sec":x["level"],"label":x["result"],"unit":x["unit"],
          "st":"now" if x["available"]=="now" else "planned","form":x["form"],"q":x["question_it_answers"],
          "cmp":x["compare_with"],"unc":x["uncertainty"],"drill":x["drill_down_to"]} for x in res]

GROUPS = ["Setup","Duties","Conditions","Energy chain","Site","Business case","Findings"]
ORDER = ["Setup / Start and purpose","Setup / Scenarios","Duties / Fleet groups","Duties / Vehicle","Duties / Route and stops",
 "Duties / Load and body equipment","Duties / Schedule and calendar","Conditions / Weather and cab climate",
 "Energy chain / Battery and ageing","Energy chain / Charging","Site / Depot and grid","Site / Flexibility",
 "Business case / Prices and tariffs","Business case / Costs and finance","Business case / Taxes and CO2",
 "Business case / Tender and bids","Findings / Decision","Findings / Energy and duty","Findings / Battery and payload",
 "Findings / Charging and resilience","Findings / Site and flexibility","Findings / Cost and CO2","Findings / Compare",
 "Findings / Inputs and sources","Findings / Documents"]
pages = [p for p in ORDER if p in {r["page"] for r in rows} or p=="Setup / Start and purpose"]
extra = sorted({r["page"] for r in rows} - set(ORDER)); pages += extra

tpl = (here/"tools"/"input_map_template.html").read_text(encoding="utf-8")
out = tpl.replace("__DATA__", json.dumps(rows, ensure_ascii=False)).replace("__PAGES__", json.dumps(pages)).replace("__GROUPS__", json.dumps(GROUPS))
(here/"wireframes"/"all-sheets.html").write_text(out, encoding="utf-8")
print(len(inp), "inputs,", len(res), "results,", len(pages), "pages")
