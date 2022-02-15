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

''' 3. Linear model '''
# https://github.com/BayesianModelingandComputationInPython/BookCode_Edition1/blob/main/notebooks/chp_03.ipynb
### PENGUINS ###
## comparing two groups ## 
penguins = pd.read_csv("../../BookCode_Edition1/data/penguins.csv")
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

# Binary encoding of the categorical predictor
## for males we have 2 terms (beta2 cancels) for females 3 (beta2 matters)
## so beta2 encodes gender difference. 
sex_obs = penguins.loc[adelie_mask ,"sex"].replace({"male":0, "female":1})

with pm.Model() as model_penguin_mass_categorical:
    σ = pm.HalfStudentT("σ", 100, 2000)
    beta0 = pm.Normal("beta0", 0, 3000)
    beta1 = pm.Normal("beta1", 0, 3000)
    beta2 = pm.Normal("beta2", 0, 3000)

    μ = pm.Deterministic(
        "μ", beta0 + beta1 * adelie_flipper_length_obs + beta2 * sex_obs)

    mass = pm.Normal("mass", mu=μ, sigma=σ, observed=adelie_mass_obs)

    inf_data_penguin_mass_categorical = pm.sample(
        target_accept=.9, return_inferencedata=True)

# check it 
az.plot_posterior(inf_data_penguin_mass_categorical, var_names=["beta0", "beta1", "beta2"], textsize=20);
az.plot_trace(inf_data_penguin_mass_categorical, compact=False, divergences="bottom", kind="rank_bars");

## with bambi (not done for now) -- how to specify priors?
import bambi as bmb
model = bmb.Model("body_mass_g ~ flipper_length_mm + sex",
                  penguins[adelie_mask])
trace = model.fit()

## nice plot ##
# Fix colors
fig, ax = plt.subplots()
alpha_1 = inf_data_penguin_mass_categorical.posterior.mean().to_dict()["data_vars"]["beta0"]["data"]
beta_1 = inf_data_penguin_mass_categorical.posterior.mean().to_dict()["data_vars"]["beta1"]["data"]
beta_2 = inf_data_penguin_mass_categorical.posterior.mean().to_dict()["data_vars"]["beta2"]["data"]


flipper_length = np.linspace(adelie_flipper_length_obs.min(), adelie_flipper_length_obs.max(), 100)

mass_mean_male = alpha_1 + beta_1 * flipper_length
mass_mean_female = alpha_1 + beta_1 * flipper_length + beta_2

ax.plot(flipper_length, mass_mean_male,
         label="Male")

ax.plot(flipper_length, mass_mean_female, c='C4',
         label="Female")

ax.scatter(adelie_flipper_length_obs, adelie_mass_obs, c=[{0:"k", 1:"b"}[code] for code in sex_obs.values])

# Figure out how to do this from inference data
#az.plot_hpd(adelie_flipper_length, trace.get_values(varname="μ"), credible_interval=0.94, color='k', ax=ax)

ax.set_xlabel('Flipper Length')
ax.set_ylabel('Mass')
ax.legend()
plt.plot(); 

### model comparison again ###
# new model much better (reduces uncertainty) 
az.plot_forest([inf_data_adelie_penguin_mass,
        inf_data_adelie_flipper_regression,
        inf_data_penguin_mass_categorical],
        var_names=["σ"], combined=True)

## counterfactuals (not run for now) since it is tf (but we can look this up). 

## GLM ##
# logistic
species_filter = penguins["species"].isin(["Adelie", "Chinstrap"])
bill_length_obs = penguins.loc[species_filter, "bill_length_mm"].values
species = pd.Categorical(penguins.loc[species_filter, "species"])

