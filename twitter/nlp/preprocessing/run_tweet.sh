#!/user/bin/env bash

### NB: relatively slow ###

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run preprocessing on tweets 
# input, e.g. "openscience" or "replicationcrisis"
python /work/50114/twitter/nlp/preprocessing/preprocess_by_tweet.py \
    -i /work/50114/twitter/data/nlp/subsets/openscience_replicationcrisis_intersection.pickle \
    -o /work/50114/twitter/data/nlp/by_tweet/ \
