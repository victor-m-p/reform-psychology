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

''' beta-binomial '''

# observerd
Y = stats.bernoulli(0.7).rvs(20)

# Declare a model in PyMC3
## numpy for blas... 
with pm.Model() as model:
    # Specify the prior distribution of unknown parameter
    θ = pm.Beta("θ", alpha=1, beta=1)

    # Specify the likelihood distribution and condition on the observed data
    y_obs = pm.Binomial("y_obs", n=1, p=θ, observed=Y)

    # Sample from the posterior distribution
    idata = pm.sample(1000, return_inferencedata=True)

# predictive distributions (prior & posterior)
pred_dists = (pm.sample_prior_predictive(1000, model)["y_obs"],
              pm.sample_posterior_predictive(idata, 1000, model)["y_obs"])

