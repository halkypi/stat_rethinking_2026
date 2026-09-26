"""Independent combinatorial and distribution checks of the random-walk lesson."""
import importlib.util
import itertools
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy import stats

path = Path(__file__).resolve().parents[1] / "notebooks" / "03_gaussian_sums.py"
spec = importlib.util.spec_from_file_location("gaussian_sums", path)
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)
for n in (0, 1, 2, 5, 10, 25, 50, 99):
    _, d = lesson.app.run(defs={"steps": SimpleNamespace(value=n)})
    assert d["walks"].shape == (1000, 100)
    assert d["endpoint_chart"].to_dict(validate=True)["$schema"]
    assert d["path_chart"].to_dict(validate=True)["$schema"]
    np.testing.assert_array_equal(d["walks"], d["simulate_walks"]())
for n in range(100):
    x = d["walks"][:,n]
    support, exact, normal = d["endpoint_distribution"](n)
    assert np.all(abs(x) <= n) and np.all((x-n) % 2 == 0)
    np.testing.assert_allclose(exact, stats.binom.pmf(np.arange(n+1), n, .5), atol=1e-14)
    np.testing.assert_allclose(exact, exact[::-1])
    np.testing.assert_allclose([exact.sum(), exact @ support, exact @ support**2], [1, 0, n], atol=1e-12)
    assert abs(x.mean()) <= 6*np.sqrt(n/1000) + 1e-12
    assert abs(np.mean(x*x)-n) <= 6*np.sqrt(2*n*(n-1)/1000) + 1e-12
    empirical = np.array([(x == v).mean() for v in support])
    assert np.all(abs(empirical-exact) <= 6*np.sqrt(exact*(1-exact)/1000) + 1/1000)
    if n <= 8:
        totals = np.array([sum(path) for path in itertools.product((-1,1), repeat=n)])
        np.testing.assert_allclose([(totals==v).mean() for v in support], exact)
_, exact1, normal1 = d["endpoint_distribution"](1)
_, exact50, normal50 = d["endpoint_distribution"](50)
assert abs(exact50-normal50).sum() < abs(exact1-normal1).sum()
print("PASS: eight notebook controls, all 100 step counts, exact enumeration through 8 moves, seeded moments/support, normal approximation convergence")
