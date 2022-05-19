#!/user/bin/env bash

# venv
#sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source ../../$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run user preprocessing for networks 
python /work/50114/twitter/network/preprocessing/create_edgelist_intersection.py \
	-i /work/50114/twitter/data/nlp/subsets/os_rc_5.pickle \
	-o /work/50114/twitter/data/network/preprocessed/
