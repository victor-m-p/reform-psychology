#!/user/bin/env bash

# venv
sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source ../../$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt

# run text preprocessing for tweets 
python preprocessing/TweetPreprocessing.py \
	-i ../data/ndjson/tweet_test/ \
	-o ../data/nlp/
