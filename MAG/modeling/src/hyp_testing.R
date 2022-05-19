#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Hypothesis Testing"
#' author: "Victor M. Poulsen" 
#' output: html_document
#' ---
#' 
## ----setup, include=FALSE-----------------------------------------------------

## inpath_post <- "/work/50114/MAG/modeling/models/replication_fos/main_model/m_post.rds"
## outpath <- "/work/50114/MAG/fig/modeling/replication_fos/hyp_testing/"
inpath_post <- args[1]
outpath <- args[2]
tag <- args[3]

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


#' 
#' # Load model
#' 
## -----------------------------------------------------------------------------

m_post <- readRDS(paste0(inpath_post))


#' 
#' # Hypothesis testing: model scales 
#' 
## -----------------------------------------------------------------------------

# main effect
h_intercept <- hypothesis(m_post, 
                          "condition_fctexperiment < condition_fctcontrol",
                          alpha = 0.05) 

# log(teamsize) interaction
h_teamsize <- hypothesis(m_post, 
                         "condition_fctexperiment:log_teamsize < condition_fctcontrol:log_teamsize",
                         alpha = 0.05)

# year after 2005 interaction
h_year <- hypothesis(m_post, 
                     "condition_fctexperiment:year_after_2005 > condition_fctcontrol:year_after_2005",
                     alpha = 0.05)


#' 
#' ## plot hypothesis testing: 
#' 
## -----------------------------------------------------------------------------
plot_hypothesis <- function(h, title, tick_size, label_size, xlab, annotate_size, x_lower, x_upper, legend_pos = "none"){
  
  # extract information
  estimate <- h$hypothesis$Estimate
  lower <- h$hypothesis$CI.Lower
  upper <- h$hypothesis$CI.Upper
  
  # generate plot (list)
  p_lst <- plot(h)
  
  # unlist
  p <- p_lst[[1]]
  
  # ggplot
  p <- p + 
    theme(legend.position = legend_pos,
          plot.title = element_text(hjust = 0.5, size = label),
          legend.title = element_blank(),
          axis.text = element_text(size = tick),
          axis.title = element_text(size = label),
          legend.text = element_text(size = tick),
          strip.background = element_blank(),
          strip.text = element_blank()) +
    annotate("pointrange", x = estimate, y = 0, xmin = lower, xmax = upper, size = annotate_size) + 
    labs(title = title, x = TeX(xlab)) +
    xlim(x_lower, x_upper)
  
  return(p)
}


#' 
#' ### plot intercept 
#' 
## -----------------------------------------------------------------------------

p_intercept <- plot_hypothesis(h = h_intercept,
                               title = "",
                               tick_size = tick,
                               label_size = label,
                               xlab = 'Intercept ($\\mu$)',
                               annotate_size = 1,
                               x_lower = -2,
                               x_upper = 2,
                               legend_pos = "none")


#' 
#' ### plot teamsize 
#' 
## -----------------------------------------------------------------------------

p_teamsize <- plot_hypothesis(h = h_teamsize,
                              title = "",
                              tick_size = tick,
                              label_size = label,
                              xlab = 'log(TEAMSIZE) ($\\mu$)',
                              annotate_size = 1,
                              x_lower = -2,
                              x_upper = 2,
                              legend_pos = "none")


#' 
#' ### plot year
#' 
## -----------------------------------------------------------------------------

p_year <- plot_hypothesis(h = h_year, 
                          title = "",
                          tick_size = tick,
                          label_size = label,
                          xlab = 'YEAR ($\\mu$)',
                          annotate_size = 1 - 0.2,
                          x_lower = -2,
                          x_upper = 2,
                          legend_pos = "bottom")


#' 
#' ### gather in grid 
#' 
## -----------------------------------------------------------------------------

p_grid <- ggarrange(p_intercept, 
                    p_teamsize, 
                    p_year, 
                    ncol = 1, 
                    common.legend = TRUE, 
                    legend = 'bottom',
                    labels = c("A", "B", "C"))


#' 
## -----------------------------------------------------------------------------


#' 
#' 
#' ### save file 
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "hyp.pdf"),
       plot = p_grid,
       width = 8,
       height = 7.5)


#' 
#' ## effects saved as csv
#' 
## -----------------------------------------------------------------------------

