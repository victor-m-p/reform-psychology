#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

#' ---
#' title: "Prior Robustness"
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
outpath_fig <- args[3]
tag <- args[4]


#' 
#' # VMP 2022-03-11
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

setwd(wd_code)
source("fun_helper.R")


#' 
#' 
#' # read data and create some variables
#' ## (1) temsize log. 
#' ## (2) match group as id 
#' 
#' 
## -----------------------------------------------------------------------------

csv_path <- paste0(inpath, infile)

# check data
d <- read_csv(csv_path) %>%
  mutate(log_teamsize = log(n_authors), 
         condition_fct = as_factor(condition), 
         id_match = as_factor(match_group),
         id_dct = as_factor(PaperId),
         year_after_2005 = Year - 2005) %>% 
  glimpse()


#' 
#' # model formula 
#' 
## -----------------------------------------------------------------------------

f <- bf(c_5 ~ 0 + condition_fct + condition_fct:log_teamsize + condition_fct:year_after_2005 + (0 + condition_fct | id_match))


#' 
#' # get prior:
#' * b: effects.
#' * cor: correlation of random effecs I think
#' * sd: match and both conditions.
#' * shape: overdispersion parameter for negative binomial.
#' 
## -----------------------------------------------------------------------------

get_prior(
  formula = f,
  data = d, 
  family = negbinomial())


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
#' # initialize vars 
#' 
## -----------------------------------------------------------------------------

# initialize lists
int_ci_lower <- c()
int_ci_upper <- c()
int_ci_est <- c()
team_ci_lower <- c()
team_ci_upper <- c()
team_ci_est <- c()
year_ci_lower <- c()
year_ci_upper <- c()
year_ci_est <- c()

# set outpath 
outpath = '/work/50114/MAG/modeling/replication_fos/models/prior_sensitivity/m_post_' 

# prior sequence
priSD <- seq(0.1, 1.5, length.out = 15)


#' 
#' # run everything 
#' 
## -----------------------------------------------------------------------------

for (i in 1:length(priSD)){
  
  p[2,] <- set_prior(paste0("normal(log(10), ", priSD[i],")"), 
                     class = "b",
                     coef = "condition_fctcontrol")
  p[3,] <- set_prior(paste0("normal(log(10), ", priSD[i],")"), 
                     class = "b",
                     coef = "condition_fctexperiment")
  p[4,] <- set_prior(paste0("normal(0.5, ", priSD[i],")"),
                     class = "b",
                     coef = "condition_fctcontrol:log_teamsize")
  p[5,] <- set_prior(paste0("normal(0.5, ", priSD[i],")"),
                     class = "b",
                     coef = "condition_fctexperiment:log_teamsize")
  p[6,] <- set_prior(paste0("normal(0, ", priSD[i],")"),
                     class = "b",
                     coef = "condition_fctcontrol:year_after_2005")
  p[7,] <- set_prior(paste0("normal(0, ", priSD[i],")"),
                     class = "b",
                     coef = "condition_fctexperiment:year_after_2005")
  
  # get path / name for saving 
  model_name <- paste0(outpath_models, priSD[i]) 
  
  # fit model 
  m_post <- fit_model(
    d = d,
    family = negbinomial(), 
    formula = f, 
    prior = p,
    sample_prior = TRUE,
    file = model_name
  )
  
  # get difference through hypothesis
  h_intercept <- hypothesis(
    m_post, 
    "condition_fctexperiment < condition_fctcontrol", 
    alpha = 0.05)
  
  h_teamsize <- hypothesis(
    m_post, 
    "condition_fctexperiment:log_teamsize < condition_fctcontrol:log_teamsize",
    alpha = 0.05
  )
  
  h_year <- hypothesis(
    m_post, "condition_fctexperiment:year_after_2005 <
    condition_fctcontrol:year_after_2005",
    alpha = 0.05
  )
  
  
  # get out estimates & add to lists
  int_ci_lower[i] <- h_intercept$hypothesis$CI.Lower
  int_ci_upper[i] <- h_intercept$hypothesis$CI.Upper
  int_ci_est[i] <- h_intercept$hypothesis$Estimate
  team_ci_lower[i] <- h_teamsize$hypothesis$CI.Lower 
  team_ci_upper[i] <- h_teamsize$hypothesis$CI.Upper
  team_ci_est[i] <- h_teamsize$hypothesis$Estimate
  year_ci_lower[i] <- h_year$hypothesis$CI.Lower
  year_ci_upper[i] <- h_year$hypothesis$CI.Upper
  year_ci_est[i] <- h_year$hypothesis$Estimate

}


#' 
#' # plot results 
#' 
## -----------------------------------------------------------------------------

light_color = "#fe8a2f"
dark_color = "#7f3f0c"
theme_set(theme_classic())
# width = 8
# height = 4
title = 18
label = 14
tick = 12


#' 
#' 
#' ## intercept difference
#' 
#' 
## -----------------------------------------------------------------------------

