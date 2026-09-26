"""Validate a constrained posterior with independent numerical integration."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from rethinking_companion.gaussian_regression import az, assert_diagnostics, diagnostics
from rethinking_companion.height_weight import fit_weight, integrated_weight_posterior, load_howell, simulated_weight


def verify_weight_fit(fit,height,weight,grid):
    summary,diag=diagnostics(fit,("a","b","sigma")); assert_diagnostics(diag)
    values=np.stack([fit.posterior[name].values for name in ("a","b","sigma")],axis=-1)
    assert values.shape==(4,1500,3)
    assert np.all(values[:,:,1]>0) and np.all((values[:,:,2]>0)&(values[:,:,2]<10))
    mean,covariance,boundary=integrated_weight_posterior(height,weight)
    refined,refined_cov,refined_boundary=integrated_weight_posterior(height,weight,resolution=2,b_max=6)
    np.testing.assert_allclose(mean,refined,rtol=0,atol=1e-5)
    np.testing.assert_allclose(covariance,refined_cov,rtol=1e-4,atol=1e-6)
    assert max(boundary,refined_boundary)<1e-10
    mcse=np.array([float(az.mcse(fit,var_names=[name])[name]) for name in ("a","b","sigma")])
    assert np.all(abs(values.mean(axis=(0,1))-mean)<6*mcse+1e-4)
    centered=values-mean
    products=centered[:,:,:,None]*centered[:,:,None,:]
    product_mcse=az.mcse(az.from_dict(posterior={"products":products})).products.values
    assert np.all(abs(products.mean(axis=(0,1))-covariance)<6*product_mcse+1e-5)
    center=height.mean()
    assert fit.attrs["training_height_mean"]==center
    expected=values[:,:,0,None]+values[:,:,1,None]*(grid-center)
    np.testing.assert_allclose(fit.predictions.mu_new,expected,atol=1e-12)
    standardized=(fit.predictions.weight_new.values-expected)/values[:,:,2,None]
    assert abs(standardized.mean())<6/np.sqrt(standardized.size)
    assert abs(np.mean(standardized**2)-1)<6*np.sqrt(2/standardized.size)
    assert fit.posterior_predictive.weight.shape==(4,1500,len(weight))
    replicated=(fit.posterior_predictive.weight.values-fit.posterior.mu.values)/values[:,:,2,None]
    assert abs(replicated.mean())<6/np.sqrt(replicated.size)
    assert abs(np.mean(replicated**2)-1)<6*np.sqrt(2/replicated.size)
    prior_a,prior_b,prior_s=(fit.prior[name].values for name in ("a","b","sigma"))
    prior_noise=(fit.prior_predictive.weight.values-prior_a[:,:,None]-prior_b[:,:,None]*(height-center))/prior_s[:,:,None]
    assert abs(prior_noise.mean())<6/np.sqrt(prior_noise.size)
    return diag,mean,covariance


def main():
    root=Path(__file__).resolve().parents[1]
    all_data=load_howell(); adults=all_data.loc[all_data.age>=18]
    assert len(adults)==352
    cases=[("Synthetic validation",*simulated_weight()),("Howell adults",adults.height.to_numpy(),adults.weight.to_numpy())]
    for name,h,w in cases:
        grid=np.linspace(130,190,50)
        fit=fit_weight(h,w,grid)
        diag,mean,covariance=verify_weight_fit(fit,h,w,grid)
        if name=="Synthetic validation":
            draws=np.stack([fit.posterior[v].values.ravel() for v in ("a","b","sigma")],axis=-1)
            interval=np.quantile(draws,[.005,.995],axis=0)
            assert np.all((np.array([70,.5,5])>interval[0])&(np.array([70,.5,5])<interval[1]))
        stem="03_weight_synthetic" if name=="Synthetic validation" else "03_weight_adults"
        fit.to_netcdf(root/"outputs"/(stem+".nc"))
        (root/"outputs"/(stem+"_diagnostics.json")).write_text(json.dumps({"diagnostics":diag,"integrated_mean":mean.tolist(),"integrated_sd":np.sqrt(np.diag(covariance)).tolist()},indent=2)+"\n")
        notebook=root/"notebooks"/"03_height_weight.py"
        if notebook.exists():
            spec=importlib.util.spec_from_file_location("weight_lesson",notebook)
            lesson=importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)
            _,d=lesson.app.run(defs={"fit":fit,"dataset":SimpleNamespace(value=name)})
            for chart in ("weight_chart","prior_chart","residual_chart"):
                assert d[chart].to_dict(validate=True)["$schema"]
            assert d["bands"].shape==(50,6)
        print("PASS",name,"grid refinement, posterior moments/covariance, diagnostics, parameter support and predictive centering/noise")
        print(json.dumps({"diagnostics":diag,"mean":mean.tolist()}))


if __name__=="__main__":
    main()
