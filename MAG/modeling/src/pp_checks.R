#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Prior/Posterior Predictive Checks"
#' author: "Victor M. Poulsen" 
#' output: html_document
#' ---
#' 
#' # Path setup
#' 
## -----------------------------------------------------------------------------

#wd_code = "/work/50114/MAG/modeling/replication_fos/code"
inpath_csv <- "/work/50114/MAG/data/modeling/"
## infile <- "psychology_replication_matched.csv"
## outpath <- "/work/50114/MAG/fig/modeling/replication_fos/pp_checks/"
## inpath_rds <- "/work/50114/MAG/modeling/models/replication_fos/main_model/"
infile <- args[1]
outpath <- args[2]
inpath_rds <- args[3]
tag <- args[4]
inpath_post <- paste0(inpath_rds, "m_post.rds")
inpath_prior <- paste0(inpath_rds, "m_prior.rds")


#' 
#' # Packages
#' 
## ---- include=FALSE-----------------------------------------------------------

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

#setwd(wd_code)
source("fun_helper.R")


#' 
#' # Aesthetics
#' 
## -----------------------------------------------------------------------------

color_scheme_set("orange")
theme_set(theme_classic())

theme_set(theme_classic())
title = 18
label = 14
tick = 12 # same as legend


#' 
#' # Read data
#' 
## ---- include = FALSE---------------------------------------------------------

csv_path <- paste0(inpath_csv, infile)

# check data
d <- read_csv(csv_path) %>%
  mutate(log_teamsize = log(n_authors), 
         condition_fct = as_factor(condition), 
         condition_fct = fct_relevel(condition_fct, c("experiment", "control")),
         id_match = as_factor(match_group),
         id_dct = as_factor(PaperId),
         year_after_2005 = Year - 2005) 


#' 
#' 
#' # Read models (RDS) 
#' 
## -----------------------------------------------------------------------------

m_prior <- readRDS(inpath_prior)
m_post <- readRDS(inpath_post)


#' 
#' # get draws 
#' 
## -----------------------------------------------------------------------------

# y: actual data 
y <- d$c_5 

# yrep: draws from prior and posterior predictive distributions
yrep_prior <- posterior_predict(m_prior, draws = 500) 
yrep_post <- posterior_predict(m_post, draws = 500) 


#' 
#' 
#' # Prior predictive checks:
#' https://cran.r-project.org/web/packages/bayesplot/vignettes/graphical-ppcs.html
#' https://mc-stan.org/bayesplot/reference/PPC-overview.html
#' 
#' ## density
#' 
#' 
## -----------------------------------------------------------------------------

plot_dens_overlay_limit <- function(y, 
                                yrep, 
                                labeltext,
                                label_size, 
                                tick_size, 
                                top, 
                                right, 
                                bottom, 
                                left, 
                                extra_pad = 0, 
                                n_draws = 50, 
                                x_upper = 50){
  
  xlab = paste0("$c_5$ ", labeltext)
  p <- ppc_dens_overlay(y, yrep[1:n_draws, ]) + 
    xlim(NA, x_upper) + 
    theme(legend.position = "none",
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size),
          plot.margin = margin(top, right, bottom, left, unit = "pt")) +
    labs(x = TeX(xlab))
  
  return(p)
  
}

plot_dens_overlay_free <- function(y, 
                                  yrep, 
                                  labeltext,
                                  label_size, 
                                  tick_size, 
                                  top, 
                                  right, 
                                  bottom, 
                                  left, 
                                  extra_pad = 0, 
                                  n_draws = 50){
  
  xlab = paste0("$c_5$ ", labeltext)
  p <- ppc_dens_overlay(y, yrep[1:n_draws, ]) + 
    theme(legend.position = "none",
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size),
          plot.margin = margin(top, right, bottom, left, unit = "pt")) +
    labs(x = TeX(xlab))
  
  return(p)
  
}


#' 
## -----------------------------------------------------------------------------

prior_dens <- plot_dens_overlay_limit(y = y,
                                    yrep = yrep_prior,
                                    labeltext = "(prior)",
                                    label_size = label,
                                    tick_size = tick,
                                    top = 5, 
                                    right = 15,
                                    bottom = 5,
                                    left = 15)


#' 
#' 
#' # posterior predictive checks
#' 
#' ## overall 
#' 
#' ### density 
#' 
#' 
## -----------------------------------------------------------------------------

post_dens1 <- plot_dens_overlay_limit(y, 
                                     yrep_post, 
                                     labeltext = "",
                                     label, 
                                     tick,
                                     top = 5,
                                     right = 15,
                                     bottom = 5,
                                     left = 15,
                                     extra_pad = -2)

post_dens2 <- plot_dens_overlay_free(y, 
                                     yrep_post, 
                                     labeltext = "",
                                     label, 
                                     tick,
                                     top = 5,
                                     right = 15,
                                     bottom = 5,
                                     left = 15,
                                     extra_pad = -2)


#' 
#' 
#' ### histogram 
#' 
## -----------------------------------------------------------------------------
plot_hist <- function(y, 
                      yrep, 
                      label_size, 
                      tick_size, 
                      top, 
                      right, 
                      bottom, 
                      left, 
                      extra_pad, 
                      n_draws = 5,
                      x_upper = 50){
  
  p <- ppc_hist(y, yrep[1:n_draws, ]) + 
    xlim(NA, x_upper) + 
    theme(legend.position = "none",
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size),
          plot.margin = margin(top, right, bottom, left, unit = "pt")) +
    labs(x = TeX("$c_5$"))
  
  return(p)
}


#' 
## -----------------------------------------------------------------------------

post_hist <- plot_hist(y, 
                     yrep_post, 
                     label, 
                     tick,
                     top = 5,
                     right = 15,
                     bottom = 5,
                     left = 15,
                     extra_pad = -2)


