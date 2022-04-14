#!/user/bin/env bash

#sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# RUN SIMPLE
python /work/50114/twitter/network/analysis/network_simple.py \
    -i /work/50114/twitter/data/network/preprocessed \
    -o /work/50114/twitter/fig/network/simple \
    -q $1 \
    -c 1 \
    -n 40
