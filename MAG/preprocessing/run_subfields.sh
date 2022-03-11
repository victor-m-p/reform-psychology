#!/user/bin/env bash

# arguments (set max_results & max_count)
field=$1
subfield=$2

# venv
#sudo apt --allow-releaseinfo-change update
#VENVNAME=psyenv
#source ../$VENVNAME/bin/activate
#python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"

# run main file 
python /work/50114/MAG/preprocessing/subfields_main.py \
	-i /work/50114/MAG/data/raw \
	-f $field \
	-s $subfield \
	-o /work/50114/MAG/data/modeling