hypothesis2df <- function(h){
  
  d <- as.data.frame(h$hypothesis) %>% select(Hypothesis, 
                                              Estimate, 
                                              Est.Error,
                                              CI.Lower, 
                                              CI.Upper, 
                                              Evid.Ratio,
                                              Post.Prob,
                                              Star)
  
  return(d)
  
}


#' 
#' ## save csv
#' 
## -----------------------------------------------------------------------------

d_intercept <- hypothesis2df(h_intercept)
d_teamsize <- hypothesis2df(h_teamsize)
d_year <- hypothesis2df(h_year)
d_summary <- bind_rows(d_intercept, d_teamsize, d_year)
write_csv(d_summary, paste0(outpath, tag, "hyp.csv"))


#' 
#' 
#' 
#' # Hypothesis testing: outcome scale
#' 
#' ## run hypotheses
#' 
## -----------------------------------------------------------------------------

# main effect
h_intercept_outcome <- hypothesis(m_post, 
                          "exp(condition_fctexperiment) < exp(condition_fctcontrol)",
                          alpha = 0.05) 

# log(teamsize) interaction
h_teamsize_outcome <- hypothesis(m_post, 
                         "exp(condition_fctexperiment:log_teamsize) < exp(condition_fctcontrol:log_teamsize)",
                         alpha = 0.05)

# year after 2005 interaction
h_year_outcome <- hypothesis(m_post, 
                     "exp(condition_fctexperiment:year_after_2005) > exp(condition_fctcontrol:year_after_2005)",
                     alpha = 0.05)


#' 
#' ### plot intercept
#' 
## -----------------------------------------------------------------------------

p_intercept_outcome <- plot_hypothesis(h = h_intercept_outcome,
                                       title = "",
                                       tick_size = tick,
                                       label_size = label,
                                       xlab = 'Intercept ($\\mu$)',
                                       annotate_size = 0.8,
                                       x_lower = -25,
                                       x_upper = 25,
                                       legend_pos = "none")


#' 
#' ### plot team size 
#' 
## -----------------------------------------------------------------------------

p_teamsize_outcome <- plot_hypothesis(h = h_teamsize_outcome,
                                      title = "",
                                      tick_size = tick,
                                      label_size = label,
                                      xlab = 'log(TEAMSIZE) ($\\mu$)',
                                      annotate_size = 0.8,
                                      x_lower = -5,
                                      x_upper = 5,
                                      legend_pos = "none")


#' 
#' ### plot year
#' 
## -----------------------------------------------------------------------------

p_year_outcome <- plot_hypothesis(h = h_year_outcome, 
                                  title = "",
                                  tick_size = tick,
                                  label_size = label,
                                  xlab = 'YEAR ($\\mu$)',
                                  annotate_size = 0.8 - 0.2,
                                  x_lower = -2,
                                  x_upper = 2,
                                  legend_pos = "bottom")


#' 
#' ### arrange in grid
#' 
## -----------------------------------------------------------------------------

p_grid_outcome <- ggarrange(p_intercept_outcome, 
                            p_teamsize_outcome, 
                            p_year_outcome, 
                            ncol = 1, 
                            common.legend = TRUE, 
                            legend = 'bottom',
                            labels = c("A", "B", "C"))


#' 
#' ### save plot
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath, tag, "hyp_outcome.pdf"),
       plot = p_grid_outcome,
       width = 8,
       height = 7.5)


#' 
#' ## gather csv
#' 
## -----------------------------------------------------------------------------

d_intercept_outcome <- hypothesis2df(h_intercept_outcome)
d_teamsize_outcome <- hypothesis2df(h_teamsize_outcome)
d_year_outcome <- hypothesis2df(h_year_outcome)
d_summary_outcome <- bind_rows(d_intercept_outcome, d_teamsize_outcome, d_year_outcome)
write_csv(d_summary_outcome, paste0(outpath, tag, "hyp_outcome.csv"))


#' 
#' 
#' # --- specific hypotheses ---
#' 
## -----------------------------------------------------------------------------

#scaling = log(2) - log(1)
#scaling


#' 
## -----------------------------------------------------------------------------

#h_teamsize_outcome <- hypothesis(
#  m_post, 
#  "exp(condition_fctexperiment:log_teamsize * 0.693) < exp(condition_fctcontrol:log_teamsize * 0.693)",
#  alpha = 0.5)
#plot(h_teamsize_outcome)


#' 
