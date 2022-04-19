#!/user/bin/env bash

### NB: relatively slow ###

# venv
VENVNAME=psyenv
source /work/50114/$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run msg decomposition
## NB: -i should be keyword
python /work/50114/twitter/nlp/msg/msg_nmf_only.py \
    -ic /work/50114/twitter/data/nlp/by_tweet/replicationcrisis_tweet_text_stopwords.csv \
    -iw /work/50114/twitter/data/nlp/msg/replicationcrisis_tweet_text_stopwords_W_k15.txt \
    -o /work/50114/twitter/data/nlp/msg/ \
    -p 2.2
