#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Likelihood Comparison"
#' author: "Victor M. Poulsen" 
#' output: html_document
#' ---
#' 
#' # VMP 2022-03-09: should be done now. 
#' 
#' ## paths setup
#' 
#' 
## -----------------------------------------------------------------------------

wd_code <- "/work/50114/MAG/modeling/src"
inpath <- "/work/50114/MAG/data/modeling/"
infile <- args[1]
outpath_models <- args[2]
outpath_fig <- args[3]
tag <- args[4]

#' 
#' 
#' # setup 
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
  install.packages("cmdstanr", repos = c("https://mc-stan.org/r-packages/", getOption("repos")))
  library(cmdstanr)
  install_cmdstan(cores = 2, overwrite = TRUE)
}

setwd(wd_code)
source("fun_helper.R")

#' 
#' ## visual setup
#' 
#' consider (a) text-size and (b) width/height
#' 
## -----------------------------------------------------------------------------

# text size: 
# https://statisticsglobe.com/change-font-size-of-ggplot2-plot-in-r-axis-text-main-title-legend

# ggsave: 
# https://ggplot2.tidyverse.org/reference/ggsave.html


color_scheme_set("orange")
theme_set(theme_classic())

theme_set(theme_classic())
title = 18
label = 14
tick = 12 # same as legend


#' 
#' 
#' # read data and create some variables
#' ## (1) temsize log. 
#' ## (2) match group as id 
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
#' # define model
#' 
## -----------------------------------------------------------------------------

f <- bf(c_5 ~ 0 + condition_fct + condition_fct:log_teamsize + condition_fct:year_after_2005 + (0 + condition_fct | id_match))


#' 
#' # get priors 
#' 
#' ## zero-inflated poisson: 
#' b, cor, sd, zi
#' 
#' ## negative binomial: 
#' b, cor, sd, shape 
#' 
#' ## zero-inflated negative binomial: 
#' b, cor, sd, shape, zi 
#' 
#' 
## ----setup, include=FALSE-----------------------------------------------------

get_prior(
  formula = f, 
  data = d, 
  family = negbinomial()
)

get_prior(
  formula = f,
  data = d,
  family = zero_inflated_poisson(),
)

get_prior(
  formula = f,
  data = d,
  family = zero_inflated_negbinomial()
)


#' 
#' # check data
#' 
## ----setup, include=FALSE-----------------------------------------------------

d %>% filter(n_authors == 1) %>%
  summarize(mean = mean(c_5))


#' 
#' 
#' # define priors 
#' 
## -----------------------------------------------------------------------------

## prior negative binomial (also the priors for main model)
p_negbin <- c(prior(exponential(0.5), class = shape), # overdispersion parameter
              prior(normal(log(10), 0.5), class = b, coef = "condition_fctcontrol"),
              prior(normal(log(10), 0.5), class = b, coef = "condition_fctexperiment"),
              prior(normal(0.5, 0.5), class = b, coef = "condition_fctcontrol:log_teamsize"),
              prior(normal(0.5, 0.5), class = b, coef = "condition_fctexperiment:log_teamsize"),
              prior(normal(0, 0.5), class = b, coef = "condition_fctcontrol:year_after_2005"),
              prior(normal(0, 0.5), class = b, coef = "condition_fctexperiment:year_after_2005"),
              prior(exponential(1), class = sd),
              prior(lkj(5), class = cor)) # Solomon Kurz (less flat). 

## prior zero-inflated poisson
p_zip <- c(prior(beta(2, 2), class = zi), # overdispersion parameter
           prior(normal(log(10), 0.5), class = b, coef = "condition_fctcontrol"),
           prior(normal(log(10), 0.5), class = b, coef = "condition_fctexperiment"),
           prior(normal(0.5, 0.5), class = b, coef = "condition_fctcontrol:log_teamsize"),
           prior(normal(0.5, 0.5), class = b, coef = "condition_fctexperiment:log_teamsize"),
           prior(normal(0, 0.5), class = b, coef = "condition_fctcontrol:year_after_2005"),
           prior(normal(0, 0.5), class = b, coef = "condition_fctexperiment:year_after_2005"),
           prior(exponential(1), class = sd),
           prior(lkj(5), class = cor)) # Solomon Kurz (less flat). 

