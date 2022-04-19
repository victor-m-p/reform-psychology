#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Simulate and Predict"
#' author: "Victor M. Poulsen" 
#' output: html_document
#' ---
#' 
#' 
## ----setup, include=FALSE-----------------------------------------------------

inpath <- "/work/50114/MAG/data/modeling/"
## infile <- "psychology_replication_matched.csv"
## inpath_post <- "/work/50114/MAG/modeling/models/replication_fos/main_model/m_post.rds"
## outpath <- "/work/50114/MAG/fig/modeling/replication_fos/simulate_predict/"
infile <- args[1]
inpath_post <- args[2]
outpath <- args[3]
tag <- args[4]


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


#' 
#' # Visual setup 
#' 
## -----------------------------------------------------------------------------

color_scheme_set("orange")
theme_set(theme_classic())

theme_set(theme_classic())
title = 18
label = 14
tick = 12 # same as legend

color_map <- c("Control" = '#fdae6b', 
               "Experiment" = '#e6550d')

categories <- c("Control",
                "Experiment")

clrs = c("#1b9e77", "#d95f02") # c('#e6550d', '#fdae6b')


#' 
#' # Load data
#' 
## -----------------------------------------------------------------------------

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
#' # Load Model
#' 
## -----------------------------------------------------------------------------

m_post <- readRDS(paste0(inpath_post))


#' 
#' # Prediction
#' 
#' ## generate simulated data
#' 
## -----------------------------------------------------------------------------

base_id = 2000
levels <- nrow(d)/2
max_id = base_id + levels - 1

d_pred <- d %>% dplyr::select(condition_fct, log_teamsize, year_after_2005) %>%
  mutate(id_match = as_factor(rep(base_id:max_id, each = 2))) %>% # new ids 
  add_predicted_draws(m_post, allow_new_levels = T) # no cutoff


#' 
#' ## power-scale plot
#' 
## -----------------------------------------------------------------------------

library(scales) # to access break formatting functions

# adding very small number to avoid log(0). 
p <- d_pred %>% group_by(condition_fct, .prediction) %>% 
  # prepare
  summarize(count = n()) %>%
  mutate(prediction = .prediction,
         N = count) %>% 
  # plot 
  ggplot(aes(x = prediction, y = N)) + #, color = condition_fct)) + 
  geom_freqpoly(data = . %>% filter(condition_fct == "control"), 
                stat = 'identity',
                aes(color = categories[1])) + 
  geom_freqpoly(data = . %>% filter(condition_fct == "experiment"), 
                stat = 'identity',
                aes(color = categories[2])) + 
  geom_vline(xintercept = 10) + 
  geom_vline(xintercept = 100) +
  geom_vline(xintercept = 1000) +
  annotate("text", x = 15, y = 10000, label = TeX("$c_5 = 10$"), size = 4) + 
  annotate("text", x = 160, y = 10000, label = TeX("$c_5 = 100$"), size = 4) + 
  annotate("text", x = 1700, y = 10000, label = TeX("$c_5 = 1000$"), size = 4) + 
  scale_x_log10(breaks = trans_breaks("log10", function(x) 10^x),
                labels = trans_format("log10", math_format(10^.x))) +
  scale_y_log10(breaks = trans_breaks("log10", function(x) 10^x),
                labels = trans_format("log10", math_format(10^.x))) +
  labs(title = "", # "Model Simulated Data",
       x = TeX("$c_5$"),
       y = "N") +
  scale_color_manual(
      breaks = categories, 
      values = color_map,
      guide = guide_legend(title = NULL)) +
  theme(plot.title = element_text(hjust = 0.5, size = title),
        axis.text = element_text(size = tick),
        axis.title = element_text(size = label),
        legend.text = element_text(size = tick),
        legend.position = "bottom") 

p


#' 
#' ## save power plot
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, "model_simulation_power.pdf"),
       plot = p,
       width = 8,
       height = 5.5)


#' 
#' # probability of hit
#' 
## -----------------------------------------------------------------------------

