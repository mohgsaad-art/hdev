"""Gate 2: is the 13 Nov notebook identical to Appendix 1 / 2 of the prompt?  Also: how stale is src/engine/consumption.py?"""
import ast, difflib, inspect, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from _load_notebook import cell_sources
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

def cell_with(name):
    for i, s in cell_sources():
        if re.search(rf"^def {name}\(", s, re.M):
            return i, s
    raise KeyError(name)

def func_text(src, name):
    m = re.search(rf"^def {name}\(.*?(?=^\S|\Z)", src, re.M | re.S)
    return m.group(0).rstrip()

out = []
a1 = open(os.path.join(HERE, "appendix", "appendix1_consumption_engine.py.txt")).read().rstrip()
i, s = cell_with("consumption_engine")
nbtxt = func_text(s, "consumption_engine")
exact = nbtxt == a1
norm = lambda t: [l.rstrip() for l in t.splitlines()]
out.append(f"consumption_engine (cell {i}) byte-identical to Appendix 1: {exact}")
if not exact:
    for l in difflib.unified_diff(norm(a1), norm(nbtxt), "appendix1", "notebook", lineterm="", n=0): out.append(l)
a2 = open(os.path.join(HERE, "appendix", "appendix2_producers.py.txt")).read().rstrip()
i, s = cell_with("force_engine")
def strip_comments(t):
    return "\n".join(re.sub(r"\s*#.*$", "", l).rstrip() for l in t.splitlines() if re.sub(r"\s*#.*$", "", l).strip())
nb_fe = strip_comments(func_text(s, "force_engine")); ap_fe = strip_comments(a2)
same_code = ast.dump(ast.parse(nb_fe)) == ast.dump(ast.parse(ap_fe))
out.append(f"force_engine (cell {i}) same code as Appendix 2.1 after removing comments: {same_code}")
# the other Appendix-2 functions: compare AST of the prompt copy is not stored; report signatures
from _load_notebook import NS
for n in ("P_aux", "pto_engine", "ssm_total_w", "climate_lookup", "HVAC_thermal", "SP_power_helper"):
    out.append(f"{n}{inspect.signature(NS[n])}")
# src/engine/consumption.py
p = os.path.join(REPO, "src", "engine", "consumption.py")
out.append("--- src/engine/consumption.py vs notebook")
if os.path.exists(p):
    t = open(p).read()
    defs = re.findall(r"^def (\w+)", t, re.M)
    out.append(f"{len(t.splitlines())} lines; defs: {defs}")
    sig = re.search(r"def consumption_engine\((.*?)\):", t, re.S)
    out.append("signature in src: " + (re.sub(r"\s+", " ", sig.group(1)) if sig else "NOT FOUND"))
    nbsig = list(inspect.signature(NS["consumption_engine"]).parameters)
    srcsig = re.findall(r"(\w+)\s*(?:=[^,]*)?(?:,|$)", sig.group(1)) if sig else []
    out.append("params only in notebook: " + str([x for x in nbsig if x not in srcsig]))
    out.append("params only in src: " + str([x for x in srcsig if x not in nbsig]))
print("\n".join(out))
open(os.path.join(HERE, "gate2_result.txt"), "w").write("\n".join(out) + "\n")
print("wrote gate2_result.txt")
