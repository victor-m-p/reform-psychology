#!/user/bin/env bash

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run nmf & network
## NB: think about keywords potentially
python /work/50114/twitter/nlp/msg/msg_edgelist_topics.py \
    -i /work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_W.txt \
    -o /work/50114/twitter/data/nlp/msg/semantic_topics/ \
