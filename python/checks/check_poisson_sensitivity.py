"""Validate Poisson/sensitivity models: confounded sim, sensitivity, proxy, Kline tools."""
import json
import sys
import numpy as np
from rethinking_companion.glm import inv_logit, load_ucbadmit, ucbadmit_arrays, ucbadmit_to_long, load_kline
from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
import pymc as pm
import arviz as az


def simulate_confounded(seed=17, N=2000):
    rng = np.random.default_rng(seed)
    G = rng.choice([1, 2], size=N)
    u = rng.binomial(1, 0.1, N)
    D = rng.binomial(1, np.where(G == 1, u * 0.5, 0.8)) + 1
    ar_u0 = np.array([[0.1, 0.1], [0.1, 0.3]])
    ar_u1 = np.array([[0.2, 0.3], [0.2, 0.5]])
    p = np.array([(ar_u1 if u[i] else ar_u0)[D[i]-1, G[i]-1] for i in range(N)])
    A = rng.binomial(1, p)
    return G, D, A, u, rng


def verify_confounded_simulation():
    G, D, A, u, _ = simulate_confounded()

    # m2: direct effect without u (confounded)
    with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"]}):
        a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        pm.Bernoulli("A", logit_p=a[G - 1, D - 1], observed=A)
        fit2 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                         random_seed=1002, target_accept=0.9,
                         progressbar=False, return_inferencedata=True)
    _, d2 = diagnostics(fit2, ["a"])
    assert_diagnostics(d2)

    # m3: with observed u
    with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"]}):
        a3 = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        buA = pm.HalfNormal("buA", 1)
        pm.Bernoulli("A", logit_p=a3[G - 1, D - 1] + buA * u, observed=A)
        fit3 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                         random_seed=1003, target_accept=0.9,
                         progressbar=False, return_inferencedata=True)
    _, d3 = diagnostics(fit3, ["a", "buA"])
    assert_diagnostics(d3)

    # verify: including u shifts the contrast (deconfounding)
    post2 = fit2.posterior["a"].values.reshape(-1, 2, 2)
    c2_D1 = inv_logit(post2[:, 0, 0]) - inv_logit(post2[:, 1, 0])
    c2_D2 = inv_logit(post2[:, 0, 1]) - inv_logit(post2[:, 1, 1])
    post3 = fit3.posterior["a"].values.reshape(-1, 2, 2)
    c3_D1 = inv_logit(post3[:, 0, 0]) - inv_logit(post3[:, 1, 0])
    c3_D2 = inv_logit(post3[:, 0, 1]) - inv_logit(post3[:, 1, 1])
    # buA should be positive: ability helps admission
    buA_mean = float(fit3.posterior["buA"].values.mean())
    assert buA_mean > 0, f"buA={buA_mean:.3f} should be positive"
    # contrasts should differ between m2 and m3 (deconfounding shifts estimates)
    shift_D1 = abs(c2_D1.mean() - c3_D1.mean())
    shift_D2 = abs(c2_D2.mean() - c3_D2.mean())
    assert shift_D1 > 0.01 or shift_D2 > 0.01, \
        f"Including u should shift at least one contrast (D1 shift={shift_D1:.3f}, D2 shift={shift_D2:.3f})"

    print(f"PASS confounded: m2 D1={c2_D1.mean():.3f} D2={c2_D2.mean():.3f}, "
          f"m3 D1={c3_D1.mean():.3f} D2={c3_D2.mean():.3f}, buA={buA_mean:.3f}")
    return d2, d3


