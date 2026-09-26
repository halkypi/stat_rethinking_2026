"""Check unequal path denominators using exact rational Bernoulli likelihoods."""
import importlib.util
import itertools
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

path = Path(__file__).resolve().parents[1] / "notebooks" / "02_garden_sizes.py"
spec = importlib.util.spec_from_file_location("garden_sizes", path)
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)
for n_seen in range(4):
    _, d = lesson.app.run(defs={"step": SimpleNamespace(value=n_seen)})
    assert d["results"][0][2] == d["results"][1][2] == Fraction(1, 2**n_seen)
    assert d["likelihood_chart"].to_dict(validate=True)["$schema"]
assert d["results"] == [(8, 64, Fraction(1, 8)), (27, 216, Fraction(1, 8))]
checks = 0
for size in (4, 6):
    for blue in range(size + 1):
        for n_seen in range(4):
            for data in itertools.product((0, 1), repeat=n_seen):
                good, total, actual = d["garden_probability"](size, blue, data)
                p = Fraction(blue, size)
                expected = p ** sum(data) * (1-p) ** (len(data)-sum(data))
                assert actual == expected
                assert 0 <= good <= total == size ** n_seen
                checks += 1
print(f"PASS: all four notebook states and {checks} exact sequence/bag cases, including all-blue and all-white boundaries")