with pm.Model() as model_logistic_penguins_bill_length:
    beta0 = pm.Normal("beta0", mu=0, sigma=10)
    beta1 = pm.Normal("beta1", mu=0, sigma=10)

    μ = beta0 + pm.math.dot(bill_length_obs, beta1)

    # Application of our sigmoid  link function
    θ = pm.Deterministic("θ", pm.math.sigmoid(μ))

    # Useful for plotting the decision boundary later
    bd = pm.Deterministic("bd", -beta0/beta1)

    # Note the change in likelihood
    yl = pm.Bernoulli("yl", p=θ, observed=species.codes)

    prior_predictive_logistic_penguins_bill_length = pm.sample_prior_predictive()
    trace_logistic_penguins_bill_length = pm.sample(5000, chains=2)
    inf_data_logistic_penguins_bill_length = az.from_pymc3(
        prior=prior_predictive_logistic_penguins_bill_length,
        trace=trace_logistic_penguins_bill_length)

# prior expectation (even, as it should be)
ax = az.plot_dist(prior_predictive_logistic_penguins_bill_length["yl"], color="C2")
ax.set_xticklabels(["Adelie: 0", "Chinstrap: 1"] )
plt.plot();

## can do multiple regression for the logistic (not done here). 

## log odds 

## picking priors (sex ratio, McElreath)
# quick plot
x = np.arange(-2,3,1)
y = [50, 44, 50, 47, 56]

import matplotlib.ticker as mtick
fig, ax = plt.subplots()

ax.scatter(x, y)
ax.set_xticks(x)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_ylim(40, 60)
ax.set_xlabel("Attractiveness of Parent")
ax.set_ylabel("% of Girl Babies")
ax.set_title("Attractiveness of Parent and Sex Ratio")
plt.plot(); 

# uninformative priors (very wide)
with pm.Model() as model_uninformative_prior_sex_ratio:
    σ = pm.Exponential("σ", .5)
    beta1 = pm.Normal("beta1", 0, 20) # 0 --> no slope (no difference by att. of parent)
    beta0 = pm.Normal("beta0", 50, 20) # 50 --> 50% --> equal sex-ratio

    μ = pm.Deterministic("μ", beta0 + beta1 * x)

    ratio = pm.Normal("ratio", mu=μ, sigma=σ, observed=y)

    prior_predictive_uninformative_prior_sex_ratio = pm.sample_prior_predictive(
        samples=10000)
    trace_uninformative_prior_sex_ratio = pm.sample(random_seed=0)
    inf_data_uninformative_prior_sex_ratio = az.from_pymc3(
        trace=trace_uninformative_prior_sex_ratio,
        prior=prior_predictive_uninformative_prior_sex_ratio)

# check posterior (overlap with 50 and 0, so no effect). 
az.plot_posterior(inf_data_uninformative_prior_sex_ratio.prior, var_names=["beta0", "beta1"])

# stats summary
az.summary(inf_data_uninformative_prior_sex_ratio, var_names=["beta0", "beta1", "σ"], kind="stats")

# check prior and posterior
# prior is too wide here (i.e. we have "impossible" cases, such as 105 boys per 100 births -- intercept)
# good plot code here to look at. 

## new model (very informative)
with pm.Model() as model_informative_prior_sex_ratio:
    σ = pm.Exponential("σ", .5)
    beta1 = pm.Normal("beta1", 0, .5)
    beta0 = pm.Normal("beta0", 48.5, .5)

    μ = pm.Deterministic("μ", beta0 + beta1 * x)

    ratio = pm.Normal("ratio", mu=μ, sigma=σ, observed=y)


    prior_predictive_informative_prior_sex_ratio = pm.sample_prior_predictive(
        samples=10000)
    trace_informative_prior_sex_ratio = pm.sample(random_seed=0)
    inf_data_informative_prior_sex_ratio = az.from_pymc3(
        trace=trace_informative_prior_sex_ratio,
        prior=prior_predictive_informative_prior_sex_ratio)

# biases the model (constrains) too much, i.e. we force it to be less than 50%
az.summary(inf_data_informative_prior_sex_ratio, var_names=["beta0", "beta1", "σ"], kind="stats")