#' 
#' ### prob = 0, prob = max, prob = mean, prob = median
#' 
## -----------------------------------------------------------------------------

plot_stat <- function(stat,
                      binwidth,
                      y, 
                      yrep, 
                      labeltext,
                      label_size, 
                      tick_size, 
                      top, 
                      right, 
                      bottom, 
                      left, 
                      extra_pad, 
                      n_draws = 50){
  
  #xlab = paste0("$c_5$ ", labeltext)
  p <- ppc_stat(y, yrep, stat = stat, binwidth = binwidth) + 
    theme(legend.position = "none",
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size),
          plot.margin = margin(top, right, bottom, left, unit = "pt")) +
    labs(x = TeX(labeltext))
  
  return(p)
}


#' 
## -----------------------------------------------------------------------------

prop_zero <- function(x) mean(x == 0)


#' 
## -----------------------------------------------------------------------------

post_0 <- plot_stat(stat = "prop_zero",
                    binwidth = 0.005,
                    y = y,
                    yrep = yrep_post,
                    labeltext = "$c_5 = 0$ frequency",
                    label, 
                    tick,
                    top = 5,
                    right = 15,
                    bottom = 5,
                    left = 15,
                    extra_pad = -2)


#' 
#' 
## -----------------------------------------------------------------------------
post_max <- plot_stat(stat = "max",
                      binwidth = 100,
                      y = y,
                      yrep = yrep_post,
                      labeltext = "$c_5$ max",
                      label, 
                      tick,
                      top = 5,
                      right = 15,
                      bottom = 5,
                      left = 15,
                      extra_pad = -2)

#' 
#' 
## -----------------------------------------------------------------------------

post_mean = plot_stat(stat = "mean",
                      binwidth = 0.5,
                      y = y,
                      yrep = yrep_post,
                      labeltext = "$c_5$ mean",
                      label, 
                      tick,
                      top = 5,
                      right = 15,
                      bottom = 5,
                      left = 15,
                      extra_pad = -2)


#' 
#' 
## -----------------------------------------------------------------------------

post_median = plot_stat(stat = "median",
                        binwidth = 1,
                        y = y,
                        yrep = yrep_post,
                        labeltext = "$c_5$ median",
                        label, 
                        tick,
                        top = 5,
                        right = 15,
                        bottom = 5,
                        left = 15,
                        extra_pad = -2)


#' 
#' # arrange plot 
#' 
## -----------------------------------------------------------------------------

p_grid <- plot_grid(prior_dens,
                    #post_hist,
                    #post_dens2,
                    post_dens1,
                    post_mean,
                    post_median,
                    post_0,
                    post_max,
                    ncol = 2,
                    nrow = 3,
                    labels = c("A", "B", "C", "D", "E", "F"))


#' 
#' # save figure
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "pp_ungrouped.pdf"),
       plot = p_grid,
       height = 7, # changed
       width = 8)


#' 
#' 
#' ## grouped 
#' 
#' ### density 
#' looks reasonable for both groups 
#' --> does not work yet! 
#' 
## -----------------------------------------------------------------------------

plot_dens_overlay_grouped <- function(y, 
                                yrep, 
                                labeltext,
                                label_size, 
                                tick_size, 
                                n_draws = 50, 
                                x_upper = 50){
  
  xlab = paste0("$c_5$ ", labeltext)
  p <- ppc_dens_overlay_grouped(y, yrep_post[1:n_draws, ], group = d$condition_fct) + 
    xlim(NA, x_upper) + 
    theme(legend.position = "none",
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size),
          panel.spacing = unit(20, "pt"),
          plot.margin = margin(0, 15, 0, 15, unit = "pt"),
          strip.background = element_blank()) +
    facet_text(size = label_size) + 
    labs(x = TeX(xlab))
  
  return(p)
  
}

#' 
#' 
## -----------------------------------------------------------------------------

p_dens_grouped <- plot_dens_overlay_grouped(y, 
                                           yrep_post, 
                                           labeltext = "",
                                           label, 
                                           tick)


#' 
#' 
## -----------------------------------------------------------------------------

#' 
#' 
#' ### histogram
#' shows that we are actually pretty cautious, i.e. both are regularized towards each other.
#' predicts too low for control (dragging it up) and too high for experiment (dragging it down). 
#' 
## -----------------------------------------------------------------------------

plot_stat_grouped <- function(stat,
                              binwidth,
                              y, 
                              yrep, 
                              labeltext,
                              label_size, 
                              tick_size){
  
  xlab = paste0("$c_5$ ", labeltext)
  p <- ppc_stat_grouped(y, yrep_post, group = d$condition_fct, stat = stat, binwidth = binwidth) + 
    theme(legend.position = "none",
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size),
          panel.spacing = unit(20, "pt"),
          plot.margin = margin(0, 15, 0, 15, unit = "pt"),
          strip.background = element_blank()) +
    facet_text(size = label_size) + 
    labs(x = TeX(xlab))
  
  return(p)
}

#' 
#' 
## -----------------------------------------------------------------------------

p_hist_grouped <- plot_stat_grouped(stat = "mean",
                                    binwidth = 1,
                                    y = y,
                                    yrep = yrep_post,
                                    labeltext = "mean",
                                    label, 
                                    tick)



#' 
## -----------------------------------------------------------------------------
p_grid <- plot_grid(p_dens_grouped,
                    p_hist_grouped,
                    ncol = 1,
                    labels = c("A", "B"))

#' 
## -----------------------------------------------------------------------------
p_grid

#' 
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "pp_grouped.pdf"),
       plot = p_grid,
       height = 6,
       width = 8)


#' 
