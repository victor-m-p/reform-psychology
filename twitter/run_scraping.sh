#!/user/bin/env bash

# arguments (set max_results & max_count)
max_results=$1
max_count=$2
token=scraping/res/bearer.txt
querry=scraping/res/querry.txt
querryname=scraping/res/querryname.txt
out_tweet=scraping/res/outpath_tweet.txt
out_user=scraping/res/outpath_user.txt
start_dates=scraping/res/start_dates.txt
end_dates=scraping/res/end_dates.txt

# venv
#sudo apt --allow-releaseinfo-change update
VENVNAME=psyenv
source ../$VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run main file 
python scraping/twitter_json.py \
	-mr $max_results \
	-mc $max_count \
	-sd $start_dates \
	-ed $end_dates \
	-bt $token \
	-q $querry \
	-qn $querryname \
	-ot $out_tweet \
	-ou $out_user
