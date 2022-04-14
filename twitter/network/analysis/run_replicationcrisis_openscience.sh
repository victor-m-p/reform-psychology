#!/user/bin/env bash

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# PLOT DOUBLE 
python /work/50114/twitter/network/analysis/network_cnsome.py \
    -i /work/50114/twitter/data/network/preprocessed \
    -o /work/50114/twitter/fig/network/combined \
    -q1 replicationcrisis \
    -q2 openscience \
    -c 200 \
    -n 50 \
    -g "True"
