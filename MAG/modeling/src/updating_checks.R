#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Updating Checks"
#' author: "Victor M. Poulsen" 
#' output: html_document
#' ---
#' 
#' # VMP 2022-03-24 (need to rerun): 
#' 
#' ## paths setup
#' 
#' 
## -----------------------------------------------------------------------------

wd_code = "/work/50114/MAG/modeling/src"
inpath <- args[1]
outpath <- args[2]
inpath_post <- paste0(inpath, "m_post.rds")
inpath_prior <- paste0(inpath, "m_prior.rds")


#' 
#' 
## ----setup, include=FALSE-----------------------------------------------------

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

setwd(wd_code)
source("fun_helper.R")


#' 
#' # visual setup 
#' 
## -----------------------------------------------------------------------------

## orange map 
# light: #fee6ce
# medium: #fdae6b
# dark: #e6550d

color_map <- c("Prior" = '#fee6ce', 
               "Posterior (control)" = '#fdae6b', 
               "Posterior (experiment)" = '#e6550d')

categories <- c("Prior", 
                "Posterior (control)", 
                "Posterior (experiment)")

color_map_sub <- c("Prior" = '#fee6ce', 
                   "Posterior (experiment)" = "#e6550d")

categories_sub <- c("Prior",
                    "Posterior (experiment)")

theme_set(theme_classic())
title = 18
label = 14
tick = 12 # same as legend


#' 
#' # load models
#' 
## -----------------------------------------------------------------------------

m_post <- readRDS(inpath_post)
m_prior <- readRDS(inpath_prior)


#' 
#' # plot update beta
#' 
## -----------------------------------------------------------------------------

plot_update_b <- function(m_post, 
                          m_prior, 
                          color_map, 
                          categories,
                          label_size,
                          tick_size){
  
  post_draws <- as_draws_df(m_post)
  prior_draws <- as_draws_df(m_prior)
  
  p_int <- prior_draws %>% ggplot() + 
    geom_density(aes(b_condition_fctexperiment, # same as prior for control
                 fill = categories[1]),
                 alpha = 1) +
    geom_density(aes(b_condition_fctcontrol,
                 fill = categories[2]),
                 alpha = 0.8,
                 data = post_draws) + 
    geom_density(aes(b_condition_fctexperiment,
                 fill = categories[3]),
                 alpha = 0.7,
                 data = post_draws) +
    labs(x = TeX("Intercept ($\\mu$)"),
         fill = "Legend") +
    scale_fill_manual(
      breaks = categories, 
      values = color_map,
      guide = guide_legend(title = NULL)) +
      theme(plot.title = element_text(hjust = 0.5),
            legend.title = element_blank(),
            axis.text = element_text(size = tick_size),
            axis.title = element_text(size = label_size),
            legend.text = element_text(size = tick_size)) 
  
  p_team <- prior_draws %>% ggplot() + 
    geom_density(aes(`b_condition_fctexperiment:log_teamsize`,
                 fill = categories[1]),
                 alpha = 1) +
    geom_density(aes(`b_condition_fctcontrol:log_teamsize`,
                 fill = categories[2]),
                 alpha = 0.8,
                 data = post_draws) +
    geom_density(aes(`b_condition_fctexperiment:log_teamsize`,
                 fill = categories[3]),
                 alpha = 0.7,
                 data = post_draws) +
    labs(x = TeX("log(Team Size) ($\\mu$)"),
         fill = "Legend") +
    scale_fill_manual(
      breaks = categories, 
      values = color_map,
      guide = guide_legend(title = NULL)) +
    theme(plot.title = element_text(hjust = 0.5),
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size)) 
  
  p_year <- prior_draws %>% ggplot() + 
    geom_density(aes(`b_condition_fctexperiment:year_after_2005`,
                 fill = categories[1]),
                 alpha = 1) + 
    geom_density(aes(`b_condition_fctcontrol:year_after_2005`,
                 fill = categories[2]),
                 alpha = 0.8,
                 data = post_draws) + 
    geom_density(aes(`b_condition_fctexperiment:year_after_2005`,
                 fill = categories[3]),
                 alpha = 0.7,
                 data = post_draws) +
    labs(x = TeX("Year ($\\mu$)")) +
    scale_fill_manual(
      breaks = categories,
      values = color_map,
      guide = guide_legend(title = NULL)) +
    theme(plot.title = element_text(hjust = 0.5),
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size)) 
    
  p_grid <- ggarrange(p_int, p_team, p_year, ncol = 3, common.legend = TRUE, legend = 'bottom')

  return(p_grid)
}


