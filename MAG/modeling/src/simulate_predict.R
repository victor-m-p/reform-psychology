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



#' 
## -----------------------------------------------------------------------------

# consider pacman
if (!require("pacman")){
  install.packages("pacman") # repos = "http://cran.r-project.org"
}

library(pacman)
p_load(tidyverse, brms, ggthemes, bayesplot, cowplot, tidybayes, modelr, latex2exp, ggpubr)

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


#' 
#' # Load data
#' 
## -----------------------------------------------------------------------------

csv_path <- paste0(inpath, infile)

# check data
d <- read_csv(csv_path) %>%
  mutate(log_teamsize = log(n_authors), 
         condition_fct = as_factor(condition), 
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
  add_predicted_draws(m_post, ndraws = 100, allow_new_levels = T)


#' 
#' ## log-log plot 
#' 
## -----------------------------------------------------------------------------

# adding very small number to avoid log(0). 
p <- d_pred %>% group_by(condition_fct, .prediction) %>% 
  # prepare
  summarize(count = n()) %>%
  mutate(log_prediction = log(.prediction + 1),
         log_count = log(count + 1)) %>% 
  # plot 
  ggplot(aes(x = log_prediction, y = log_count)) + #, color = condition_fct)) + 
  geom_freqpoly(data = . %>% filter(condition_fct == "control"), 
                stat = 'identity',
                aes(color = categories[1])) + 
  geom_freqpoly(data = . %>% filter(condition_fct == "experiment"), 
                stat = 'identity',
                aes(color = categories[2])) + 
  geom_vline(xintercept = log(10)) + 
  geom_vline(xintercept = log(100)) +
  geom_vline(xintercept = log(1000)) +
  annotate("text", x = log(15), y = 9, label = TeX("$c_5 = 10$"), size = 4) + 
  annotate("text", x = log(160), y = 9, label = TeX("$c_5 = 100$"), size = 4) + 
  annotate("text", x = log(1700), y = 9, label = TeX("$c_5 = 1000$"), size = 4) + 
  labs(title = "Model Simulated Data",
       x = TeX("log($c_5$)"),
       y = "log(N)") +
  scale_color_manual(
      breaks = categories, 
      values = color_map,
      guide = guide_legend(title = NULL)) +
  theme(plot.title = element_text(hjust = 0.5, size = title),
        axis.text = element_text(size = tick),
        axis.title = element_text(size = label),
        legend.text = element_text(size = tick),
        legend.position = "bottom") 


#' 
#' ## save log-log plot 
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, "model_simulation_log.pdf"),
       plot = p,
       width = 8,
       height = 5.5) # half page


#' 
#' ## power-scale plot
#' 
## -----------------------------------------------------------------------------

library(MASS) # to access Animals data sets
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
  labs(title = "Model Simulated Data",
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