# function
n_above <- function(d, cutoff){
  
  divisor = nrow(d)/2
  label = paste0("above_", cutoff)
  d_above <- d %>% 
    group_by(condition_fct) %>%
    filter(.prediction > cutoff) %>%
    summarize(count = n()) %>%
    mutate(
      percent_of_total = round((count / divisor)*100, 2),
      percent_of_above = round((count / sum(count))*100, 2),
      type = label)
  
  return(d_above)
  
}

# generate 
d_0 <- n_above(d_pred, 0) # visible
d_10 <- n_above(d_pred, 10) # ...
d_100 <- n_above(d_pred, 100) # hit
d_1000 <- n_above(d_pred, 1000) # ...

# bind 
d_summary <- bind_rows(d_0, 
                       d_10,
                       d_100,
                       d_1000)

# save
write_csv(d_summary, paste0(outpath, "d_summary.csv"))


#' 
#' ## conditional means / counterfactuals ##
#' https://cran.r-project.org/web/packages/tidybayes/vignettes/tidy-brms.html
#' 
#' ### NOTE: 
#' We should do it for minimum values instaed of mean values & 
#' then provide it with more uncertainty in SI. 
#' 
#' #### TEAMSIZE 
#' 
#' ##### Create data
#' 
## -----------------------------------------------------------------------------

# fix year at min
d_team_min <- d %>%
    group_by(condition_fct) %>%
    data_grid(log_teamsize = seq_range(log_teamsize, n = 101), # sequence of values
              year_after_2005 = min(year_after_2005)) %>% # fixed year
    add_epred_draws(m_post, re_formula = NA) # no random eff. uncertainty


#' 
#' ##### Natural scale
#' 
## -----------------------------------------------------------------------------

plt_team_nat <- function(draws, d, clrs, xlim, ylim){
  
  p <- draws %>% ggplot(aes(x = exp(log_teamsize), 
                       y = c_5, 
                       color = ordered(condition_fct), 
                       fill = ordered(condition_fct))) +
    geom_jitter(data = d, alpha = 0.1) + 
    stat_lineribbon(aes(y = .epred), .width = c(.95, .80), alpha = 1/4) +
    labs(title = "Average", #  "Expected Value (mean actor)",
         x = "TEAMSIZE",
         y = TeX("$c_5$")) +
    theme(plot.title = element_text(hjust = 0.5, size = title),
          axis.text = element_text(size = tick),
          axis.title = element_text(size = label),
          legend.text = element_text(size = tick),
          legend.position = "bottom") +
    scale_color_manual(
      values = clrs,
      guide = guide_legend(title = NULL)) +
    scale_fill_manual(
      values = clrs,
      guide = guide_legend(title = NULL)) +
    ylim(0, ylim) +
    xlim(0, xlim)
  
  return(p)
  
}
  

#' 
#' ##### All data 
#' 
#' min team
#' 
## -----------------------------------------------------------------------------

y_max = quantile(d_team_min$.epred, .9999)
p_team_full <- plt_team_nat(d_team_min, d, clrs, max(d$n_authors), y_max)


#' 
#' #### Capped (& min year)
#' 
## -----------------------------------------------------------------------------

dsub <- d_team_min %>% filter(exp(log_teamsize) <= 20)
y_max <- quantile(dsub$.epred, .9999)
p_team_lim <- plt_team_nat(d_team_min, d, clrs, 20, y_max)


#' 
#' ##### Marginalized (Natural Scale)
#' 
#' TEAMSIZE draws (CI bands) marginalized study and mean YEAR (2010).
#' 
#' EXPLANATION:
#' Based on our fitted BETA values (population) and random-effects (group-level) variation
#' we plot the expected value based on a number of draws (and 95% and 80% confidence intervals). 
#' We marginalize over the random-effects of study (see McElreath & mjskay) and generalize
#' to new population??
#' 
## -----------------------------------------------------------------------------

