#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Explore Priors"
#' author: "Victor M. Poulsen" 
#' output: html_document
#' ---
#' 
#' # Path setup
#' 
## ----setup, include=FALSE-----------------------------------------------------

#outpath <- "/work/50114/MAG/fig/modeling/replication_fos/explore_priors/"
outpath = args[1]

#' 
## ---- include=FALSE-----------------------------------------------------------

r = getOption("repos")
r["CRAN"] = "http://cran.r-project.org"
options(repos = r)

# consider pacman
if (!require("pacman")){
  print("-- installing pacman --")
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
               ggpubr,
               extraDistr)

# set up cmdstanr if it is not already present
if (!require('cmdstanr')){
  print("-- installing cmdstanr --")
  install.packages("cmdstanr", repos = c("https://mc-stan.org/r-packages/", getOption("repos")))
  library(cmdstanr)
  install_cmdstan(cores = 2, overwrite = TRUE)
}


#' 
#' # Visual setup
#' 
## -----------------------------------------------------------------------------

color_map <- c("Prior" = '#fee6ce', 
               "Posterior (control)" = '#fdae6b', 
               "Posterior (experiment)" = '#e6550d')

color_lst <- c('#fee6ce', '#fdae6b', '#e6550d')

theme_set(theme_classic())
title = 18
label = 14
tick = 12 # same as legend


#' 
#' # Shape/Phi parameter
#' 
#' ## plot gamma: 
#' * For gamma() it is shape and rate (not scale I think). 
#' --> first argument is shape. 
#' --> second argument is rate: https://bookdown.org/content/4857/monsters-and-mixtures.html
#' 
#' 
## -----------------------------------------------------------------------------

plot_gamma <- function(title_size, 
                       tick_size, 
                       label_size, 
                       shape = .01,
                       rate = .01,
                       n = 10000, 
                       from = 0, 
                       to = 10, 
                       by = .01){
  
  d <- tibble(x = rgamma(n, shape, rate)) %>% # rethinking::rgamma2(n, shape, scale)
    ggplot(aes(x = x)) +
    geom_ribbon(aes(ymin = 0,
                    ymax = dgamma(x, shape, rate)),
              fill = color_lst[2],
              alpha = 1) +
    stat_pointinterval(aes(y = 0), .width = c(.5, .95)) +
    labs(title = TeX("$\\gamma(.01, .01)$"), # Prior predictive distribution 
         x = TeX("Shape ($\\phi$)"),
         y = "") + 
    coord_cartesian(xlim = c(0, 10), ylim = (c(0, 1))) +
    theme(plot.title = element_text(size = title_size, hjust = 0.5),
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size)) 
  
  return(d)
}



#' 
#' ## plot gamma 
#' 
## -----------------------------------------------------------------------------

p_gamma <- plot_gamma(title_size = title,
                      tick_size = tick,
                      label_size = label)


#' 
#' ## plot exp:
#' * For exponential(rate) it is just rate. 
#' 
## -----------------------------------------------------------------------------

plot_exp <- function(rate, 
                     title_size, 
                     tick_size, 
                     label_size, 
                     n = 10000, 
                     from = 0, 
                     to = 10, 
                     by = .01){
  
  d <- tibble(x = rexp(n, rate)) %>%
    ggplot(aes(x = x)) +
    geom_ribbon(aes(ymin = 0,
                    ymax = dexp(x, rate = rate)),
              fill = color_lst[2],
              alpha = 1) +
    stat_pointinterval(aes(y = 0), .width = c(.5, .95)) +
    labs(title = TeX("$\\exp(0.5)$"), # Prior predictive distribution
         x = TeX("Shape ($\\phi$)"),
         y = "Density") + 
    coord_cartesian(xlim = c(0, 10), ylim = (c(0, 0.6))) +
    theme(plot.title = element_text(size = title_size, hjust = 0.5),
          legend.title = element_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = tick_size)) 
  
  return(d)
}


#' 
## -----------------------------------------------------------------------------

p_exp <- plot_exp(rate = 0.5, 
                  title_size = title, 
                  tick_size = tick,
                  label_size = label)



#' 
#' # gamma-Poisson:
#' * NB(mu, shape/phi): or Gamma-Poisson(mu, shape) #https://bookdown.org/content/4857/monsters-and-mixtures.html
#' ** we infer mu from the data (through linear model).
#' ** we infer shape (phi) from the data (through exponential prior).
#' 
#' As such, we do not place priors directly on these parameters, but we can visualize how the shape 
#' parameter affects the distribution through running various values through. 
#' 
#' ** shape/phi: we get from the gamma (or now exponential) prior.
#' ** mu: we get from our log-likelihood (positive rate?). 
#' 
#' * The NB(mu, phi): 
#' --> shape is Poisson rate?
#' --> phi/shape is the gamma prior. (which we show below)
#' 
#' 
#' ## Maybe it should be gamma, as in: https://bookdown.org/content/4857/monsters-and-mixtures.html
#' 
#' ## using dgpois
#' 
#' ### specify exact values (rely on intercept = 10 as that is our prior mean for intercept for each group)
#' ### NB: could sample from our prior (Exp(0.5)) instead actually. 
#' 
## -----------------------------------------------------------------------------

### gamma-poisson function ###
plot_dgpois <- function(title_size, 
                        tick_size, 
                        label_size, 
                        shape,
                        intercept){
  
  d <- expand.grid(x = seq(from = 0, to = 50, by = 1),
                   shape = shape) %>%
    mutate(theta = intercept/shape,
           density = dgpois(x, shape = shape, scale = theta)) %>%
  
    ggplot(aes(x = x, y = density, color = as.factor(shape))) + 
    geom_line(size = 2) + 
    labs(title = "Gamma-Poisson", # Prior predictive distribution 
         x = TeX("$c_5$"), # given by exp(\\mu) 
         y = "Frequency") + 
    coord_cartesian(xlim = c(0, 50), ylim = (c(0, 0.25))) +
    theme(plot.title = element_text(size = title_size, hjust = 0.5),
          legend.title = element_text(size = label_size), #lement_blank(),
          axis.text = element_text(size = tick_size),
          axis.title = element_text(size = label_size),
          legend.text = element_text(size = label_size),
          legend.position = c(0.87, 0.87)) +
    scale_color_manual(values = color_lst,
                       name = TeX("Shape ($\\phi$)"))
  
  return(d)
}



#' 
#' 
## -----------------------------------------------------------------------------

p_gpois <- plot_dgpois(title_size = title,
                       tick_size = tick,
                       label_size = label,
                       shape =  c(0.5, 1, 3),
                       intercept = 10)


#' 
#' ## gather plot (exp, gamma-pois)
#' 
## -----------------------------------------------------------------------------

p_grid <- plot_grid(p_exp,
                    p_gpois,
                    ncol = 2,
                    labels = c("A", "B"))



#' 
#' ## save plot
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, "gamma_poisson.pdf"),
       plot = p_grid,
       height = 4,
       width = 8)


#' 
#' 
#' ## gather plot (exp, gamma)
#' 
## -----------------------------------------------------------------------------

p_grid <- plot_grid(p_exp,
                    p_gamma,
                    ncol = 2,
                    labels = c("A", "B"))


#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, "gamma_exp.pdf"),
       plot = p_grid,
       height = 4,
       width = 8)


#' 
