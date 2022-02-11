#!/bin/bash

# Prophylactically update all the packages, optional.
apt -y update && apt -y upgrade

# Downloads and installs miniconda silently
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda

# Also prophylactic just to make sure commands run properly
export PATH="$HOME/miniconda/bin:$PATH"

# Initiate the conda environment
conda init

# Make sure the environment is activated by default
conda config --set auto_activate_base true

# Necessary to run conda commands still within a startup script (workaround to close and re-open your current shell)
source ~/miniconda/etc/profile.d/conda.sh

# set up our specific environment
conda env create -f environment.yml
conda activate bmcp