CI_team_marginalized <- function(d, clrs, xlim){
  
  # fitted means (marginalized)
  base_id = 2000
  levels <- nrow(d)/2
  max_id = base_id + levels - 1
  
  draws <- d %>%
    group_by(condition_fct) %>%
    data_grid(log_teamsize = seq_range(log_teamsize, n = 101),
              id_match = as_factor(rep(base_id:max_id, each = 2)),
              year_after_2005 = min(year_after_2005)) %>% # fixed year
    add_epred_draws(m_post, ndraws = 100, re_formula = NULL, allow_new_levels = TRUE) # marginalize 
  
  draws_sub <- draws %>% filter(exp(log_teamsize) <= xlim)
  ymax <- quantile(draws_sub$.epred, .999)
  
  p <- draws %>% 
    ggplot(aes(x = exp(log_teamsize), 
               y = c_5, 
               color = ordered(condition_fct), 
               fill = ordered(condition_fct))) +
    geom_jitter(data = d, alpha = 0.1) + 
    stat_lineribbon(aes(y = .epred), .width = c(.95, .80), alpha = 1/4) +
    labs(title = "Marginal", #  "Expected Value (mean actor)",
         x = "TEAMSIZE",
         y = TeX("$c_5$")) +
    theme(plot.title = element_text(hjust = 0.5, size = title),
          axis.text = element_text(size = tick),
          axis.title = element_text(size = label),
          legend.text = element_text(size = tick),
          legend.position = "bottom") +
    scale_color_manual(
      values = clrs,
      guide = guide_legend(title = NULL)) +
    scale_fill_manual(
      values = clrs,
      guide = guide_legend(title = NULL)) +
    ylim(0, ymax) +
    xlim(0, xlim)
  
  return(p)
  
}


#' 
#' ## DRAW THEM 
#' 
#' Still need to really understand this. 
#' We are interested in the mean still (epred) 
#' but now we draw from everything. 
#' I thought that what we did was draw from everything and take the mean a lot of times -- 
#' which could never result in this much uncertainty...?
#' 
## -----------------------------------------------------------------------------

p_team_marginalize_lim <- CI_team_marginalized(d, clrs, 20)


#' 
## -----------------------------------------------------------------------------

p_team_marginalize_full <- CI_team_marginalized(d, clrs, max(d$n_authors))


#' 
#' #### GATHER IN FIG (lim) ####
#' 
## -----------------------------------------------------------------------------

p_grid <- ggarrange(p_team_lim,
                    p_team_marginalize_lim, 
                    ncol = 2, 
                    common.legend = TRUE, 
                    legend = 'bottom',
                    labels = c("A", "B"))



#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "conditional_team_lim.pdf"),
       plot = p_grid,
       width = 8,
       height = 4)


#' 
#' #### GATHER IN FIG (full) ####
#' 
## -----------------------------------------------------------------------------

p_grid <- ggarrange(p_team_full,
                    p_team_marginalize_full, 
                    ncol = 2, 
                    common.legend = TRUE, 
                    legend = 'bottom',
                    labels = c("A", "B"))



#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "conditional_team_full.pdf"),
       plot = p_grid,
       width = 8,
       height = 4)


#' 
#' #### YEAR 
#' 
#' ##### create data
#' 
## -----------------------------------------------------------------------------

d_year_min <- d %>%
    group_by(condition_fct) %>%
    data_grid(log_teamsize = min(log_teamsize), # sequence of values
              year_after_2005 = seq_range(year_after_2005, 101)) %>% # fixed year
    add_epred_draws(m_post, re_formula = NA) # no random eff. uncertainty


#' 
#' ##### natural scale
#' 
## -----------------------------------------------------------------------------

