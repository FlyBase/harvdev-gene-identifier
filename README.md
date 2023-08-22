# gene-identifier
## Installation
1. Clone this repository.
2. Update the `config.ini` file as necessary.
2. Build the Docker image:

    `docker build -f Dockerfile . --progress plain -t gene-identifier`

## Running
1. Create two local directories "input_files" and "output_files", _e.g._

    `/local/gene-identifier/input_files`

    `/local/gene-identifier/output_files`

2. Needed environments variables.
   1) USER               - FlyBase postgres db user name 
   2) PGPASSWORD         - FlyBase postgres password
   3) SERVER             - FlyBase postgres server
   4) PORT               - FlyBase postgres port
   5) DB                 - FlyBase postgres db name
   6) PORT               - FlyBase postgres port
   7) GI_DATA_INPUT      - local directory to store files needed to run gene-identfier (*optional, can change docker command directly)
   8) GI_DATA_OUTPUT     - local directory to put output from gene-identfier (*optional)

3. Create input_files externally (skip here if doing interactively):

    1) Generate a list of Dmel and Hsap current gene synonyms (fb_synonym_latest.tsv)
        `docker run --user $(id -u):$(id -g) -v $GI_DATA_INPUT:/src/input/ --network="host" -e SERVER=$SERVER -e PGPASSWORD=$PGPASSWORD -e USER=$USER -e DB=$DB -e PORT=$PORT --entrypoint /usr/bin/python gene-identifier src/get_synonyms_batch.py --filepath /src/input/`
  
    2) Generate a list of Dmel and Hsap gene unique names (currentDmelHsap.txt)
        `(docker run --user $(id -u):$(id -g) -v $GI_DATA_INPUT:/src/input/ --network="host" -e SERVER=$SERVER -e PGPASSWORD=$PGPASSWORD -e USER=$USER -e DB=$DB -e PORT=$PORT  --entrypoint /usr/bin/python gene-identifier src/get_gene_uniquenames.py --filepath /src/input/`
 
    3) Get PMC ids file (PMC-ids.csv))
       `(docker run --user $(id -u):$(id -g) -v $GI_DATA_INPUT:/src/input/ --network="host" --entrypoint /usr/bin/bash gene-identifier src/get_PMC.sh --filepath /src/input/`

    4) Get PMC's to examine (new_pub_dbxrefs.txt)
       `docker run  -v /local/gene-identifier/data:/usr/src/app/input_files  --entrypoint /usr/bin/python gene-identifier src/get_new_pubs.py --filepath /src/input/`


3. Run the gene identifier code (interactive mode):

    1) `docker run -v $GI_DATA_INPUT:/usr/src/app/input_files -v $GI_DATA_OUTPUT:/usr/src/app/output_files -it gene-identifier`
    2) If input files not created yet you can do that now by running the commands in 3 in docker directly.
    3) Change to the directory `FlyBaseAnnotationHelper` by running `cd FlyBaseAnnotationHelper`
    4) Execute the command `python3 update_resources.py`
    5) Execute the command `python3 annotation_helper.py /usr/src/app/output_files/new_pub_dbxrefs.txt`
    6) Output file can be found in the output directory, _e.g._ `/local/gene-identifier/output_files`

4. Run code on commandline locally (via GoCd etc))
    1) 