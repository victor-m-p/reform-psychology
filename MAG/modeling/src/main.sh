#!/user/bin/env bash

## logging
touch "log$(date +"%Y_%m_%d_%I_%M").out"
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1> "log$(date +"%Y_%m_%d_%I_%M").out" 2>&1

## set variables
explore_priors=true
replication_fos=true
reproducibility_fos=true
replication_keyword=true

## explore priors 
if [ $explore_priors = true ]
  then
	# run explore_priors.R
	echo "-- running explore_priors.R --"
	Rscript --vanilla explore_priors.R \
		"/work/50114/MAG/fig/modeling/replication_fos/explore_priors/" 
fi 

## replication fos 
if [ $replication_fos = true ]
then
  echo "-- REPLICATION_FOS --"
	# run main_model.R
	echo "-- running main_model.R (replication_fos) --"
	Rscript --vanilla main_model.R \
		"psychology_replication_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_fos/main_model/"

	# run prior_sensitivity.R
	echo "-- running prior_sensitivity.R (replication_fos) --"
	Rscript --vanilla prior_sensitivity.R \
		"psychology_replication_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_fos/prior_sensitivity/m_post_" \
		"/work/50114/MAG/fig/modeling/replication_fos/prior_sensitivity/" \
		"replication_"

	# run likelihood_comparison.R
	echo "-- running likelihood_comparison.R (replication_fos) --"
	Rscript --vanilla likelihood_comparison.R \
		"psychology_replication_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_fos/likelihood_comparison/" \
		"/work/50114/MAG/fig/modeling/replication_fos/likelihood_comparison/" \
		"replication_"

	# run updating_checks.R
	echo "-- running updating_checks.R (replication_fos) --"
	Rscript --vanilla updating_checks.R \
		"/work/50114/MAG/modeling/models/replication_fos/main_model/" \
		"/work/50114/MAG/fig/modeling/replication_fos/updating_checks/" \
		"replication_"
		
	# run pp_checks.R
	echo "-- running pp_checks.R (replication_fos) --"
	Rscript --vanilla pp_checks.R \
	  "psychology_replication_matched.csv" \
	  "/work/50114/MAG/fig/modeling/replication_fos/pp_checks/" \
	  "/work/50114/MAG/modeling/models/replication_fos/main_model/" \
	  "replication_"
	  
  echo "-- running hyp_testing.R (replication_fos) --"
  Rscript --vanilla hyp_testing.R \
    "/work/50114/MAG/modeling/models/replication_fos/main_model/m_post.rds" \
    "/work/50114/MAG/fig/modeling/replication_fos/hyp_testing/" \
    "replication_"
    
  echo "-- running simulate_predict.R (replication_fos) -- " 
  Rscript --vanilla simulate_predict.R \
    "psychology_replication_matched.csv" \
    "/work/50114/MAG/modeling/models/replication_fos/main_model/m_post.rds" \
    "/work/50114/MAG/fig/modeling/replication_fos/simulate_predict/" \
    "replication_"
fi