plt_year <- function(draws, d, clrs, ylim){
  
  p <- draws %>% ggplot(aes(x = year_after_2005, 
                       y = c_5, 
                       color = ordered(condition_fct), 
                       fill = ordered(condition_fct))) +
      #geom_jitter(data = d, alpha = 0.8) + 
      stat_lineribbon(aes(y = .epred), .width = c(.95, .80), alpha = 1/4) +
      labs(title = "Average", #  "Expected Value (mean actor)",
           x = "YEAR",
           y = TeX("$c_5$")) +
      theme(plot.title = element_text(hjust = 0.5, size = title),
            axis.text = element_text(size = tick),
            axis.title = element_text(size = label),
            legend.text = element_text(size = tick),
            legend.position = "bottom") +
      scale_color_manual(
        values = clrs,
        guide = guide_legend(title = NULL)) +
      scale_fill_manual(
        values = clrs,
        guide = guide_legend(title = NULL)) +
      ylim(0, ylim) 
  
  return(p)
}


#' 
#' #### plot it 
#' 
#' https://mjskay.github.io/tidybayes/reference/add_predicted_draws.html
#' 
#' Fixing teamsize at minimum (solo-authored paper) and varying YEAR over a grid from 2005 (YEAR = 0) to 2015 (YEAR = 10).
#' Draws from the expectation of the posterior predictive distribution (see link). 
#' setting the group-level effects to their mean and only displaying the uncertainty for our population estimates. 
#' Bold line indicates the mean, and CI-bands of 80% and 95% uncertainty intervals (credibility, confidence...). 
#' 
## -----------------------------------------------------------------------------

ymax = max(d_year_min$.epred) 
p_year <- plt_year(d_year_min, d, clrs, ymax)


#' 
#' ##### marginalized 
#' 
## -----------------------------------------------------------------------------

CI_year_marginalized <- function(d, clrs, xlim){
  
  # fitted means (marginalized)
  base_id = 2000
  levels <- nrow(d)/2
  max_id = base_id + levels - 1
  
  draws <- d %>%
    group_by(condition_fct) %>%
    data_grid(year_after_2005 = seq_range(year_after_2005, n = 101),
              id_match = as_factor(rep(base_id:max_id, each = 2)),
              log_teamsize = min(log_teamsize)) %>% # fixed year
    add_epred_draws(m_post, ndraws = 100, re_formula = NULL, allow_new_levels =TRUE) # marginalize 
  
  
  draws_sub <- draws %>% filter(exp(year_after_2005) <= xlim)
  ymax <- quantile(draws_sub$.epred, .999)
  
  p <- draws %>% ggplot(aes(x = year_after_2005, 
               y = c_5, 
               color = ordered(condition_fct), 
               fill = ordered(condition_fct))) +
    stat_lineribbon(aes(y = .epred), .width = c(.95, .80), alpha = 1/4) +
    labs(title = "Marginal", 
         x = "YEAR",
         y = TeX("$c_5$")) +
    theme(plot.title = element_text(hjust = 0.5, size = title),
          axis.text = element_text(size = tick),
          axis.title = element_text(size = label),
          legend.text = element_text(size = tick),
          legend.position = "bottom") +
    scale_color_manual(
      values = clrs, 
      guide = guide_legend(title = NULL)) +
    scale_fill_manual(
      values = clrs, 
      guide = guide_legend(title = NULL)) +
    ylim(0, ymax) +
    xlim(0, xlim)
  
  return(p)
    
}

#' 
#' ## plot marginalized
#' Fixing teamsize at minimum (solo-authored paper) and varying YEAR over a grid from 2005 (YEAR = 0) to 2015 (YEAR = 10).
#' Draws from the expectation of the posterior predictive distribution (see link). 
#' Incorporating varying effects uncertainty, by simulating from the posterior standard deviation of group-level effects
#' (marginalizing over random effects). Shows that there is a lot of uncertainty between levels (groups). 
#' 
## -----------------------------------------------------------------------------

p_year_marginalized <- CI_year_marginalized(d, clrs, max(d$year_after_2005))


#' 
#' ### GATHER IN FIG ###
#' 
## -----------------------------------------------------------------------------

p_grid <- ggarrange(p_year,
                    p_year_marginalized, 
                    ncol = 2, 
                    common.legend = TRUE, 
                    legend = 'bottom',
                    labels = c("A", "B"))



#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "conditional_year.pdf"),
       plot = p_grid,
       width = 8,
       height = 4)


#' 
