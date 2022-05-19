#!/user/bin/env bash

### NB: NEW DOCUMENT FOR THIS !! ##

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# plot overlap (with labels for reference)
python /work/50114/twitter/nlp/network_viz/network_main.py \
    -i /work/50114/twitter/data/nlp/backboning \
    -o /work/50114/twitter/fig/nlp/network \
    -q1 "openscience" \
    -q2 "replicationcrisis" \
    -m "df" \
    -t 0.995 \
    -n 50 \
    -g "True"

# plot overlap (without labels for showing)
python /work/50114/twitter/nlp/network_viz/network_main.py \
    -i /work/50114/twitter/data/nlp/backboning \
    -o /work/50114/twitter/fig/nlp/network \
    -q1 "openscience" \
    -q2 "replicationcrisis" \
    -m "df" \
    -t 0.995 \
    -n 0 \
    -g "True"
