#!/user/bin/env bash
#Rscript knit.R

replication_fos=true
reproducibility_fos=true
replication_keyword=true

if [ $replication_fos = true ]
then
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
		"/work/50114/MAG/fig/modeling/replication_fos/prior_sensitivity/"

	# run likelihood_comparison.R
	echo "-- running likelihood_comparison.R (replication_fos) --"
	Rscript --vanilla likelihood_comparison.R \
		"psychology_replication_matched.csv" \
		"/work/50114/MAG/modeling/models/replication_fos/likelihood_comparison/" \
		"/work/50114/MAG/fig/modeling/replication_fos/likelihood_comparison/"

	# run updating_checks.R
	echo "-- running updating_checks.R (replication_fos) --"
	Rscript --vanilla updating_checks.R \
		"/work/50114/MAG/modeling/models/replication_fos/main_model/" \
		"/work/50114/MAG/fig/modeling/replication_fos/updating_checks/"
fi



if [ $reproducibility_fos = true ]
then
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
		"/work/50114/MAG/fig/modeling/reproducibility_fos/prior_sensitivity/"

	# run likelihood_comparison.R
	echo "-- running likelihood_comparison.R (reproducibility_fos) --"
	Rscript --vanilla likelihood_comparison.R \
		"psychology_reproducibility_matched.csv" \
		"/work/50114/MAG/modeling/models/reproducibility_fos/likelihood_comparison/" \
		"/work/50114/MAG/fig/modeling/reproducibility_fos/likelihood_comparison/"

	# run updating_checks.R
	echo "-- running updating_checks.R (reproducibility_fos) --"
	Rscript --vanilla updating_checks.R \
		"/work/50114/MAG/modeling/models/reproducibility_fos/main_model/" \
		"/work/50114/MAG/fig/modeling/reproducibility_fos/updating_checks/"
fi

if [ $replication_keyword = true ]
then
	# run main_model.R
	echo "-- running main_model.R (replication_keyword) --"
	Rscript --vanilla main_model.R \
		"psychology_replicat_matched.csv" \
		"/work/50114/MAG/modeling/models/replicat_fos/main_model/"

	# run prior_sensitivity.R
	echo "-- running prior_sensitivity.R (replication_keyword) --"
	Rscript --vanilla prior_sensitivity.R \
		"psychology_replicat_matched.csv" \
		"/work/50114/MAG/modeling/models/replicat_fos/prior_sensitivity/m_post_" \
		"/work/50114/MAG/fig/modeling/replicat_fos/prior_sensitivity/"

	# run likelihood_comparison.R
	echo "-- running likelihood_comparison.R (replication_keyword) --"
	Rscript --vanilla likelihood_comparison.R \
		"psychology_replicat_matched.csv" \
		"/work/50114/MAG/modeling/models/replicat_fos/likelihood_comparison/" \
		"/work/50114/MAG/fig/modeling/replicat_fos/likelihood_comparison/"

	# run updating_checks.R
	echo "-- running updating_checks.R (replication_keyword) --"
	Rscript --vanilla updating_checks.R \
		"/work/50114/MAG/modeling/models/replicat_fos/main_model/" \
		"/work/50114/MAG/fig/modeling/replicat_fos/updating_checks/"
fi


