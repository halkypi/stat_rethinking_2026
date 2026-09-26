"""Run all Week 2 fidelity checks in isolated Python processes."""
from pathlib import Path
import subprocess
import sys

checks = Path(__file__).resolve().parent
for name in (
    "check_garden.py",
    "check_garden_sizes.py",
    "check_misclassification.py",
    "check_beta_updating.py",
    "check_predictive_simulation.py",
):
    print(f"\nRunning {name}", flush=True)
    subprocess.run([sys.executable, str(checks / name)], check=True)
print("\nAll five Week 2 lessons passed.")
