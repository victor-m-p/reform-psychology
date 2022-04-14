#!/user/bin/env bash

# venv
#sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source ../../$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run tweet preprocessing for networks  
python /work/50114/twitter/network/preprocessing/author_attributes.py \
	-i /work/50114/twitter/data/raw/preprocessed/$1 \
	-o /work/50114/twitter/data/network/preprocessed/

# run user preprocessing for networks 
python /work/50114/twitter/network/preprocessing/create_edgelist_simple.py \
	-i /work/50114/twitter/data/raw/preprocessed/$1 \
	-o /work/50114/twitter/data/network/preprocessed/
