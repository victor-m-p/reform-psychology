# Reform-Psychology 

This Github repo contains the code-base for the Masters thesis of victor-m-p,
investigating the "reform psychology" and "open science" movements following the
"replication crisis" in psychology. It uses data scraped from Twitter and data from
Microsoft Academic Graph (MAG). 

## Description

The code falls in three main parts: 
* /MAG-data-curation
* /MAG
* /Twitter 

The folder /MAG-data-curation is early preprocessing and data curation of MAG data
needed for studying publication and citation behavior of replication studies (and 
other reform-psychology publications, e.g. open science). The code uses data from
a MAG image obtained on 2021-08-02 which cannot be shared. The code in /MAG-data-curation
was run on the high-performance cluster of ITU using SLURM scheduler and relies on Spark/Pyspark.  

The folder /MAG contains all analyses and plots from the citation/publication part of the
thesis. A main part of the analysis is bayesian modeling of citation behavior. 

The folder /Twitter contains the code-base for all Twitter-based analysis reported in the
thesis. This includes scraping, cleaning, network analysis (/network) and semantic analysis (/nlp).

## Dependencies

### /MAG-data-curation
* see MAG-data-curation/nerdenv.yml
* run on ubuntu server (hpc.itu.dk) using SLURM scheduler. 
* requires Spark/PySpark set-up

### /MAG and /Twitter
* see requirements.txt, create\_venv.sh and add\_venv.sh

## Files


### Files /MAG-data-curation

#### MAGmasters.py and MAGsparkmasters.py
Enables communication between Spark/PySpark and the hpc cluster at ITU (hpc.itu.dk).
Stores dtypes for the files that need to be loaded with PySpark. 

#### preprocessing.ipynb: 
Early preprocessing and subsetting of data used for the study.
Writes most of the files that are used in further analysis (https://github.com/victor-m-p/reform-psychology). 
E.g. 
* only relevant main fields of study (psychology, economics, sociology, political science). 
* from 2010-2021.
* journal articles. 
* all papers citing these focal articles.

### get\_subfields.ipynb: 
Extracts information from subfields, "open science", "reproducibility" and "replication".

### check\_preprocessing.ipynb:
Sanity check of the preprocessing, e.g. number of articles, number of authorships and document types. 

### check\_pipeline.ipynb: 
Sanity check of the intended analysis pipeline (see: https://github.com/victor-m-p/reform-psychology).
E.g. important that some articles actually do mention "replicat" in their titles. 

## Authors

Victor Møller Poulsen: [@vic\_moeller](https://github.com/victor-m-p) & [github](https://github.com/victor-m-p) <br/>
Lasse Buschmann Alsbirk: [github](https://github.com/buschbirk)
centre-for-humanities-computing (CHCAA): [github](https://github.com/centre-for-humanities-computing)

## Contributions

Victor Møller Poulsen conducted all analysis. <br/> 
Lasse Buschmann obtained the 2021-08-02 version of MAG and set up Spark/PySpark to work on the hpc.itu.dk
CHCAA contributed with parts of the code-base used for semantic analysis (Twitter/nlp). 

## License 

This project is licensed under the MIT License - (see the LICENSE.md file for details)

