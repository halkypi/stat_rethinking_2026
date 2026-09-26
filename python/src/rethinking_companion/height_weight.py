"""Centered positive-slope regression from 03_howell_new_weight_model.r."""
from .runtime import configure_runtime
configure_runtime()

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pymc as pm


def load_howell():
    folder=Path(__file__).resolve().parents[2]/"data"
    payload=(folder/"Howell1.csv").read_bytes()
    provenance=json.loads((folder/"Howell1.provenance.json").read_text())
    if hashlib.sha256(payload).hexdigest()!=provenance["sha256"]:
        raise ValueError("Howell1 checksum differs from the recorded upstream file")
    data=pd.read_csv(folder/"Howell1.csv",sep=";")
    if list(data.columns)!=["height","weight","age","male"] or len(data)!=544 or data.isna().any().any():
        raise ValueError("Unexpected Howell1 schema or missing data")
    return data


def simulated_weight(seed=604):
    rng=np.random.default_rng(seed)
    height=rng.uniform(130,170,100)
    weight=rng.normal(70+.5*(height-height.mean()),5)
    return height,weight


def fit_weight(height,weight,height_grid,*,seed=604,draws=1500,tune=1000):
    height,weight,height_grid=map(np.asarray,(height,weight,height_grid))
    center=float(height.mean())
    with pm.Model(coords={"observation":np.arange(len(height))}):
        h=pm.Data("height_centered",height-center,dims="observation")
        a=pm.Normal("a",60,10)
        b=pm.LogNormal("b",0,1)
        sigma=pm.Uniform("sigma",0,10)
        mu=pm.Deterministic("mu",a+b*h,dims="observation")
        pm.Normal("weight",mu,sigma,observed=weight,dims="observation")
        prior=pm.sample_prior_predictive(draws=1000,random_seed=seed+1)
        fit=pm.sample(draws=draws,tune=tune,chains=4,cores=1,random_seed=seed,
                      target_accept=.9,progressbar=False,return_inferencedata=True)
        pm.sample_posterior_predictive(fit,var_names=["weight"],random_seed=seed+2,
                                      extend_inferencedata=True,progressbar=False)
    fit.extend(prior)
    with pm.Model(coords={"prediction":np.arange(len(height_grid))}):
        h=pm.Data("height_centered",height_grid-center,dims="prediction")
        a=pm.Normal("a",60,10)
        b=pm.LogNormal("b",0,1)
        sigma=pm.Uniform("sigma",0,10)
        mu=pm.Deterministic("mu_new",a+b*h,dims="prediction")
        pm.Normal("weight_new",mu,sigma,dims="prediction")
        pm.sample_posterior_predictive(fit,var_names=["mu_new","weight_new"],predictions=True,
                                      random_seed=seed+3,extend_inferencedata=True,progressbar=False)
    fit.attrs["training_height_mean"]=center
    fit.attrs["random_seed"]=seed
    return fit


def integrated_weight_posterior(height,weight,*,resolution=1,b_max=3):
    """Independent deterministic integration; analytically integrate out a.

    Fine grids in b and sigma integrate the remaining two-dimensional posterior.
    Return moments and boundary mass so checks can verify grid refinement and
    truncation rather than assuming a finite grid is exact.
    """
    height,weight=map(np.asarray,(height,weight))
    n=len(weight); z=height-height.mean(); ybar=weight.mean(); yc=weight-ybar
    b=np.linspace(.0001,b_max,1201*resolution)
    sigma=np.linspace(.01,10,801*resolution)
    B,S=b[:,None],sigma[None,:]
    sse=yc@yc-2*B*(z@yc)+B**2*(z@z)
    logp=-(n-1)*np.log(S)-.5*np.log(S*S+n*100)-sse/(2*S*S)
    logp=logp-(ybar-60)**2/(2*(100+S*S/n))-np.log(B)-.5*np.log(B)**2
    weights=np.exp(logp-logp.max())
    # Trapezoid endpoint weights; constant grid spacing cancels on normalization.
    weights[[0,-1],:]*=.5; weights[:,[0,-1]]*=.5
    weights/=weights.sum()
    a_var=1/(n/S**2+1/100)
    a_mean=a_var*(n*ybar/S**2+60/100)
    values=[a_mean,B,S]
    means=np.array([(weights*v).sum() for v in values])
    covariance=np.array([[(weights*(v-means[i])*(w-means[j])).sum()
                          for j,w in enumerate(values)] for i,v in enumerate(values)])
    covariance[0,0]+=(weights*a_var).sum()
    boundary=float(weights[:2,:].sum()+weights[-2:,:].sum()+weights[:,:2].sum()+weights[:,-2:].sum())
    return means,covariance,boundary