## reproducibility_fos
if [ $reproducibility_fos = true ]
then
  echo "-- REPRODUCIBILITY_FOS --"
	# run main_model.R
	echo "-- running main_model.R (reproducibility_fos) --"
	Rscript --vanilla main_model.R \
		"psychology_reproducibility_matched.csv" \
		"/work/50114/MAG/modeling/models/reproducibility_fos/main_model/"

	# run prior_sensitivity.R
	echo "-- running prior_sensitivity.R (reproducibility_fos) --"
	Rscript --vanilla prior_sensitivity.R \
		"psychology_reproducibility_matched.csv" \
		"/work/50114/MAG/modeling/models/reproducibility_fos/prior_sensitivity/m_post_" \
		"/work/50114/MAG/fig/modeling/reproducibility_fos/prior_sensitivity/" \
		"reproducibility_"

	# run likelihood_comparison.R
	echo "-- running likelihood_comparison.R (reproducibility_fos) --"
	Rscript --vanilla likelihood_comparison.R \
		"psychology_reproducibility_matched.csv" \
		"/work/50114/MAG/modeling/models/reproducibility_fos/likelihood_comparison/" \
		"/work/50114/MAG/fig/modeling/reproducibility_fos/likelihood_comparison/" \
		"reproducibility_"

	# run updating_checks.R
	echo "-- running updating_checks.R (reproducibility_fos) --"
	Rscript --vanilla updating_checks.R \
		"/work/50114/MAG/modeling/models/reproducibility_fos/main_model/" \
		"/work/50114/MAG/fig/modeling/reproducibility_fos/updating_checks/" \
		"reproducibility_"
		
	# run pp_checks.R
	echo "-- running pp_checks.R (reproducibility_fos) --"
	Rscript --vanilla pp_checks.R \
	  "psychology_reproducibility_matched.csv" \
	  "/work/50114/MAG/fig/modeling/reproducibility_fos/pp_checks/" \
	  "/work/50114/MAG/modeling/models/reproducibility_fos/main_model/" \
	  "reproducibility_"
	  
  echo "-- running hyp_testing.R (reproducibility_fos) --"
  Rscript --vanilla hyp_testing.R \
    "/work/50114/MAG/modeling/models/reproducibility_fos/main_model/m_post.rds" \
    "/work/50114/MAG/fig/modeling/reproducibility_fos/hyp_testing/" \
    "reproducibility_"
  
  echo "-- running simulate_predict.R (reproducibility_fos) -- " 
  Rscript --vanilla simulate_predict.R \
    "psychology_reproducibility_matched.csv" \
    "/work/50114/MAG/modeling/models/reproducibility_fos/main_model/m_post.rds" \
    "/work/50114/MAG/fig/modeling/reproducibility_fos/simulate_predict/" \
    "reproducibility_"
fi

## reproducibility_keyword
if [ $replication_keyword = true ]
then
  echo "-- REPLICATION_KEYWORD --"
	# run main_model.R
	echo "-- running main_model.R (replication_keyword) --"
	Rscript --vanilla main_model.R \
		"psychology_replicat_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_keyword/main_model/"

	# run prior_sensitivity.R
	echo "-- running prior_sensitivity.R (replication_keyword) --"
	Rscript --vanilla prior_sensitivity.R \
		"psychology_replicat_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_keyword/prior_sensitivity/m_post_" \
		"/work/50114/MAG/fig/modeling/replication_keyword/prior_sensitivity/" \
		"replicat_"

	# run likelihood_comparison.R
	echo "-- running likelihood_comparison.R (replication_keyword) --"
	Rscript --vanilla likelihood_comparison.R \
		"psychology_replicat_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_keyword/likelihood_comparison/" \
		"/work/50114/MAG/fig/modeling/replication_keyword/likelihood_comparison/" \
		"replicat_"

	# run updating_checks.R
	echo "-- running updating_checks.R (replication_keyword) --"
	Rscript --vanilla updating_checks.R \
		"/work/50114/MAG/modeling/models/replication_keyword/main_model/" \
		"/work/50114/MAG/fig/modeling/replication_keyword/updating_checks/" \
		"replicat_"
		
	# run pp_checks.R
	echo "-- running pp_checks.R (replication_keyword) --"
	Rscript --vanilla pp_checks.R \
	  "psychology_replicat_matched.csv" \
	  "/work/50114/MAG/fig/modeling/replication_keyword/pp_checks/" \
	  "/work/50114/MAG/modeling/models/replication_keyword/main_model/" \
	  "replicat_"
	  
  echo "-- running hyp_testing.R (replication_keyword) --"
  Rscript --vanilla hyp_testing.R \
    "/work/50114/MAG/modeling/models/replication_keyword/main_model/m_post.rds" \
    "/work/50114/MAG/fig/modeling/replication_keyword/hyp_testing/" \
    "replicat_"
  
  echo "-- running simulate_predict.R (replication_keyword) -- " 
  Rscript --vanilla simulate_predict.R \
    "psychology_replicat_matched.csv" \
    "/work/50114/MAG/modeling/models/replication_keyword/main_model/m_post.rds" \
    "/work/50114/MAG/fig/modeling/replication_keyword/simulate_predict/" \
    "replicat_"
fi

## ZIP 
sudo apt install zip unzip
cd /work/50114/MAG/fig/
zip -r "modeling/bayes_fig$(date +"%Y_%m_%d_%I_%M").zip" modeling/