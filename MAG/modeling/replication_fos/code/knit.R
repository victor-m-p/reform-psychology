# knit .Rmd to .R to run whole pipeline from .sh script.
library(knitr)
purl("testcommandline.Rmd", output = "testcommandline.R", documentation = 2) # tmp
purl("main_model.Rmd", output = "main_model.R", documentation = 2)
purl("prior_sensitivity.Rmd", output = "prior_sensitivity.R", documentation = 2)
purl("updating_checks.Rmd", output = "updating_checks.R", documentation = 2)
purl("likelihood_comparison.Rmd", output = "likelihood_comparison.R", documentation = 2)