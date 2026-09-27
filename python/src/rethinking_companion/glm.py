"""GLM utilities: link functions and data loaders for binomial/Poisson models."""
from .runtime import configure_runtime
configure_runtime()

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit as inv_logit, logit  # noqa: F401


def _data_folder():
    return Path(__file__).resolve().parents[2] / "data"


def load_ucbadmit():
    folder = _data_folder()
    payload = (folder / "UCBadmit.csv").read_bytes()
    provenance = json.loads((folder / "UCBadmit.provenance.json").read_text())
    if hashlib.sha256(payload).hexdigest() != provenance["sha256"]:
        raise ValueError("UCBadmit checksum differs from recorded upstream file")
    d = pd.read_csv(folder / "UCBadmit.csv")
    assert list(d.columns) == ["dept", "applicant.gender", "admit", "reject", "applications"]
    assert len(d) == 12
    assert d["admit"].sum() + d["reject"].sum() == d["applications"].sum()
    return d


def ucbadmit_arrays(d):
    """Return dict of arrays matching the R source's dat list."""
    return {
        "A": d["admit"].to_numpy(),
        "N": d["applications"].to_numpy(),
        "G": np.where(d["applicant.gender"] == "female", 1, 2),
        "D": pd.Categorical(d["dept"]).codes + 1,
        "dept_labels": sorted(d["dept"].unique()),
    }


def ucbadmit_to_long(d):
    """Expand aggregated UCBadmit to individual Bernoulli rows."""
    rows = []
    for _, row in d.iterrows():
        base = {"dept": row["dept"], "applicant.gender": row["applicant.gender"]}
        rows.extend([{**base, "admit": 1}] * int(row["admit"]))
        rows.extend([{**base, "admit": 0}] * int(row["reject"]))
    dl = pd.DataFrame(rows)
    return {
        "A": dl["admit"].to_numpy(),
        "G": np.where(dl["applicant.gender"] == "female", 1, 2),
        "D": pd.Categorical(dl["dept"]).codes + 1,
        "N_long": len(dl),
    }


def load_kline():
    folder = _data_folder()
    payload = (folder / "Kline.csv").read_bytes()
    provenance = json.loads((folder / "Kline.provenance.json").read_text())
    if hashlib.sha256(payload).hexdigest() != provenance["sha256"]:
        raise ValueError("Kline checksum differs from recorded upstream file")
    d = pd.read_csv(folder / "Kline.csv")
    assert len(d) == 10
    log_pop = np.log(d["population"].to_numpy(dtype=float))
    P = (log_pop - log_pop.mean()) / log_pop.std()
    return {
        "T": d["total_tools"].to_numpy(),
        "P": P,
        "C": np.where(d["contact"] == "high", 2, 1),
        "population": d["population"].to_numpy(dtype=float),
        "culture": d["culture"].tolist(),
        "log_pop_mean": float(log_pop.mean()),
        "log_pop_std": float(log_pop.std()),
    }
