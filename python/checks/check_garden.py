"""Execute every slider state and verify finite-garden statistical fidelity."""
import importlib.util
import itertools
from pathlib import Path
from types import SimpleNamespace

import numpy as np

notebook = Path(__file__).resolve().parents[1] / "notebooks" / "02_garden.py"
spec = importlib.util.spec_from_file_location("garden", notebook)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

expected = np.array([
    [1/3, 1/3, 1/3],
    [1/6, 1/3, 1/2],
    [0.3, 0.4, 0.3],
    [0.15, 0.4, 0.45],
])
for n in range(4):
    outputs, defs = module.app.run(defs={"step": SimpleNamespace(value=n)})
    assert len(outputs) > 0
    np.testing.assert_allclose(defs["posterior_history"], expected)
    np.testing.assert_allclose(defs["comparison"]["Posterior"], expected[n])
    assert len(defs["path_table"]) == 3 * 4 ** n
    assert (defs["path_table"]["Status"] == "Compatible").sum() == defs["counts"].sum()
    assert np.isclose(defs["next_blue"], 0.575)
    for name in ("path_chart", "probability_chart", "history_chart"):
        assert defs[name].to_dict(validate=True)["$schema"]

# Independently compare enumeration, Bernoulli likelihood, and sequential Bayes
# for every binary sequence up to three draws, with equal and unequal priors.
for n in range(4):
    for sequence in itertools.product((0, 1), repeat=n):
        count = defs["count_paths"](sequence)
        p = defs["p_blue"]
        analytical = p ** sum(sequence) * (1 - p) ** (n - sum(sequence))
        np.testing.assert_allclose(count / 4 ** n, analytical)
        for prior in (np.ones(3) / 3, np.array([0.6, 0.3, 0.1])):
            batch = analytical * prior
            batch /= batch.sum()
            np.testing.assert_allclose(defs["update"](sequence, prior)[-1], batch)
print("PASS: all four notebook states, three chart schemas, 15 sequences, two priors; posterior = [0.15, 0.40, 0.45], predictive blue = 0.575")
