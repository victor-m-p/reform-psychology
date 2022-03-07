#!/usr/bin/env bash

VENVNAME=semanticenv

python3 -m venv $VENVNAME
source $VENVNAME/bin/activate

pip install --upgrade pip

#sudo apt-get update allow-releaseinfo-change
#sudo apt-get update --fix-missing
sudo apt --allow-releaseinfo-change update
sudo apt -y install graphviz graphviz-dev
sudo apt -y install zip unzip

# problems when installing from requirements.txt
pip install ipython
pip install jupyter
pip install matplotlib
pip install pygraphviz

python -m ipykernel install --user --name=$VENVNAME

test -f requirements.txt && pip install -r requirements.txt

deactivate
echo "build $VENVNAME"
