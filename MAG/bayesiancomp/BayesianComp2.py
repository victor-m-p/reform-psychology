'''
VMP 2022-09-02: 
following: https://bayesiancomputationbook.com/
EDA & model-evaluation work-flow
'''

# imports 
import pandas as pd
import pymc3 as pm
from scipy import stats
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

''' CH2 '''
''' effective samples & rhat '''
good_chains = stats.beta.rvs(2, 5,size=(2, 2000))
bad_chains0 = np.random.normal(np.sort(good_chains, axis=None), 0.05,
                               size=4000).reshape(2, -1)

bad_chains1 = good_chains.copy()
for i in np.random.randint(1900, size=4):
    bad_chains1[i%2:,i:i+100] = np.random.beta(i, 950, size=100)

chains = {"good_chains":good_chains,
          "bad_chains0":bad_chains0,
          "bad_chains1":bad_chains1}

az.ess(chains) # high for good_chains (fine). 
az.rhat(chains) # < 1.01 for good_chains (fine).
az.mcse(chains) # monto-carlo standard error (very low for good_chains).
az.plot_mcse(chains)

## the only one we will actually use (to get everything) ##
az.summary(chains, kind="diagnostics")

''' trace plots '''
az.plot_trace(chains)

# auto-correlation (should only be small random fluctuations)
az.plot_autocorr(chains, combined=True)

# rank-plot (should be uniform)
## more sensitive than trace-plots (they recommend). 
az.plot_rank(chains, kind="bars")

''' divergences '''
with pm.Model() as model_0:
    θ1 = pm.Normal("θ1", 0, 1, testval=0.1)
    θ2 = pm.Uniform("θ2", -θ1, θ1)
    idata_0 = pm.sample(return_inferencedata=True)

# black bars = divergences 
az.plot_trace(idata_0, kind="rank_bars")

# check divergences
az.plot_pair(idata_0, divergences=True)

# reparameterize
with pm.Model() as model_1:
    θ1 = pm.HalfNormal("θ1", 1 / (1-2/np.pi)**0.5)
    θ2 = pm.Uniform("θ2", -θ1, θ1)
    idata_1 = pm.sample(return_inferencedata=True)

# reparameterize + target-accept. 
with pm.Model() as model_1bis:
    θ1 = pm.HalfNormal("θ1", 1 / (1-2/np.pi)**0.5)
    θ2 = pm.Uniform("θ2", -θ1, θ1)
    idata_1bis = pm.sample(target_accept=.95, return_inferencedata=True)

''' model evaluation / comparison '''
# LOO is good
y_obs = np.random.normal(0, 1, size=100)
idatas_cmp = {}

# Generate data from Skewnormal likelihood model
# with fixed mean and skewness and random standard deviation
with pm.Model() as mA:
    σ = pm.HalfNormal("σ", 1)
    y = pm.SkewNormal("y", 0, σ, alpha=1, observed=y_obs)
    idataA = pm.sample(return_inferencedata=True)
    # add_groups modifies an existing az.InferenceData
    # has to be indented (contrary to in the book)
    idataA.add_groups({"posterior_predictive":
                    {"y":pm.sample_posterior_predictive(idataA)["y"][None,:]}})

idatas_cmp["mA"] = idataA

# Generate data from Normal likelihood model
# with fixed mean with random standard deviation
with pm.Model() as mB:
    σ = pm.HalfNormal("σ", 1)
    y = pm.Normal("y", 0, σ, observed=y_obs)
    idataB = pm.sample(return_inferencedata=True)
    # again has to be indented (because we sample)
    idataB.add_groups({"posterior_predictive":
                    {"y":pm.sample_posterior_predictive(idataB)["y"][None,:]}})

idatas_cmp["mB"] = idataB

# Generate data from Normal likelihood model
# with random mean and random standard deviation
with pm.Model() as mC:
    μ = pm.Normal("μ", 0, 1)
    σ = pm.HalfNormal("σ", 1)
    y = pm.Normal("y", μ, σ, observed=y_obs)
    idataC = pm.sample(return_inferencedata=True)
    idataC.add_groups({"posterior_predictive":
                    {"y":pm.sample_posterior_predictive(idataC)["y"][None,:]}})

idatas_cmp["mC"] = idataC

# az.compare()
az.compare(idatas_cmp)

# LOO-PIT (is- although not quite)
az.plot_bpv(idataA, kind="u_value")
az.plot_bpv(idataC, kind="u_value")