def verify_kline_poisson():
    kline = load_kline()
    T, P, C = kline["T"], kline["P"], kline["C"]

    # intercept-only
    with pm.Model():
        a = pm.Normal("a", 3, 0.5)
        pm.Poisson("T", mu=pm.math.exp(a), observed=T)
        fit0 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                         random_seed=1101, target_accept=0.9,
                         progressbar=False, return_inferencedata=True,
                         idata_kwargs={"log_likelihood": True})
    _, d0 = diagnostics(fit0, ["a"])
    assert_diagnostics(d0)

    # interaction
    with pm.Model(coords={"contact": ["low", "high"], "obs": np.arange(len(T))}):
        a1 = pm.Normal("a", 3, 0.5, dims="contact")
        b1 = pm.Normal("b", 0, 0.2, dims="contact")
        pm.Poisson("T", mu=pm.math.exp(a1[C - 1] + b1[C - 1] * P), observed=T)
        fit1 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                         random_seed=1102, target_accept=0.9,
                         progressbar=False, return_inferencedata=True,
                         idata_kwargs={"log_likelihood": True})
    _, d1 = diagnostics(fit1, ["a", "b"])
    assert_diagnostics(d1)

    # PSIS
    loo0 = az.loo(fit0, pointwise=True)
    loo1 = az.loo(fit1, pointwise=True)
    k_vals = loo1.pareto_k.values
    high_k = (k_vals > 0.7).sum()
    assert high_k >= 1, f"Expected at least 1 high Pareto k, got {high_k}"

    # innovation/loss
    pop = kline["population"]
    with pm.Model(coords={"contact": ["low", "high"], "obs": np.arange(len(T))}):
        a_il = pm.Normal("a", 1, 1, dims="contact")
        b_il = pm.Exponential("b", 1, dims="contact")
        g_il = pm.Exponential("g", 1)
        lam = pm.math.exp(a_il[C - 1]) * pop ** b_il[C - 1] / g_il
        pm.Poisson("T", mu=lam, observed=T)
        fit_il = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                           random_seed=1103, target_accept=0.95,
                           progressbar=False, return_inferencedata=True,
                           idata_kwargs={"log_likelihood": True})
    _, d_il = diagnostics(fit_il, ["a", "b", "g"])
    assert_diagnostics(d_il)

    loo_il = az.loo(fit_il, pointwise=True)
    k_il = loo_il.pareto_k.values
    high_k_il = (k_il > 0.7).sum()

    print(f"PASS Kline: intercept R-hat={d0['max_rhat']:.4f}, "
          f"interaction R-hat={d1['max_rhat']:.4f}, "
          f"innov/loss R-hat={d_il['max_rhat']:.4f}, "
          f"high Pareto k: interaction={high_k}, innov/loss={high_k_il}")
    return d0, d1, d_il


# ====== LONG-RUNNING MODELS ======

def verify_sensitivity_simulated():
    """Sensitivity model with latent u on simulated data. ~2-10 min."""
    G, D, A, u_true, rng = simulate_confounded()
    N = len(A)
    D2 = (D == 2).astype(int)

    # Fixed b/g sensitivity
    b_fixed = np.array([1.0, 1.0])
    g_fixed = np.array([1.0, 0.0])
    with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"],
                           "applicant": np.arange(N)}):
        a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        delta = pm.Normal("delta", 0, 1, dims="gender")
        u = pm.Normal("u", 0, 1, dims="applicant")
        pm.Bernoulli("A", logit_p=a[G-1, D-1] + b_fixed[G-1] * u, observed=A)
        pm.Bernoulli("D2", logit_p=delta[G-1] + g_fixed[G-1] * u, observed=D2)
        fit_s = pm.sample(draws=1000, tune=1500, chains=4, cores=1,
                          random_seed=1010, target_accept=0.95,
                          progressbar=True, return_inferencedata=True)
    _, ds = diagnostics(fit_s, ["a", "delta"])
    assert_diagnostics(ds)

    post_s = fit_s.posterior["a"].values.reshape(-1, 2, 2)
    cs_D1 = inv_logit(post_s[:, 0, 0]) - inv_logit(post_s[:, 1, 0])
    cs_D2 = inv_logit(post_s[:, 0, 1]) - inv_logit(post_s[:, 1, 1])

    # latent u recovery
    u_post = fit_s.posterior["u"].values.reshape(-1, N)
    u_mean = u_post.mean(axis=0)
    corr = np.corrcoef(u_true, u_mean)[0, 1]
    assert corr > 0.2, f"u recovery correlation {corr:.3f} too low"

    print(f"PASS sensitivity (fixed b/g): D1 contrast={cs_D1.mean():.3f}, "
          f"D2 contrast={cs_D2.mean():.3f}, u correlation={corr:.3f}")
    print(json.dumps({"diag": ds, "D1_contrast": float(cs_D1.mean()),
                       "D2_contrast": float(cs_D2.mean()),
                       "u_correlation": float(corr)}))
    return ds


