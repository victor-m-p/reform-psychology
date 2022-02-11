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

''' 3. Linear model '''
# https://github.com/BayesianModelingandComputationInPython/BookCode_Edition1/blob/main/notebooks/chp_03.ipynb
### PENGUINS ###
## comparing two groups ## 
penguins = pd.read_csv("../BookCode_Edition1/data/penguins.csv")
penguins.head(5)
# subset to needed columns 
missing_data = penguins.isnull()[
    ["bill_length_mm", "flipper_length_mm", "sex", "body_mass_g"]
].any(axis=1)
# shows the rows that are missing data (from the columns we care about) - pretty neat
missing_data.head(5)
# drop rows with any missing data
penguins = penguins.loc[~missing_data] # we do not want true, thus ~

## empirical mean ##
summary_stats = (penguins.loc[:, ["species", "body_mass_g"]]
                         .groupby("species")
                         .agg(["mean", "std", "count"]))

summary_stats

## MODEL: wide priors ##
# bit of a funky way of doing the code, but yeah, pretty cool. 
adelie_mask = (penguins["species"] == "Adelie")
adelie_mass_obs = penguins.loc[adelie_mask, "body_mass_g"].values

with pm.Model() as model_adelie_penguin_mass:
    σ = pm.HalfStudentT("σ", 100, 2000)
    μ = pm.Normal("μ", 4000, 3000)
    mass = pm.Normal("mass", mu=μ, sigma=σ, observed=adelie_mass_obs)

    prior = pm.sample_prior_predictive(samples=5000)
    trace = pm.sample(chains=4)
    inf_data_adelie_penguin_mass = az.from_pymc3(prior=prior, trace=trace)

# quick checks of prior (reasonable)
az.plot_posterior(inf_data_adelie_penguin_mass.prior, var_names=["σ", "μ"], textsize=20)
az.plot_trace(inf_data_adelie_penguin_mass, divergences="bottom", kind="rank_bars")
az.summary(inf_data_adelie_penguin_mass)

# posterior (weight distribution on left, standard deviation on right)
az.plot_posterior(inf_data_adelie_penguin_mass, hdi_prob=.94, textsize=26);

## ACROSS SPECIES (but three separate models) ## 
# pd.categorical makes it easy to index species below
all_species = pd.Categorical(penguins["species"])

with pm.Model() as model_penguin_mass_all_species:
    # Note the addition of the shape parameter
    σ = pm.HalfStudentT("σ", 100, 2000, shape=3)
    μ = pm.Normal("μ", 4000, 3000, shape=3)
    mass = pm.Normal("mass",
                     mu=μ[all_species.codes],
                     sigma=σ[all_species.codes],
                     observed=penguins["body_mass_g"])

    trace = pm.sample()
    inf_data_model_penguin_mass_all_species = az.from_pymc3(
        trace=trace,
        coords={"μ_dim_0": all_species.categories,
                "σ_dim_0": all_species.categories})

# check traces 
az.plot_trace(inf_data_model_penguin_mass_all_species, compact=False, divergences="bottom", kind="rank_bars");

# forest plot of mass (mu)
az.plot_forest(inf_data_model_penguin_mass_all_species, var_names=["μ"])
# forest plot of variance (sigma/sd?)
az.plot_forest(inf_data_model_penguin_mass_all_species, var_names=["σ"])

### IN TENSORFLOW ###
# I have not put the code here, but can be done # 

### Linear Regression ### 
# non-centered regresssion
adelie_flipper_length_obs = penguins.loc[adelie_mask, "flipper_length_mm"]

with pm.Model() as model_adelie_flipper_regression1:
    # pm.Data allows us to change the underlying value in a later code block
    adelie_flipper_length = pm.Data("adelie_flipper_length",
                                    adelie_flipper_length_obs)
    σ = pm.HalfStudentT("σ", 100, 2000)
    beta0 = pm.Normal("beta0", 0, 4000)
    beta1 = pm.Normal("beta1", 0, 4000)
    μ = pm.Deterministic("μ", beta0 + beta1 * adelie_flipper_length)

    mass = pm.Normal("mass", mu=μ, sigma=σ, observed = adelie_mass_obs)

    inf_data_adelie_flipper_regression = pm.sample(return_inferencedata=True)

