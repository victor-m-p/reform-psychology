# Reform-Psychology preprocessing 

This github repo is dedicated to the preprocessing of Microsoft Academic Graph (MAG) data
which accompanies the reform-psychology Master's project (https://github.com/victor-m-p/reform-psychology). 

## Description

The code is early preprocessing of data from psychology, economics, sociology and political science,
needed for studying publication and citation behavior of replication studies (and other reform-psychology publications).
The code uses data from a share of MAG obtained on 2021-08-02 which cannot be shared.  

## Dependencies

* see nerdenv.yml
* run on ubuntu server (hpc.itu.dk) using SLURM scheduler. 
* requires spark/pyspark set-up

## Files

### MAGmasters.py and MAGsparkmasters.py
Enables communication between Spark/PySpark and the hpc cluster at ITU (hpc.itu.dk).
Stores dtypes for the files that need to be loaded with PySpark. 

### preprocessing.ipynb: 
Early preprocessing and subsetting of data used for the study.
Writes most of the files that are used in further analysis (https://github.com/victor-m-p/reform-psychology). 
E.g. 
* only relevant main fields of study (psychology, economics, sociology, political science). 
* from 2010-2021.
* journal articles. 
* all papers citing these focal articles.

### get_subfields.ipynb: 
Extracts information from subfields, "open science", "reproducibility" and "replication".

### check_preprocessing.ipynb:
Sanity check of the preprocessing, e.g. number of articles, number of authorships and document types. 

### check_pipeline.ipynb: 
Sanity check of the intended analysis pipeline (see: https://github.com/victor-m-p/reform-psychology).
E.g. important that some articles actually do mention "replicat" in their titles. 

## Authors

Victor Møller Poulsen: [@vic_moeller](https://github.com/victor-m-p) & [github](https://github.com/victor-m-p) <br/>
Lasse Buschmann Alsbirk: [github](https://github.com/buschbirk)

## Contributions

Victor Møller Poulsen conducted all main subsetting, sanity checking and analysis. <br/> 
Lasse Buschmann obtained the 2021-08-02 version of MAG and set up Spark/PySpark to work on the hpc.itu.dk

## License 

This project is licensed under the MIT License - (see the LICENSE.md file for details)