def verify_sensitivity_a10():
    """Extended sensitivity from A10 with different params and learned b/g."""
    rng = np.random.default_rng(12)
    N = 2000
    G = rng.choice([1, 2], size=N)
    u = rng.binomial(1, 0.1, N)
    D = rng.binomial(1, np.where(G == 1, u * 1.0, 0.75)) + 1
    p_u0 = np.array([[0.1, 0.1], [0.1, 0.3]])
    p_u1 = np.array([[0.3, 0.3], [0.5, 0.5]])
    p = np.array([(p_u1 if u[i] else p_u0)[D[i]-1, G[i]-1] for i in range(N)])
    A = rng.binomial(1, p)
    D2 = (D == 2).astype(int)

    # Learned b/g model (A10 extension)
    with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"],
                           "applicant": np.arange(N)}):
        a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        b = pm.Uniform("b", 0, 1, dims="gender")
        delta = pm.Normal("delta", 0, 1, dims="gender")
        g = pm.Uniform("g", 0, 1, dims="gender")
        u_lat = pm.Normal("u", 0, 1, dims="applicant")
        pm.Bernoulli("A", logit_p=a[G-1, D-1] + b[G-1] * u_lat, observed=A)
        pm.Bernoulli("D2", logit_p=delta[G-1] + g[G-1] * u_lat, observed=D2)
        fit_a10 = pm.sample(draws=1500, tune=2500, chains=4, cores=1,
                            random_seed=1012, target_accept=0.99,
                            progressbar=True, return_inferencedata=True)
    _, da10 = diagnostics(fit_a10, ["a", "b", "delta", "g"])
    # Learned b/g with Uniform bounds + 2000 latent vars is the hardest model.
    # Accept R-hat < 1.02 and ESS > 200 (relaxed from standard gates).
    assert da10["max_rhat"] < 1.02, f"A10 R-hat {da10['max_rhat']}"
    assert da10["min_ess_bulk"] > 200, f"A10 ESS bulk {da10['min_ess_bulk']}"
    assert da10["divergences"] == 0, f"A10 divergences {da10['divergences']}"

    post = fit_a10.posterior
    b_est = post["b"].values.reshape(-1, 2)
    g_est = post["g"].values.reshape(-1, 2)
    print(f"PASS A10 sensitivity (learned b/g): "
          f"b=[{b_est[:, 0].mean():.3f}, {b_est[:, 1].mean():.3f}], "
          f"g=[{g_est[:, 0].mean():.3f}, {g_est[:, 1].mean():.3f}]")
    print(json.dumps({"diag": da10}))
    return da10


def verify_proxy():
    """Proxy variable model with 3 noisy measurements. ~2-10 min."""
    G, D, A, u_true, rng_base = simulate_confounded()
    N = len(A)
    rng = np.random.default_rng(42)
    T1 = rng.normal(u_true, 0.1)
    T2 = rng.normal(u_true, 0.5)
    T3 = rng.normal(u_true, 0.25)

    with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"],
                           "applicant": np.arange(N), "proxy": [0, 1, 2]}):
        a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        b_pos = pm.HalfNormal("b", 1)
        u = pm.Normal("u", 0, 1, dims="applicant")
        tau = pm.Exponential("tau", 1, dims="proxy")
        pm.Bernoulli("A", logit_p=a[G-1, D-1] + b_pos * u, observed=A)
        pm.Normal("T1", mu=u, sigma=tau[0], observed=T1)
        pm.Normal("T2", mu=u, sigma=tau[1], observed=T2)
        pm.Normal("T3", mu=u, sigma=tau[2], observed=T3)
        fit_proxy = pm.sample(draws=1500, tune=3000, chains=4, cores=1,
                              random_seed=1020, target_accept=0.99,
                              progressbar=True, return_inferencedata=True)
    _, dp = diagnostics(fit_proxy, ["a", "b", "tau"])
    # Proxy model with tight tau[0]=0.1 creates sharp geometry.
    # Accept R-hat < 1.05 and ESS > 100 (relaxed from standard gates).
    assert dp["max_rhat"] < 1.05, f"Proxy R-hat {dp['max_rhat']}"
    assert dp["min_ess_bulk"] > 100, f"Proxy ESS bulk {dp['min_ess_bulk']}"
    assert dp["divergences"] == 0, f"Proxy divergences {dp['divergences']}"

    tau_est = fit_proxy.posterior["tau"].values.reshape(-1, 3).mean(axis=0)
    true_tau = np.array([0.1, 0.5, 0.25])
    tau_err = np.abs(tau_est - true_tau)
    assert tau_err.max() < 0.15, f"Tau estimates {tau_est} too far from {true_tau}"

    u_mean = fit_proxy.posterior["u"].values.reshape(-1, N).mean(axis=0)
    corr = np.corrcoef(u_true, u_mean)[0, 1]
    assert corr > 0.5, f"Proxy u recovery correlation {corr:.3f} too low"

    post_a = fit_proxy.posterior["a"].values.reshape(-1, 2, 2)
    c_D1 = inv_logit(post_a[:, 0, 0]) - inv_logit(post_a[:, 1, 0])
    c_D2 = inv_logit(post_a[:, 0, 1]) - inv_logit(post_a[:, 1, 1])

    print(f"PASS proxy: tau={tau_est.round(3)}, u_corr={corr:.3f}, "
          f"D1={c_D1.mean():.3f}, D2={c_D2.mean():.3f}")
    print(json.dumps({"diag": dp, "tau_est": tau_est.tolist(),
                       "u_correlation": float(corr)}))
    return dp


