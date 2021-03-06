#!/user/bin/env bash

## logging
touch "log$(date +"%Y_%m_%d_%I_%M").out"
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1> "log$(date +"%Y_%m_%d_%I_%M").out" 2>&1

## set variables
explore_priors=false
replication_fos=true
reproducibility_fos=false
replication_keyword=true


## replication fos 
if [ $replication_fos = true ]
then
  # putting it early ¨
  echo "--running replication matched"
  Rscript --vanilla results.R \
  "psychology_replication_matched.csv" \
  "/work/50114/MAG/modeling/models/replication_fos/main_model/m_post.rds" \
  "/work/50114/MAG/fig/modeling/replication_fos/simulate_predict/" \
  "replication_"
fi
  
if [ $replication_keyword = true ]
then

  # putting it early
  echo "-- running results.R (replication keyword) --"
  Rscript --vanilla results.R \
  "psychology_replicat_matched.csv" \
  "/work/50114/MAG/modeling/models/replication_keyword/main_model/m_post.rds" \
  "/work/50114/MAG/fig/modeling/replication_keyword/results/" \
  "replicat_"
fi