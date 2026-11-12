"""Run every script of the force-engine review in order (about 1 minute). Prints the files each script wrote.

    VECTO_SRC=/path/to/VECTO python run_all.py          (VECTO_SRC only needed by Gate 1)
"""
import subprocess
import sys

SCRIPTS = ["run_gates_1_2.py", "run_part_a_b_numbers.py", "run_part_c.py", "run_part_d.py", "run_part_e.py",
           "run_part_f.py", "run_part_g_conventions.py", "run_part_j.py", "run_graphs.py", "make_tables.py"]
for s in SCRIPTS:
    print("=" * 20, s)
    r = subprocess.run([sys.executable, s])
    if r.returncode:
        sys.exit(r.returncode)
