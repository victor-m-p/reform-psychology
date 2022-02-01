#!/user/bin/env bash

# venv
sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source ../../$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt

# run text preprocessing for tweets 
python semantic_kernel/prep_data.py \
	-i ../data/nlp/NLP2CSV.csv \
	-o ../data/semantic_kernel/
