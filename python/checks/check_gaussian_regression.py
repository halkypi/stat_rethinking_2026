"""Four-chain NUTS against exact Gaussian inference and an independent quadrature."""
import json
from pathlib import Path
import numpy as np
from scipy import stats
from rethinking_companion.gaussian_regression import (
    az, assert_diagnostics, design_matrix, diagnostics, exact_posterior, fit_gaussian, linear_data,
)


def verify_fit(idata, X, y, X_grid):
    mean, covariance = exact_posterior(X, y)
    summary, diag = diagnostics(idata)
    assert_diagnostics(diag)
    beta = idata.posterior.beta.transpose("chain", "draw", "coefficient").values
    assert beta.shape == (4, 1500, X.shape[1])
    mcse = az.mcse(idata, var_names=["beta"]).beta.values
    assert np.all(abs(beta.mean(axis=(0,1))-mean) < 6*mcse + 1e-4)
    centered = beta-mean
    products = centered[:,:,:,None]*centered[:,:,None,:]
    product_mcse = az.mcse(az.from_dict(posterior={"product":products})).product.values
    assert np.all(abs(products.mean(axis=(0,1))-covariance) < 6*product_mcse + 1e-4)
    prediction = idata.predictions.mu_new.transpose("chain", "draw", "prediction").values
    np.testing.assert_allclose(prediction, np.einsum("ij,cdj->cdi", X_grid,beta), atol=1e-12)
    assert idata.posterior_predictive.y.shape == (4, 1500, len(y))
    noise = idata.predictions.y_new.values - prediction
    assert abs(noise.mean()) < 6/np.sqrt(noise.size)
    assert abs(np.mean(noise**2)-1) < 6*np.sqrt(2/noise.size)
    prior = idata.prior.beta.values.reshape(-1, X.shape[1])
    assert np.all(abs(prior.mean(axis=0)) < 6/np.sqrt(len(prior)))
    assert np.all(abs(np.mean(prior**2,axis=0)-1) < 6*np.sqrt(2/len(prior)))
    prior_noise = idata.prior_predictive.y.values - np.einsum("ij,cdj->cdi", X,idata.prior.beta.values)
    assert abs(prior_noise.mean()) < 6/np.sqrt(prior_noise.size)
    assert abs(np.mean(prior_noise**2)-1) < 6*np.sqrt(2/prior_noise.size)
    exact_mu = X_grid @ mean
    exact_var = np.einsum("ij,jk,ik->i", X_grid,covariance,X_grid)
    pred_mcse = az.mcse(idata.predictions, var_names=["y_new"]).y_new.values
    assert np.all(abs(idata.predictions.y_new.mean(("chain","draw")).values-exact_mu) < 6*pred_mcse + 1e-4)
    # Quantile coverage at representative prediction points, using exact normal CDF.
    for j in (0, len(X_grid)//2, len(X_grid)-1):
        bounds = np.quantile(idata.predictions.y_new.values[:,:,j], [.055,.945])
        cdf = stats.norm.cdf(bounds,exact_mu[j],np.sqrt(1+exact_var[j]))
        for k,q in enumerate((.055,.945)):
            ess = float(az.ess(idata.predictions.y_new.isel(prediction=j).to_dataset(), method="quantile", prob=q).y_new)
            assert abs(cdf[k]-q) < 6*np.sqrt(q*(1-q)/ess) + 1/6000
    return diag


def main():
    x,y = linear_data()
    X = design_matrix(x)
    grid = design_matrix(np.linspace(-2.2,2.2,81))
    mean,covariance = exact_posterior(X,y)
    # Numerical integration of prior * likelihood over two coefficient axes.
    axes = [np.linspace(mean[j]-7*np.sqrt(covariance[j,j]), mean[j]+7*np.sqrt(covariance[j,j]), 301) for j in range(2)]
    aa,bb=np.meshgrid(*axes,indexing="ij")
    logp=-.5*(aa**2+bb**2)
    for xi,yi in zip(x,y):
        logp-=.5*(yi-aa-bb*xi)**2
    weights=np.exp(logp-logp.max()); weights/=weights.sum()
    qm=np.array([(weights*aa).sum(),(weights*bb).sum()])
    qc=np.array([[(weights*(a-qm[i])*(b-qm[j])).sum() for j,b in enumerate((aa,bb))] for i,a in enumerate((aa,bb))])
    np.testing.assert_allclose(qm,mean,atol=1e-8)
    np.testing.assert_allclose(qc,covariance,atol=1e-8)
    # Every observation prefix, including zero, must agree with sequential updates.
    m=np.zeros(2); V=np.eye(2)
    for n in range(11):
        m_exact,V_exact=exact_posterior(X[:n],y[:n])
        np.testing.assert_allclose(m,m_exact,atol=1e-12)
        np.testing.assert_allclose(V,V_exact,atol=1e-12)
        if n<10:
            gain=V@X[n]/(1+X[n]@V@X[n])
            m=m+gain*(y[n]-X[n]@m)
            V=V-np.outer(gain,X[n]@V)
    idata=fit_gaussian(X,y,grid)
    diag=verify_fit(idata,X,y,grid)
    out=Path(__file__).resolve().parents[1]/"outputs"
    out.mkdir(exist_ok=True)
    idata.to_netcdf(out/"03_linear_fit.nc")
    (out/"03_linear_diagnostics.json").write_text(json.dumps(diag,indent=2)+"\n")
    # Exercise all displayed states with this independently verified fit, avoiding
    # five redundant refits; the marimo export separately executes fitting too.
    import importlib.util
    from types import SimpleNamespace
    notebook=Path(__file__).resolve().parents[1]/"notebooks"/"03_gaussian_regression.py"
    spec=importlib.util.spec_from_file_location("linear_lesson",notebook)
    lesson=importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)
    for n in (0,1,2,5,10):
        _,d=lesson.app.run(defs={"fit":idata,"prefix":SimpleNamespace(value=n)})
        assert d["regression_chart"].to_dict(validate=True)["$schema"]
        assert d["prior_chart"].to_dict(validate=True)["$schema"]
        np.testing.assert_allclose(d["predictive_sd"]**2-d["mu_sd"]**2,1)
    print("PASS: exact posterior, independent 2D quadrature, sequential prefixes, four-chain diagnostics, coefficient means/covariance, prior predictive and new-data prediction checks")
    print(json.dumps(diag,indent=2))


if __name__ == "__main__":
    main()