## prior zero-inflated negative binomial
p_zinegbin <- c(prior(exponential(0.5), class = shape), # overdispersion parameter
                prior(beta(2, 2), class = zi),
                prior(normal(log(10), 0.5), class = b, coef = "condition_fctcontrol"),
                prior(normal(log(10), 0.5), class = b, coef = "condition_fctexperiment"),
                prior(normal(0.5, 0.5), coef = "condition_fctcontrol:log_teamsize"),
                prior(normal(0.5, 0.5), coef = "condition_fctexperiment:log_teamsize"),
                prior(normal(0, 0.5), class = b, coef = "condition_fctcontrol:year_after_2005"),
                prior(normal(0, 0.5), class = b, coef = "condition_fctexperiment:year_after_2005"),
                prior(exponential(1), class = sd),
                prior(lkj(5), class = cor)) # Solomon Kurz (less flat). 


#' 
#' # sample prior (NB: reproducibility with seed from fun_helper.R)
#' 
## ---- include=FALSE-----------------------------------------------------------

## sample prior for negative binomial (no divergences)
m_prior_negbin <- fit_model(
  d = d,
  family = negbinomial(), 
  formula = f,
  prior = p_negbin,
  sample_prior = "only",
  file = paste0(outpath_models, "m_prior_negbin")
)

## sample prior for zero-inflated poisson (no divergences)
m_prior_zip <- fit_model(
  d = d,
  family = zero_inflated_poisson(),
  formula = f,
  prior = p_zip,
  sample_prior = "only",
  file = paste0(outpath_models, "m_prior_zip")
)

## sample prior for zero-inflated negative binomial (no divergences)
m_prior_zinegbin <- fit_model(
  d = d,
  family = zero_inflated_negbinomial(),
  formula = f,
  prior = p_zinegbin, 
  sample_prior = "only",
  file = paste0(outpath_models, "m_prior_zinegbin")
)


#' 
#' # sample posterior 
#' 
## ---- include=FALSE-----------------------------------------------------------

## sample posterior for negative binomial (174 pareto_k > 0.7 & 136 (8.7%) p_waic > 0.4)
m_post_negbin <- fit_model(
  d = d,
  family = negbinomial(), 
  formula = f,
  prior = p_negbin,
  sample_prior = TRUE,
  file = paste0(outpath_models, "m_post_negbin") 
)

## sample posterior for zero-inflated poisson (1086 pareto_k > 0.7 & 1222 (78.0%) p_waic > 0.4)
m_post_zip <- fit_model(
  d = d,
  family = zero_inflated_poisson(),
  formula = f,
  prior = p_zip,
  sample_prior = TRUE,
  file = paste0(outpath_models, "m_post_zip") 
)

## sample posterior for zero-inflated negative binomial (405 pareto_k > 0.7 & 383 (24.5%) p_waic > 0.4)
m_post_zinegbin <- fit_model(
  d = d,
  family = zero_inflated_negbinomial(),
  formula = f,
  prior = p_zinegbin, 
  sample_prior = TRUE,
  file = paste0(outpath_models, "m_post_zinegbin") 
)


#' 
#' # combo plot
#' 
## -----------------------------------------------------------------------------

