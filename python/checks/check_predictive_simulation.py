"""Check the complete reactive lesson against independent integration and moments."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy import integrate, stats

path = Path(__file__).resolve().parents[1] / "notebooks" / "02_predictive_simulation.py"
spec = importlib.util.spec_from_file_location("predictive", path)
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)

for mode, a, b in (("Posterior", 7, 4), ("Prior", 1, 1)):
    previous_p = previous_water = None
    for size in (50, 500, 5000, 50000):
        _, d = lesson.app.run(defs={"mode": SimpleNamespace(value=mode), "sample_count": SimpleNamespace(value=size)})
        assert (d["a"], d["b"]) == (a, b)
        assert d["p_draws"].shape == d["water_draws"].shape == (50000,)
        assert np.all((d["p_draws"] >= 0) & (d["p_draws"] <= 1))
        assert np.all((d["water_draws"] >= 0) & (d["water_draws"] <= 9))
        assert d["water_draws"].dtype.kind in "iu"
        assert d["observed_counts"].sum() == size
        assert d["selected_water"] == d["water_draws"][size - 1]
        assert d["selected_p"] == d["p_draws"][size - 1]
        np.testing.assert_allclose(d["conditional_data"]["Probability"].sum(), 1)
        assert d["three_panel"].to_dict(validate=True)["$schema"]
        if previous_p is not None:
            np.testing.assert_array_equal(d["p_draws"], previous_p)
            np.testing.assert_array_equal(d["water_draws"], previous_water)
        previous_p, previous_water = d["p_draws"], d["water_draws"]
    # Integrate the hierarchy independently of scipy.stats.betabinom.
    quadrature = np.array([
        integrate.quad(lambda p: stats.binom.pmf(k, 9, p) * stats.beta.pdf(p, a, b), 0, 1)[0]
        for k in range(10)
    ])
    np.testing.assert_allclose(d["exact"], quadrature, atol=1e-12)
    if mode == "Prior":
        np.testing.assert_allclose(quadrature, np.full(10, 0.1), atol=1e-12)
    empirical = np.bincount(d["water_draws"], minlength=10) / 50000
    # Six binomial standard errors per category, plus one count for discreteness.
    tolerance = 6 * np.sqrt(quadrature * (1 - quadrature) / 50000) + 1 / 50000
    assert np.all(np.abs(empirical - quadrature) < tolerance)
    assert abs(d["p_draws"].mean() - a / (a + b)) < 6 * np.sqrt(stats.beta.var(a, b) / 50000)
    assert abs(d["water_draws"].mean() - d["predictive_mean"]) < 6 * np.sqrt(d["predictive_variance"] / 50000)
    np.testing.assert_allclose(quadrature @ (np.arange(10) - d["predictive_mean"]) ** 2, d["predictive_variance"])
    for actual, repeated in zip((d["p_draws"], d["water_draws"]), d["simulate_predictive"](a, b)):
        np.testing.assert_array_equal(actual, repeated)
    print(f"PASS {mode}: 4 controls, 50000 seeded draws, quadrature, moments; max frequency error {max(abs(empirical-quadrature)):.5f}")
