#!/user/bin/env bash

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run nmf & network
## NB: think about keywords potentially
python /work/50114/twitter/nlp/msg/msg_edgelist_tweets.py \
    -ic /work/50114/twitter/data/nlp/by_tweet/os_rc_5_typeretweet.csv \
    -iw /work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_W.txt \
    -o /work/50114/twitter/data/nlp/msg/semantic_tweets/ \
    -t "clean_lemma" \
    -p 2 # 2.2 for bropenscience