"""Verify latent-state conditioning by independent rational Bayes calculations."""
import importlib.util
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import numpy as np

path = Path(__file__).resolve().parents[1] / "notebooks" / "02_misclassification.py"
spec = importlib.util.spec_from_file_location("misclassification", path)
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)
for sensor, correct, tickets in [
    ("2 of 3 correct (source)", 2, 3),
    ("1 of 2 correct (uninformative)", 1, 2),
    ("Always correct", 1, 1),
]:
    for report in ("Blue", "White"):
        _, d = lesson.app.run(defs={"sensor": SimpleNamespace(value=sensor), "report": SimpleNamespace(value=report)})
        assert len(d["paths"]) == 4*tickets
        assert np.isclose(d["joint_table"]["Joint probability"].sum(), 1)
        for chart in ("joint_chart", "posterior_chart"):
            assert d[chart].to_dict(validate=True)["$schema"]
        if tickets == 3:
            assert d["report_probability"] == (Fraction(7,12) if report == "Blue" else Fraction(5,12))
            assert d["posterior_blue"] == (Fraction(6,7) if report == "Blue" else Fraction(3,5))
        if tickets == 2:
            assert d["posterior_blue"] == Fraction(3,4)
        if tickets == 1:
            assert d["posterior_blue"] == int(report == "Blue")
        # Test other base rates as well as the notebook's fixed known bag.
        for blue in (1, 2, 3):
            p, accuracy = Fraction(blue,4), Fraction(correct,tickets)
            likelihood_blue = accuracy if report == "Blue" else 1-accuracy
            likelihood_white = 1-accuracy if report == "Blue" else accuracy
            evidence = p*likelihood_blue + (1-p)*likelihood_white
            posterior = p*likelihood_blue/evidence
            paths = d["enumerate_reports"](blue, correct, tickets)
            assert d["infer_true_blue"](paths, report) == (evidence, posterior)
# Reconstruct the final R block literally, including its reversed parent index.
r_paths = []
for j in range(1, 5):
    parent = 5-j  # R is one-indexed: parents 1,2,3 blue; parent 4 white.
    reports = ("White", "White", "Blue") if j == 1 else ("Blue", "Blue", "White")
    r_paths.extend(("Blue" if parent <= 3 else "White", value) for value in reports)
python_paths = d["enumerate_reports"](3, 2, 3)
from collections import Counter
assert Counter(r_paths) == Counter((p["True color"], p["Reported color"]) for p in python_paths)
print("PASS: six UI states, 18 rational Bayes cases, literal R parent/report mapping; source P(report blue)=7/12 and P(true blue | report blue)=6/7")
