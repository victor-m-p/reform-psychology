'''
VMP 2022-09-02: 
following: https://bayesiancomputationbook.com/
'''

# imports 
import pandas as pd
import pymc3 as pm
from scipy import stats
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

## from Bayesian Analysis with Python 
babies = pd.read_csv("../../BookCode_Edition1/data/babies.csv")
# Add a constant term so we can use the dot product to express the intercept
babies["Intercept"] = 1

# quick scatter 
babies.plot.scatter('Month', 'Length')

## first linear model 
with pm.Model() as model_baby_linear:
    beta = pm.Normal("beta", sigma=10, shape=2)

    μ = pm.Deterministic("μ", pm.math.dot(babies[["Intercept", "Month"]], beta))
    ϵ = pm.HalfNormal("ϵ", sigma=10)

    length = pm.Normal("length", mu=μ, sigma=ϵ, observed=babies["Length"])

    trace_linear = pm.sample(draws=2000, tune=4000)
    pcc_linear = pm.sample_posterior_predictive(trace_linear)
    inf_data_linear = az.from_pymc3(trace=trace_linear,
                                    posterior_predictive=pcc_linear)

## some good plots here I have omitted

## non-linear model 
with pm.Model() as model_baby_sqrt:
    beta = pm.Normal("beta", sigma=10, shape=2) # shape = 2!!

    μ = pm.Deterministic("μ", beta[0] + beta[1] * np.sqrt(babies["Month"]))
    σ = pm.HalfNormal("σ", sigma=10)

    length = pm.Normal("length", mu=μ, sigma=σ, observed=babies["Length"])
    inf_data_sqrt = pm.sample(draws=2000, tune=4000)

### VARYING UNCERTAINTY ###

## extended, modeling variance over time 
with pm.Model() as model_baby_vv:
    β = pm.Normal("β", sigma=10, shape=2)
    
    # Additional variance terms
    δ = pm.HalfNormal("δ", sigma=10, shape=2)

    μ = pm.Deterministic("μ", β[0] + β[1] * np.sqrt(babies["Month"]))
    σ = pm.Deterministic("σ", δ[0] + δ[1] * babies["Month"])

    length = pm.Normal("length", mu=μ, sigma=σ, observed=babies["Length"])
    
    trace_baby_vv = pm.sample(2000, target_accept=.95)
    ppc_baby_vv = pm.sample_posterior_predictive(trace_baby_vv,
                                                 var_names=["length", "σ"])
    inf_data_baby_vv = az.from_pymc3(trace=trace_baby_vv,
                                     posterior_predictive=ppc_baby_vv)

### INTERACTION EFFECTS ###

## tips data 
tips_df = pd.read_csv("../../BookCode_Edition1/data/tips.csv")
tips = tips_df["tip"]
total_bill_c = (tips_df["total_bill"] - tips_df["total_bill"].mean())  
smoker = pd.Categorical(tips_df["smoker"]).codes

## no interaction
with pm.Model() as model_no_interaction:
    β = pm.Normal("β", mu=0, sigma=1, shape=3)
    σ = pm.HalfNormal("σ", 1)

    μ = (β[0] +
         β[1] * total_bill_c + 
         β[2] * smoker)

    obs = pm.Normal("obs", μ, σ, observed=tips)
    trace_no_interaction = pm.sample(1000, tune=1000)

## introducing interaction
# good code-setup here, very intuitive, I like it. 
with pm.Model() as model_interaction:
    β = pm.Normal("β", mu=0, sigma=1, shape=4)
    σ = pm.HalfNormal("σ", 1)

    μ = (β[0]
       + β[1] * total_bill_c
       + β[2] * smoker
       + β[3] * smoker * total_bill_c
        )

    obs = pm.Normal("obs", μ, σ, observed=tips)
    trace_interaction = pm.sample(1000, tune=1000)

# skipped some good plots & loo

### ROBUST REGRESSION (OUTLIERS): 
# omitted code, but see the ipynb/chapter. 
