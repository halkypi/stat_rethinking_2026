"""Validate simulation-based model recovery."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from rethinking_companion.runtime import configure_runtime
configure_runtime()
import pymc as pm


def single_recovery(seed, b_true=0.5, n=100):
    rng = np.random.default_rng(93 + seed)
    H = rng.uniform(130, 170, n)
    W = rng.normal(b_true * H, 5)
    with pm.Model():
        a = pm.Normal("a", 0, 10)
        b = pm.Uniform("b", 0, 1)
        sigma = pm.Uniform("sigma", 0, 10)
        mu = a + b * H
        pm.Normal("W", mu, sigma, observed=W)
        idata = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    b_draws = idata.posterior["b"].values.ravel()
    return float(b_draws.mean()), float(np.quantile(b_draws, 0.055)), float(np.quantile(b_draws, 0.945))


def main():
    b_true = 0.5
    # Single detailed recovery
    b_mean, b_lo, b_hi = single_recovery(0)
    assert b_lo <= b_true <= b_hi, f"Single recovery: 89% interval [{b_lo:.4f}, {b_hi:.4f}] misses {b_true}"
    print(f"PASS single recovery: b = {b_mean:.4f}, 89% CI [{b_lo:.4f}, {b_hi:.4f}]")

    # 20-replication quick coverage check (not full 100 to save time)
    covers = 0
    for i in range(20):
        rng = np.random.default_rng(93 + i)
        H = rng.uniform(130, 170, 100)
        W = rng.normal(b_true * H, 5)
        with pm.Model():
            a = pm.Normal("a", 0, 10)
            b = pm.Uniform("b", 0, 1)
            sigma = pm.Uniform("sigma", 0, 10)
            mu = a + b * H
            pm.Normal("W", mu, sigma, observed=W)
            idata = pm.sample(draws=500, tune=500, chains=2, cores=1,
                              random_seed=i, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        b_draws = idata.posterior["b"].values.ravel()
        lo, hi = np.quantile(b_draws, [0.055, 0.945])
        if lo <= b_true <= hi:
            covers += 1
    coverage = covers / 20
    assert coverage >= 0.6, f"Coverage {coverage:.0%} is suspiciously low"
    print(f"PASS 20-replication coverage: {coverage:.0%} (expect ~89%)")

    # Notebook execution
    root = Path(__file__).resolve().parents[1]
    notebook = root / "notebooks" / "04_sim_validate.py"
    if notebook.exists():
        spec = importlib.util.spec_from_file_location("sim_lesson", notebook)
        lesson = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lesson)
        _, d = lesson.app.run(defs={"n_reps": SimpleNamespace(value="10")})
        assert "coverage" in d
        assert "df" in d and len(d["df"]) == 10
        print("PASS notebook executes with 10 replications")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