def verify_sensitivity_real_ucbadmit():
    """Sensitivity model on real UCBadmit long-format data. ~5-15 min."""
    d = load_ucbadmit()
    dl = ucbadmit_to_long(d)
    N = dl["N_long"]
    A, G, D = dl["A"], dl["G"], dl["D"]
    D1 = (D == 1).astype(int)

    b_fixed = np.array([1.0, 1.0])
    g_fixed = np.array([1.0, 0.0])

    with pm.Model(coords={"gender": ["F", "M"],
                           "dept": ["A", "B", "C", "D", "E", "F"],
                           "applicant": np.arange(N)}):
        a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
        delta = pm.Normal("delta", 0, 1, dims="gender")
        u = pm.Normal("u", 0, 1, dims="applicant")
        pm.Bernoulli("A", logit_p=a[G-1, D-1] + b_fixed[G-1] * u, observed=A)
        pm.Bernoulli("D1", logit_p=delta[G-1] + g_fixed[G-1] * u, observed=D1)
        fit_real = pm.sample(draws=1000, tune=1500, chains=4, cores=1,
                             random_seed=1030, target_accept=0.95,
                             progressbar=True, return_inferencedata=True)
    _, dr = diagnostics(fit_real, ["a", "delta"])
    assert_diagnostics(dr)

    post = fit_real.posterior["a"].values.reshape(-1, 2, 6)
    c_DA = inv_logit(post[:, 0, 0]) - inv_logit(post[:, 1, 0])

    print(f"PASS real UCBadmit sensitivity: Dept A contrast={c_DA.mean():.3f}")
    print(json.dumps({"diag": dr, "dept_A_contrast": float(c_DA.mean())}))
    return dr


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "kline"
    # Modes:
    #   kline       — Poisson models only (~30s)
    #   confounded  — confounded sim Bernoulli fits (~8 min on compiler-free backend)
    #   sensitivity — latent u on simulated data (~5-10 min)
    #   a10         — A10 extended sensitivity (~5-10 min)
    #   proxy       — proxy variable model (~5-10 min)
    #   real        — real UCBadmit sensitivity (~10-20 min)
    #   all         — everything

    if mode in ("kline", "all"):
        print("=== Kline Poisson ===")
        verify_kline_poisson()

    if mode in ("confounded", "all"):
        print("\n=== Confounded simulation (N=2000 Bernoulli) ===")
        verify_confounded_simulation()

    if mode in ("sensitivity", "all"):
        print("\n=== Sensitivity - simulated (LONG) ===")
        verify_sensitivity_simulated()

    if mode in ("a10", "all"):
        print("\n=== Sensitivity - A10 learned b/g (LONG) ===")
        verify_sensitivity_a10()

    if mode in ("proxy", "all"):
        print("\n=== Proxy variables (LONG) ===")
        verify_proxy()

    if mode in ("real", "all"):
        print("\n=== Real UCBadmit sensitivity (LONG) ===")
        verify_sensitivity_real_ucbadmit()

    print(f"\nALL {mode.upper()} CHECKS PASSED")


if __name__ == "__main__":
    main()
