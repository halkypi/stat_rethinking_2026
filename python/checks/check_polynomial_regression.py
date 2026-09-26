"""Reuse the established fitting oracle for curved, linear-in-coefficient models."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from check_gaussian_regression import verify_fit
from rethinking_companion.gaussian_regression import design_matrix, exact_posterior, fit_gaussian, regression_case

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("regression_lesson",root/"notebooks"/"03_gaussian_regression.py")
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)
for kind in ("Quadratic", "Cubic"):
    x,y,degree,grid=regression_case(kind)
    X,X_grid=design_matrix(x,degree),design_matrix(grid,degree)
    if degree==2:
        assert (x[8],y[8])==(3.,-1.)
    assert X.shape==(10,degree+1)
    np.testing.assert_array_equal(X[:,2],x*x)
    fit=fit_gaussian(X,y,X_grid)
    diag=verify_fit(fit,X,y,X_grid)
    m,V=exact_posterior(X,y)
    # Source formula and generic design matrix must agree draw by draw.
    beta=fit.posterior.beta.values
    explicit=sum(beta[:,:,j,None]*grid[None,None,:]**j for j in range(degree+1))
    np.testing.assert_allclose(explicit,fit.predictions.mu_new,atol=1e-10)
    for n in (0,8,9,10):
        _,d=lesson.app.run(defs={"fit":fit,"scenario":SimpleNamespace(value=kind),"prefix":SimpleNamespace(value=n)})
        assert d["regression_chart"].to_dict(validate=True)["$schema"]
        assert d["prior_chart"].to_dict(validate=True)["$schema"]
        np.testing.assert_allclose(d["predictive_sd"]**2-d["mu_sd"]**2,1,atol=1e-10)
        np.testing.assert_allclose(d["exact_mean"],exact_posterior(X[:n],y[:n])[0])
    fit.to_netcdf(root/"outputs"/f"03_{kind.lower()}_fit.nc")
    (root/"outputs"/f"03_{kind.lower()}_diagnostics.json").write_text(json.dumps(diag,indent=2)+"\n")
    print(f"PASS {kind}: source modifications, full exact covariance, diagnostics, joint predictions and prefixes")
    print(json.dumps(diag))
