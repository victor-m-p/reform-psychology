#!/user/bin/env bash

# arguments (set max_results & max_count)
field=$1
query=$2

# run preprocessing for replication (query)
python /work/50114/MAG/preprocessing/query.py \
	-i /work/50114/MAG/data/raw \
	-f "psychology" \
	-q "replicat" \
	-o /work/50114/MAG/data/modeling

# run preprocessing for replication (fos) 
python /work/50114/MAG/preprocessing/fos.py \
	-i /work/50114/MAG/data/raw \
	-f "psychology" \
	-s "replication" \
	-o /work/50114/MAG/data/modeling

# run preprocessing for reproducibility (fos)
python /work/50114/MAG/preprocessing/fos.py \
	-i /work/50114/MAG/data/raw \
	-f "psychology" \
	-s "reproducibility" \
	-o /work/50114/MAG/data/modeling

# run preprocessing for open science (fos)
python /work/50114/MAG/preprocessing/fos.py \
	-i /work/50114/MAG/data/raw \
	-f "psychology" \
	-s "openscience" \
	-o /work/50114/MAG/data/modeling