# check posterior & trace
az.plot_posterior(inf_data_adelie_flipper_regression, var_names=["beta0", "beta1"], textsize=20);
az.plot_trace(inf_data_adelie_flipper_regression, compact=False, divergences="bottom", kind="rank_bars");

# interpretation: 
## 94% HDI does not cross zero, so there is some relation
## beta0 however means that we expect 0mm flipper to be between -4000 and -500 grams... 
## -- not necessarily problematic, but not interpretable. 

# does the model improve with flipper as covariate? (TL;DR -- YES!)
axes = az.plot_forest(
    [inf_data_adelie_penguin_mass, inf_data_adelie_flipper_regression],
    model_names=["mass_only", "flipper_regression"],
    var_names=["σ"], combined=True, figsize=(10,2))

axes[0].set_title("σ Comparison 94.0 HDI")

# plot the linear relation
fig, ax = plt.subplots()
alpha_m = inf_data_adelie_flipper_regression.posterior.mean().to_dict()["data_vars"]["beta0"]["data"]
beta_m = inf_data_adelie_flipper_regression.posterior.mean().to_dict()["data_vars"]["beta1"]["data"]

flipper_length = np.linspace(adelie_flipper_length_obs.min(), adelie_flipper_length_obs.max(), 100)

flipper_length_mean = alpha_m + beta_m * flipper_length
ax.plot(flipper_length, flipper_length_mean, c='C4',
         label=f'y = {alpha_m:.2f} + {beta_m:.2f} * x')

ax.scatter(adelie_flipper_length_obs, adelie_mass_obs)

# Figure out how to do this from inference data
az.plot_hdi(adelie_flipper_length_obs, inf_data_adelie_flipper_regression.posterior['μ'], hdi_prob=0.94, color='k', ax=ax)

ax.set_xlabel('Flipper Length')
ax.set_ylabel('Mass')
plt.plot();

### PREDICTIONS ### 
with model_adelie_flipper_regression:
    # Change the underlying value to the mean observed flipper length
    # for our posterior predictive samples
    pm.set_data({"adelie_flipper_length": [adelie_flipper_length_obs.mean()]})
    posterior_predictions = pm.sample_posterior_predictive(
        inf_data_adelie_flipper_regression.posterior, var_names=["mass", "μ"])

# posterior predictive of individual vs. posterior predictive of mean (mu) 
fig, ax = plt.subplots()
az.plot_dist(posterior_predictions["mass"], label="Posterior Predictive of \nIndividual Penguin Mass", ax=ax)
az.plot_dist(posterior_predictions["μ"],label="Posterior Predictive of μ", color="C4", ax=ax)
ax.set_xlim(2900, 4500);
ax.legend(loc=2)
ax.set_xlabel("Mass (grams)")
ax.set_yticks([])
plt.plot(); 

## MAKING beta0 interpretable 
# (1) get mean value for flipper
adelie_flipper_length_c = (adelie_flipper_length_obs -
                           adelie_flipper_length_obs.mean())

# centered model
with pm.Model() as model_adelie_flipper_regression:
    σ = pm.HalfStudentT("σ", 100, 2000)
    beta1 = pm.Normal("beta1", 0, 4000)
    beta0 = pm.Normal("beta0", 0, 4000)
    μ = pm.Deterministic("μ", beta0 + beta1*adelie_flipper_length_c)

    mass = pm.Normal("mass", mu=μ, sigma=σ, observed = adelie_mass_obs)

    # Need to remove this one I find bug
    inf_data_adelie_flipper_length_c = pm.sample(return_inferencedata=True, random_seed=0)

# beta1 is same, but beta0 shifted (because we centered)
# we now get the distribution of weight for mean flipper as beta0 and beta1 retains association. 
az.plot_posterior(inf_data_adelie_flipper_length_c, var_names=["beta0", "beta1"], textsize=20);

### MULTIPLE LINEAR REGRESSSION ###
# second covariate: sex 
# got to here ... 