plot_combo <- function(m_post, filename, tick_size, label_size, height = 11, width = 8){
  
  p <- as_draws_df(m_post) %>%
  rename(#chain = `.chain`,
         `beta[CONTROL]` = `b_condition_fctcontrol`,
         `beta[EXPERIMENT]` = `b_condition_fctexperiment`,
         `beta[CONTROL:TEAMSIZE]` = `b_condition_fctcontrol:log_teamsize`,
         `beta[EXPERIMENT:TEAMSIZE]` = `b_condition_fctexperiment:log_teamsize`,
         `beta[CONTROL:YEAR]` = `b_condition_fctcontrol:year_after_2005`,
         `beta[EXPERIMENT:YEAR]` = `b_condition_fctexperiment:year_after_2005`) %>%
  mcmc_combo(combo = c("dens_overlay", "trace"),
             pars = vars(contains("beta")),
             facet_args = list(labeller = label_parsed),
             gg_theme = theme(legend.position = "none",
                              strip.text.y = element_text(angle = 0),
                              axis.text = element_text(size = tick_size),
                              axis.title = element_text(size = label_size),
                              strip.background = element_blank()) + facet_text(size=label_size)) 
  
  ggsave(filename = filename, 
         plot = p,
         height = 8,
         width = 8)
  
}

             

#' 
## -----------------------------------------------------------------------------

plot_combo(m_post = m_post_negbin,
           filename = paste0(outpath_fig, tag, "negbin_combo.pdf"),
           tick_size = tick,
           label_size = label)

plot_combo(m_post = m_post_zip,
           filename = paste0(outpath_fig, tag, "zip_combo.pdf"),
           tick_size = tick,
           label_size = label)

plot_combo(m_post = m_post_zinegbin,
           filename = paste0(outpath_fig, tag, "zinegbin_combo.pdf"),
           tick_size = tick,
           label_size = label)


#' 
#' # pareto
#' 
## -----------------------------------------------------------------------------

pareto_k <- function(d, m, likelihood){
  # d: dataframe 
  # m: model 
  # likelihood: string (for printing only)
  
  d_pareto <- d %>%
    mutate(k = m$criteria$loo$diagnostics$pareto_k) %>%
    filter(k > .7) %>%
    summarize(pareto_k = n()) 

  return(d_pareto)
  
}


#' 
## -----------------------------------------------------------------------------

pareto_negbin <- pareto_k(d, m_post_negbin, "pareto_k > 0.7 (negative binomial)") # 195
pareto_zip <- pareto_k(d, m_post_zip, "pareto_k > 0.7 (zero-inflated poisson)") # 1086
pareto_zinegbin <- pareto_k(d, m_post_zinegbin, "pareto_k > 0.7 (zero-inflated negative binomial)") # 447


#' 
#' # Rhat + Eff. samples
#' 
## -----------------------------------------------------------------------------

summary_diagnostics <- function(m){ # m = model
  
  # get brmssummary object
  m_summary <- print(m)
  
  # get data
  d_fixed <- as.data.frame(m_summary$fixed) %>% select(Rhat, Bulk_ESS, Tail_ESS)
  d_family <- as.data.frame(m_summary$spec_pars) %>% select(Rhat, Bulk_ESS, Tail_ESS)
  d_group <- as.data.frame(m_summary$random) %>% rename_with(~ gsub("id_match.", "", .)) %>% select(Rhat, Bulk_ESS, Tail_ESS)
  
  # summarize 
  d_summary <- bind_rows(d_fixed, d_family, d_group) %>%
    summarize(max_rhat = round(max(Rhat), 2),
              min_tail = round(min(Tail_ESS), 2),
              min_bulk = round(min(Bulk_ESS), 2))
  
  # return
  return(d_summary)
  
}

#' 
## ---- include=FALSE-----------------------------------------------------------

summary_negbin <- summary_diagnostics(m_post_negbin)
summary_zip <- summary_diagnostics(m_post_zip)
summary_zinegbin <- summary_diagnostics(m_post_zinegbin)


#' 
#' # cbind and save 
#' 
## -----------------------------------------------------------------------------

diagnostics_negbin <- cbind(summary_negbin, pareto_negbin)
diagnostics_zip <- cbind(summary_zip, pareto_zip)
diagnostics_zinegbin <- cbind(summary_zinegbin, pareto_zinegbin)

write_csv(diagnostics_negbin, paste0(outpath_fig, "diagnostics_negbin.csv"))
write_csv(diagnostics_zip, paste0(outpath_fig, "diagnostics_zip.csv"))
write_csv(diagnostics_zinegbin, paste0(outpath_fig, "diagnostics_zinegbin.csv"))


#' 
