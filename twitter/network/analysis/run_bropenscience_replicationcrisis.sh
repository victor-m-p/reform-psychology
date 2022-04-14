#!/user/bin/env bash

# vars

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# PLOT DOUBLE 
python /work/50114/twitter/network/analysis/network_cnsome.py \
    -i /work/50114/twitter/data/network/preprocessed \
    -o /work/50114/twitter/fig/network/combined \
    -q1 bropenscience \
    -q2 replicationcrisis \
    -c 5 \
    -n 20 \
    -g "True"

