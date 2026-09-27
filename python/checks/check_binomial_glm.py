"""Validate binomial GLM models: generative simulation, UCBadmit, marginal causal effect."""
import json
import numpy as np
from rethinking_companion.glm import inv_logit, load_ucbadmit, ucbadmit_arrays
from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
import pymc as pm


def fit_total_effect(G, A, N=None, *, seed, use_binomial=False):
    with pm.Model(coords={"gender": ["F", "M"]}):
        a = pm.Normal("a", 0, 1, dims="gender")
        if use_binomial:
            pm.Binomial("A", n=N, logit_p=a[G - 1], observed=A)
        else:
            pm.Bernoulli("A", logit_p=a[G - 1], observed=A)
        idata = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata


def fit_direct_effect(G, D, A, N=None, *, seed, dept_labels, use_binomial=False):
    with pm.Model(coords={"gender": ["F", "M"], "dept": dept_labels}):
        a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        if use_binomial:
            pm.Binomial("A", n=N, logit_p=a[G - 1, D - 1], observed=A)
        else:
            pm.Bernoulli("A", logit_p=a[G - 1, D - 1], observed=A)
        idata = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata


def verify_generative_simulation():
    rng = np.random.default_rng(1999)
    N_sim = 1000
    G = rng.choice([1, 2], size=N_sim)
    D = rng.binomial(1, np.where(G == 1, 0.3, 0.8)) + 1
    accept = np.array([[0.05, 0.1], [0.2, 0.3]])
    p = np.array([accept[D[i]-1, G[i]-1] for i in range(N_sim)])
    A = rng.binomial(1, p)

    # total effect
    fit1 = fit_total_effect(G, A, seed=901)
    _, d1 = diagnostics(fit1, ["a"])
    assert_diagnostics(d1)

    # direct effect (Bernoulli)
    fit2 = fit_direct_effect(G, D, A, seed=902, dept_labels=["1", "2"])
    _, d2 = diagnostics(fit2, ["a"])
    assert_diagnostics(d2)

    # aggregated binomial equivalence
    import pandas as pd
    simdf = pd.DataFrame({"A": A, "G": G, "D": D})
    agg = simdf.groupby(["G", "D"]).agg(admit=("A", "sum"), n=("A", "count")).reset_index()
    fitb = fit_direct_effect(
        agg["G"].values, agg["D"].values, agg["admit"].values,
        N=agg["n"].values, seed=903, dept_labels=["1", "2"], use_binomial=True)
    _, db = diagnostics(fitb, ["a"])
    assert_diagnostics(db)

    pb = fit2.posterior["a"].values.reshape(-1, 4)
    pbin = fitb.posterior["a"].values.reshape(-1, 4)
    mdiff = np.abs(pb.mean(0) - pbin.mean(0)).max()
    assert mdiff < 0.15, f"Bernoulli/Binomial mean diff {mdiff} too large"

    # verify total contrast direction: G=1 has lower acceptance in this simulation
    post1 = fit1.posterior["a"].values.reshape(-1, 2)
    total_contrast = inv_logit(post1[:, 0]) - inv_logit(post1[:, 1])
    assert total_contrast.mean() < 0, "G=1 should have lower total admission rate"

    print(f"PASS generative sim: R-hat total={d1['max_rhat']:.4f}, "
          f"direct={d2['max_rhat']:.4f}, binomial_diff={mdiff:.4f}")
    return d1, d2


def verify_ucbadmit():
    d = load_ucbadmit()
    dat = ucbadmit_arrays(d)

    # total effect (binomial)
    fit_mG = fit_total_effect(dat["G"], dat["A"], N=dat["N"],
                               seed=911, use_binomial=True)
    _, dmG = diagnostics(fit_mG, ["a"])
    assert_diagnostics(dmG)

    # direct effect (binomial)
    fit_mGD = fit_direct_effect(dat["G"], dat["D"], dat["A"], N=dat["N"],
                                 seed=912, dept_labels=dat["dept_labels"],
                                 use_binomial=True)
    _, dmGD = diagnostics(fit_mGD, ["a"])
    assert_diagnostics(dmGD)

    # Simpson's paradox check
    postG = fit_mG.posterior["a"].values.reshape(-1, 2)
    total_diff = inv_logit(postG[:, 0]) - inv_logit(postG[:, 1])
    assert total_diff.mean() < 0, "Total effect should favor men (negative F-M)"

    postGD = fit_mGD.posterior["a"].values.reshape(-1, 2, 6)
    n_depts_favoring_women = 0
    for i in range(6):
        dept_c = inv_logit(postGD[:, 0, i]) - inv_logit(postGD[:, 1, i])
        if dept_c.mean() > 0:
            n_depts_favoring_women += 1
    assert n_depts_favoring_women >= 3, \
        f"Simpson's: expected ≥3 depts favoring women, got {n_depts_favoring_women}"

    # Marginal causal effect
    apps_per_dept = np.array([dat["N"][dat["D"] == i + 1].sum() for i in range(6)])
    D_exp = np.repeat(np.arange(6), apps_per_dept)
    pF = inv_logit(postGD[:, 0, :][:, D_exp])
    pM = inv_logit(postGD[:, 1, :][:, D_exp])
    marginal = pF.mean(axis=1) - pM.mean(axis=1)
    assert abs(marginal.mean()) < 0.05, \
        f"Marginal causal effect {marginal.mean():.4f} should be near zero"

    print(f"PASS UCBadmit: total diff={total_diff.mean():.3f}, "
          f"marginal causal={marginal.mean():.4f}, "
          f"depts favoring women={n_depts_favoring_women}")
    print(json.dumps({"diag_mG": dmG, "diag_mGD": dmGD,
                       "total_diff_mean": float(total_diff.mean()),
                       "marginal_mean": float(marginal.mean())}))
    return dmG, dmGD


def main():
    print("=== Generative simulation ===")
    verify_generative_simulation()
    print("\n=== UCBadmit real data ===")
    verify_ucbadmit()
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
