#!/user/bin/env bash

# arguments (set max_results & max_count)

# venv
#sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source ../../$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run tweet preprocessing for networks  
python preprocessing/NetworkTweet2CSV.py \
	-i ../data/ndjson/tweet_test/ \
	-o ../data/network/ \

# run user preprocessing for networks 
python preprocessing/NetworkUser2CSV.py \
	-i ../data/ndjson/user_test/ \
	-o ../data/network/
