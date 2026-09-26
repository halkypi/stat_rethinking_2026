"""Verify sequential Beta updates and credible intervals without hidden state."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy import integrate, stats

path = Path(__file__).resolve().parents[1] / "notebooks" / "02_beta_updating.py"
spec = importlib.util.spec_from_file_location("beta_updating", path)
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)

scenarios = [
    ("Six water, three land", (1, 0, 1, 1, 1, 0, 1, 0, 1)),
    ("Interval example: one water, three land", (1, 0, 0, 0)),
]
for label, data in scenarios:
    for n in range(len(data) + 1):
        _, d = lesson.app.run(defs={
            "sequence_choice": SimpleNamespace(value=label),
            "interval_mass": SimpleNamespace(value=0.99),
            "sequence": data, "step": SimpleNamespace(value=n),
        })
        w, l = sum(data[:n]), n - sum(data[:n])
        assert (d["a"], d["b"]) == (1 + w, 1 + l)
        assert d["parameter_history"].shape == (len(data) + 1, 2)
        # Normalize the ordered Bernoulli likelihood under a flat prior,
        # independently of the Beta parameter-update formula.
        z = integrate.quad(lambda p: p**w * (1-p)**l, 0, 1)[0]
        grid = np.linspace(0, 1, 101)
        np.testing.assert_allclose(stats.beta.pdf(grid, d["a"], d["b"]), grid**w * (1-grid)**l / z, atol=1e-12)
        assert d["density_chart"].to_dict(validate=True)["$schema"]
        assert d["draws"].shape == (10000,)
        np.testing.assert_array_equal(d["draws"], np.random.default_rng(2026).beta(1+w, 1+l, 10000))
        np.testing.assert_allclose(stats.beta.cdf(d["exact_interval"], 1+w, 1+l), [0.005, 0.995], atol=1e-12)
        empirical_cdf = stats.beta.cdf(d["sample_interval"], 1+w, 1+l)
        assert np.max(abs(empirical_cdf - [0.005, 0.995])) < 6*np.sqrt(0.005*0.995/10000) + 1/10000
        majority = integrate.quad(lambda p: p**w * (1-p)**l / z, 0.5, 1)[0]
        np.testing.assert_allclose(d["water_majority"], majority, atol=1e-12)
    np.testing.assert_array_equal(d["posterior_parameters"](data)[-1], d["posterior_parameters"](tuple(reversed(data)))[-1])
    widths = []
    for mass in (0.5, 0.89, 0.99):
        # Let the actual sequence and slider cells execute to check their defaults.
        _, d = lesson.app.run(defs={"sequence_choice": SimpleNamespace(value=label), "interval_mass": SimpleNamespace(value=mass)})
        bounds = d["exact_interval"]
        area = integrate.quad(lambda p: stats.beta.pdf(p, d["a"], d["b"]), *bounds)[0]
        assert np.isclose(area, mass)
        widths.append(bounds[1] - bounds[0])
    assert np.all(np.diff(widths) > 0)
    print(f"PASS {label}: every prefix, three interval levels, likelihood quadrature, seeded quantiles; 99% interval {d['exact_interval']}")
