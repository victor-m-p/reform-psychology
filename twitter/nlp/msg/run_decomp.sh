#!/user/bin/env bash

### NB: relatively slow ###

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run msg decomposition
## NB: -i should be keyword
python /work/50114/twitter/nlp/msg/msg_decomp.py \
    -i /work/50114/twitter/data/nlp/by_tweet/os_rc_5_typeretweet.csv \
    -o /work/50114/twitter/data/nlp/msg/topic_model \
    -t "clean_lemma" \
    -k 100

python /work/50114/twitter/nlp/msg/msg_decomp.py \
    -i /work/50114/twitter/data/nlp/by_tweet/os_rc_5_typeretweet.csv \
    -o /work/50114/twitter/data/nlp/msg/topic_model/ \
    -t "clean_lemma" \
    -k 50
