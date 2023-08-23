# harvdev-gene-identifier

## Introduction.
This repo is a helper script to get the latest data from a FlyBase database and dockerise and run <br>
https://github.com/grivaz/FlyBaseAnnotationHelper and <br>
https://huggingface.co/cgrivaz/FlyBaseGeneAbstractClassifier

See these for information on how the code all works.
NOTE: To generate the data using this repo you will need access to a FlyBase postgres database.
      If you do not have this then you must generate the data another way but call the file names the same things.


## Installation
1. Clone this repository.
2. Build docker image OR pull from dockerhub
    1) docker build . -t gene-identifier
    2) docker pull flybase/harvdev-gene-identifier

NOTE: gene-identifier being used in examples below. Switch names in commands if using the pulled image.

## Environment variables needed
1. USER               - FlyBase postgres db user name 
2. PGPASSWORD         - FlyBase postgres password
3. SERVER             - FlyBase postgres server
      if using local db instance you need to use `host.docker.internal` 
4. PORT               - FlyBase postgres port
5. DB                 - FlyBase postgres db name
6. PORT               - FlyBase postgres port
7. MONDAY_DATE        - start date used to generate new Pubs in FlyBase.
8. GI_DATA_INPUT      - local directory to store files needed to run gene-identifier (*optional, can change docker command directly)
9. GI_DATA_OUTPUT     - local directory to put output from gene-identifier (*optional)

## Data files needed (skip this if generating these in interactive shell)
1. Generate a list of Dmel and Hsap current gene synonyms (fb_synonym_latest.tsv)
        `docker run --rm -p$PORT:$PORT -v $GI_DATA_INPUT:/src/input/ -e SERVER=$SERVER -e PGPASSWORD=$PGPASSWORD -e USER=$USER -e DB=$DB -e PORT=$PORT --entrypoint /usr/bin/python3 gene-identifier src/get_synonyms_batch.py --filepath /src/input/`
  
2. Generate a list of Dmel and Hsap gene unique names (currentDmelHsap.txt)
        `docker run --rm -p$PORT:$PORT -v $GI_DATA_INPUT:/src/input/ -e SERVER=$SERVER -e PGPASSWORD=$PGPASSWORD -e USER=$USER -e DB=$DB -e PORT=$PORT  --entrypoint /usr/bin/python3 gene-identifier src/get_gene_uniquenames.py --filepath /src/input/`
 
3. Get PMC ids file (PMC-ids.csv)
       `docker run --rm -v $GI_DATA_INPUT:/src/input/ --entrypoint /usr/bin/bash gene-identifier src/get_PMC.sh`

4. Get PMC's to examine (new_pub_dbxrefs.txt)
       `docker run  --rm -p$PORT:$PORT -v $GI_DATA_INPUT:/src/input/ -e SERVER=$SERVER -e PGPASSWORD=$PGPASSWORD -e MONDAY_DATE=$MONDAY_DATE -e USER=$USER -e DB=$DB -e PORT=$PORT --entrypoint /usr/bin/python3 gene-identifier src/get_new_pubs.py --filepath /src/input/`
       Note you can also create this by hand by just adding a list on PMC identifiers.

## Running
1. Run the gene identifier code (interactive mode):

    1) `docker run --rm -v $GI_DATA_INPUT:/src/input -e SERVER=$SERVER -e PGPASSWORD=$PGPASSWORD -e USER=$USER -e DB=$DB -e PORT=$PORT -v $GI_DATA_OUTPUT:/usr/src/app/output_files -it gene-identifier`
    2) If input files not created yet create them
       1. python3 src/get_synonyms_batch.py --filepath /src/input/
       2. python3 src/get_gene_uniquenames.py --filepath /src/input/
       3. python3 src/get_new_pubs.py --filepath /src/input/
       4. sh src/get_PMC.sh
    3) Change to the directory `FlyBaseAnnotationHelper` by running `cd FlyBaseAnnotationHelper`
    4) Execute the command `python3 update_resources.py`
    5) Execute the command `python3 annotation_helper.py /usr/src/app/output_files/new_pub_dbxrefs.txt`
    6) Output file can be found in the output directory, $GI_DATA_OUTPUT outside of docker and /usr/src/app/output_files inside docker

2. Run code on command line locally (via GoCd etc))
   1) Get the files needed by following Datafiles needed section or via alternative methods.
   2) docker run --rm -v $GI_DATA_INPUT:/src/input -v $GI_DATA_OUTPUT:/src/output --entrypoint /usr/bin/bash gene-identifier src/run_gene_identifier.sh
