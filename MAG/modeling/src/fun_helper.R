# main function for fitting models & adding criterion

fit_model <- function(d, family, formula, prior, sample_prior, file, random_seed = 13){ 
  
  m <- brm(data = d, 
           family = family, 
           formula = formula,
           prior = prior, 
           sample_prior = sample_prior,
           cores = 6,
           chains = 4,
           iter = 4000, 
           warmup = 2000,
           file = file,
           save_pars = save_pars(all = TRUE),
           file_refit = "on_change",
           threads = threading(2),
           seed = random_seed,
           control = list(adapt_delta = .99, 
                          max_treedepth = 20), 
           backend = "cmdstanr")
  
  if (sample_prior == TRUE){
    
    m <- add_criterion(m, 
                       c("loo", "waic", "bayes_R2"),
                       file = file,
                       force_save = TRUE)
  }
  
  return(m)
  
}
