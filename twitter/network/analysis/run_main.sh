#!/user/bin/env bash

### NB: NEW DOCUMENT FOR THIS !! ##

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# plot combined (disparity filter)
python /work/50114/twitter/network/analysis/network_main.py \
    -i /work/50114/twitter/data/network/backboning \
    -o /work/50114/twitter/fig/network/combined \
    -q1 $1 \
    -q2 $2 \
    -m "df" \
    -t 0.99 \
    -n 30 \
    -g "True"
