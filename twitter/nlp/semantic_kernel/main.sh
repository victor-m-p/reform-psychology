#!/usr/bin/env bash

# input vars
TRAIN=false
SEEDS=res/*
ASSOCIATIONS=assoc/*
PRUNINGS=prun/*

# venv
sudo apt-get --allow-releaseinfo-change update
sudo apt-get -y install graphviz graphviz-dev
sudo apt-get -y install zip unzip

VENVNAME=semanticenv
source $VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt

# train vector representations
if [ $TRAIN = true ]
then
    echo "[INFO] training vectors..."
    python src/train_vectors.py \
        -i '/work/50114/twitter/data/nlp/semantic_kernel/bropenscience/lemma' \
        -vo 'mdl/vectors_bropenscience.pcl' \
        -mo 'mdl/w2v_bropenscience.pcl'
else
    echo "[INFO] using existing vectors"
fi

# build kernel and graph
for seedls in $SEEDS
do 
    for associations in $ASSOCIATIONS 
    do
        echo "[INFO] Processing $seedls file..."
        echo "[INFO] Processing $associations file..."
        python src/build_kernel_new.py --model mdl/vectors_bropenscience.pcl --seed $seedls --association $associations --norm True
        
        for prunings in $PRUNINGS
        do
            echo "[INFO] Processing $prunings file..."
            python src/build_graph_new.py --seed $seedls --type 'bropenscience' --association $associations --pruning $prunings
            echo "-----"

        done 
    done
done

# write all figures to comptessed file for download
zip -r /work/50114/twitter/fig/nlp/semantic_kernel/bropenscience.zip /work/50114/twitter/fig/nlp/semantic_kernel/bropenscience
