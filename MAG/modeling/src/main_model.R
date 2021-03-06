#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Fit main model"
#' author: "Victor M. Poulsen"
#' output: html_document
#' ---
#' 
#' # Path setup
#' 
## -----------------------------------------------------------------------------

wd_code <- "/work/50114/MAG/modeling/src"
inpath <- "/work/50114/MAG/data/modeling/"
infile <- args[1]
outpath_models <- args[2]

#' 
#' 
#' # VMP 2022-03-11
#' 
## -----------------------------------------------------------------------------

# consider pacman
if (!require("pacman")){
  install.packages("pacman") # repos = "http://cran.r-project.org"
}

pacman::p_load(tidyverse, 
               brms, 
               ggthemes, 
               bayesplot, 
               cowplot, 
               tidybayes, 
               modelr, 
               latex2exp, 
               ggpubr)

# set up cmdstanr if it is not already present
if (!require('cmdstanr')){
  print("installing cmdstanr")
  install.packages("cmdstanr", repos = c("https://mc-stan.org/r-packages/", getOption("repos")))
  library(cmdstanr)
  install_cmdstan(cores = 2, overwrite = TRUE)
}

setwd(wd_code)
source("fun_helper.R")



#' 
#' load data
#' 
## ----setup, include=FALSE-----------------------------------------------------

csv_path <- paste0(inpath, infile)

# check data
d <- read_csv(csv_path) %>%
  mutate(log_teamsize = log(n_authors), 
         condition_fct = as_factor(condition), 
         condition_fct = fct_relevel(condition_fct, c("experiment", "control")),
         id_match = as_factor(match_group),
         id_dct = as_factor(PaperId),
         year_after_2005 = Year - 2005) 


#' 
#' model formula
#' 
## -----------------------------------------------------------------------------

f <- bf(c_5 ~ 0 + condition_fct + condition_fct:log_teamsize + condition_fct:year_after_2005 + (0 + condition_fct | id_match))


#' 
#' 
#' # get prior:
#' * b: effects.
#' * cor: correlation of random effecs I think
#' * sd: match and both conditions.
#' * shape: overdispersion parameter for negative binomial.
#' 
## ----setup, include=FALSE-----------------------------------------------------

get_prior(
  formula = f,
  data = d, 
  family = negbinomial())


#' 
#' 
#' # prior for main model
#' 
## -----------------------------------------------------------------------------

# informed by prior-posterior update
p <- c(prior(exponential(0.5), class = shape), # overdispersion parameter
       prior(normal(log(10), 0.5), class = b, coef = "condition_fctcontrol"),
       prior(normal(log(10), 0.5), class = b, coef = "condition_fctexperiment"),
       prior(normal(0.5, 0.5), class = b, coef = "condition_fctcontrol:log_teamsize"),
       prior(normal(0.5, 0.5), class = b, coef = "condition_fctexperiment:log_teamsize"),
       prior(normal(0, 0.5), class = b, coef = "condition_fctcontrol:year_after_2005"),
       prior(normal(0, 0.5), class = b, coef = "condition_fctexperiment:year_after_2005"),
       prior(exponential(1), class = sd),
       prior(lkj(5), class = cor)) # Solomon Kurz (less flat). 


#' 
#' # fit model (sample prior)
#' 
## ---- include = FALSE---------------------------------------------------------

# no divergences. 
m_prior <- fit_model(
  d = d,
  family = negbinomial(), 
  formula = f, 
  prior = p,
  sample_prior = "only",
  file = paste0(outpath_models, "m_prior")
)


#' 
#' # fit model (sample posterior)
#' 
## ----setup, include=FALSE-----------------------------------------------------

m_post <- fit_model(
  d = d,
  family = negbinomial(), 
  formula = f, 
  prior = p,
  sample_prior = TRUE,
  file = paste0(outpath_models, "m_post")
)


#' 
