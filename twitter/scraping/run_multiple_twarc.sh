#!/user/bin/env bash

# arguments (set max_results & max_count)
querryname=$1
querry=$2
#start_dates=$(< /work/50114/twitter/scraping/res/start_dates.txt)
#end_dates=$(< /work/50114/twitter/scraping/res/end_dates.txt)
start_dates=$3
end_dates=$4
outname1=/work/50114/twitter/data/raw/twarc_raw/$querryname.json
outname2=/work/50114/twitter/data/raw/twarc_flat/$querryname.ndjson

# venv
#sudo apt --allow-releaseinfo-change update
#VENVNAME=psyenv
#source /work/50114/$VENVNAME/bin/activate
#python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run main file
twarc2 searches --combine-queries --start-time $start_dates --end-time $end_dates --archive $querry $outname1
twarc2 flatten $outname1 $outname2