# get data 
int_data <- tibble(priSD, int_ci_lower, int_ci_upper, int_ci_est) %>%
  mutate(condition = case_when(priSD == 0.5 ~ 'Prior (main model)', TRUE ~ 'Prior (sensitivity)'))

# get ylims
int_ylim <- int_data %>% 
  summarize(y_min = min(int_ci_lower),
            y_max = max(int_ci_upper)) %>%
  mutate(y_min = round(y_min, 1) - 0.1,
         y_max = round(y_max, 1) + 0.1) 

y_min <- int_ylim$y_min
y_max <- int_ylim$y_max

# plot 
p_intercept <- int_data %>% ggplot(aes(x = priSD, y = int_ci_est, color = condition)) + 
  geom_point(size = 3) + 
  geom_pointrange(ymin = int_ci_lower, ymax = int_ci_upper) + 
  ylim(y_min, y_max) +
  labs(x = "", 
       y = TeX("Group difference ($\\mu$)"), 
       title = "Intercept") + 
  scale_color_manual(
    breaks = c("Prior (main model)", "Prior (sensitivity)"),
    values = c(dark_color, light_color),
    guide = guide_legend(title = NULL)) +
  theme(plot.title = element_text(hjust = 0.5, size = title),
        axis.text = element_text(size = tick),
        axis.title = element_text(size = label),
        legend.position = "none")



#' 
#' ## teamsize interaction difference
#' 
## -----------------------------------------------------------------------------

# get data 
team_data <- tibble(priSD, team_ci_lower, team_ci_upper, team_ci_est) %>% 
  mutate(condition = case_when(priSD == 0.5 ~ 'Prior (main model)', TRUE ~ 'Prior (sensitivity)'))

# get ylims
team_ylim <- team_data %>% 
  summarize(y_min = min(team_ci_lower),
            y_max = max(team_ci_upper)) %>%
  mutate(y_min = round(y_min, 1) - 0.1,
         y_max = round(y_max, 1) + 0.1) 

y_min <- team_ylim$y_min
y_max <- team_ylim$y_max

# plot 
p_team <- team_data %>% ggplot(aes(x = priSD, y = team_ci_est, color = condition)) + 
  geom_point(size = 3) + 
  geom_pointrange(ymin = team_ci_lower, ymax = team_ci_upper) + 
  ylim(y_min, y_max) +
  labs(x = "", 
       y = "", #TeX("Group difference ($\\mu$)"), 
       title = "TEAMSIZE") + 
  theme(plot.title = element_text(hjust = 0.5, size = title),
        axis.text = element_text(size = tick),
        axis.title = element_text(size = label),
        legend.position = "none") + 
  scale_color_manual(
    breaks = c("Prior (main model)", "Prior (sensitivity)"),
    values = c(dark_color, light_color),
    guide = guide_legend(title = NULL))


#' 
#' ## year interaction difference
#' 
## -----------------------------------------------------------------------------

# get data
year_data <- tibble(priSD, year_ci_lower, year_ci_upper, year_ci_est) %>%
  mutate(condition = case_when(priSD == 0.5 ~ 'Prior (main model)', TRUE ~ 'Prior (sensitivity)'))

# get ylims
year_ylim <- team_data %>% 
  summarize(y_min = min(year_ci_lower),
            y_max = max(year_ci_upper)) %>%
  mutate(y_min = round(y_min, 1) - 0.1,
         y_max = round(y_max, 1) + 0.1) 

y_min <- year_ylim$y_min
y_max <- year_ylim$y_max

# plot 
p_year <- year_data %>% ggplot(aes(x = priSD, y = year_ci_est, color = condition)) + 
  geom_point(size = 3) + 
  geom_pointrange(ymin = year_ci_lower, ymax = year_ci_upper) + 
  ylim(y_min, y_max) +
  labs(x = "", # TeX("Prior standard deviation ($\\sigma$)"),
       y = "", #TeX("Group difference ($\\mu$)"), 
       title = "YEAR") + 
  theme(plot.title = element_text(hjust = 0.5, size = title),
        axis.text = element_text(size = tick),
        axis.title = element_text(size = label),
        #legend.text = element_text(size = tick),
        legend.position = "none") + 
    scale_color_manual(
      breaks = c("Prior (main model)", "Prior (sensitivity)"),
      values = c(dark_color, light_color),
      guide = guide_legend(title = NULL))


#' 
#' ## gather plot
#' 
## -----------------------------------------------------------------------------

p_grid <- ggarrange(p_intercept, 
                    p_team, 
                    p_year, 
                    ncol = 3,
                    labels = c("A", "B", "C")
                    )  
                    #common.legend = TRUE, 
                    #legend = "right") 


#' 
#' ## annotate 
#' 
## -----------------------------------------------------------------------------

p_annotate <- annotate_figure(p = p_grid, 
                              bottom = text_grob(TeX("Prior standard deviation ($\\sigma$)"), size = label, vjust = -0.5))


#' 
#' ## save plot
#' 
## -----------------------------------------------------------------------------

ggsave(filename = paste0(outpath_fig, tag, "c5_distribution.pdf"), 
       plot = p_annotate,
       width = 8,
       height = 3)


#' 