#' 
#' # generate grid
#' 
## -----------------------------------------------------------------------------

p_grid <- plot_update_b(m_post = m_post, 
                        m_prior = m_prior, 
                        color_map = color_map, 
                        categories = categories,
                        label_size = label,
                        tick_size = tick)


#' 
#' # save 
#' 
## -----------------------------------------------------------------------------

filename = "updating_b.pdf"
outname = paste0(outpath, filename)

ggsave(filename = outname, 
       plot = p_grid,
       height = 3,
       width = 8)


#' 
#' # updating other params 
#' Hard to make super smooth because it is a combination of family specific paramters (shape) which are not by group, and then one group-level effect that is not by group (cor) and one than is by group (sd). 
#' 
## -----------------------------------------------------------------------------

plot_update_other <- function(m_post, 
                              m_prior, 
                              color_map, 
                              categories,
                              color_map_sub,
                              categories_sub,
                              label_size,
                              tick_size){
  
  post_draws <- as_draws_df(m_post)
  prior_draws <- as_draws_df(m_prior)
  
  p_shape <- prior_draws %>% ggplot() + 
    geom_density(aes(shape, # same as prior for control
                 fill = categories[1]),
                 alpha = 0.6) +
    geom_density(aes(shape,
                 fill = categories[3]),
                 alpha = 0.6,
                 data = post_draws) + 
    labs(x = TeX("Phi ($\\phi$)")) +
    scale_fill_manual(
      breaks = categories_sub, 
      values = color_map_sub,
      guide = guide_legend(title = NULL)) +
      theme(plot.title = element_text(hjust = 0.5),
            legend.title = element_blank(),
            axis.text = element_text(size = tick_size),
            axis.title = element_text(size = label_size),
            legend.text = element_text(size = tick_size)) 
  
  p_cor <- prior_draws %>% ggplot() + 
    geom_density(aes(cor_id_match__condition_fctexperiment__condition_fctcontrol,
                 fill = categories[1]),
                 alpha = 0.6) +
    geom_density(aes(cor_id_match__condition_fctexperiment__condition_fctcontrol,
                 fill = categories[3]),
                 alpha = 0.6,
                 data = post_draws) +
    labs(x = "cor") +
    scale_fill_manual(
      breaks = categories_sub, 
      values = color_map_sub,
      guide = guide_legend(title = NULL)) +
    theme(plot.title = element_text(hjust = 0.5),
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size)) 
  
  p_sd <- prior_draws %>% ggplot() + 
    geom_density(aes(sd_id_match__condition_fctexperiment,
                 fill = categories[1]),
                 alpha = 0.6) + 
    geom_density(aes(sd_id_match__condition_fctcontrol,
                 fill = categories[2]),
                 alpha = 0.6,
                 data = post_draws) + 
    geom_density(aes(sd_id_match__condition_fctexperiment,
                 fill = categories[3]),
                 alpha = 0.6,
                 data = post_draws) +
    labs(x = "sd") +
    scale_fill_manual(
      breaks = categories,
      values = color_map,
      guide = guide_legend(title = NULL)) +
    theme(plot.title = element_text(hjust = 0.5),
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size)) 
    
  p_grid <- ggarrange(p_sd, p_cor, p_shape, ncol = 3, common.legend = TRUE, legend = 'bottom')

  return(p_grid)
}


#' 
## -----------------------------------------------------------------------------

p_grid <- plot_update_other(m_post = m_post,
                            m_prior = m_prior,
                            color_map = color_map,
                            categories = categories,
                            color_map_sub = color_map_sub,
                            categories_sub = categories_sub,
                            label_size = label,
                            tick_size = tick)


#' 
## -----------------------------------------------------------------------------

filename = "updating_family_group.pdf"
outname = paste0(outpath, filename)

ggsave(filename = outname, 
       plot = p_grid,
       height = 3,
       width = 8)


#' 
#' 
