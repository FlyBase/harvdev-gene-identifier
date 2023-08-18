# gene-identifier
## Installation
1. Clone this repository.
2. Update the `config.ini` file as necessary.
2. Build the Docker image:

    `docker build -f Dockerfile . --progress plain -t gene-identifier`

## Running
1. Create two local directories "input_files" and "output_files", _e.g._

    `/data/harvdev/gene-identifier/input_files`

    `/data/harvdev/gene-identifier/output_files`

2. Ensure the input_files directory contains the following files:


    `currentDmelHsap.txt`

    `(docker run --user $(id -u):$(id -g) -v ${HOME}/${DATABASE}/bulk_reports/:/src/output/ --network="host" --entrypoint /usr/bin/perl bulk_reports harvdev-reports/report_fb_synonym.pl $SERVER $DATABASE $USER $PGPASSWORD ./output/fb_synonym_${DATABASE}.tsv)`
    `src/report_fb_synonym.pl this would be better`
    `wget http://ftp.flybase.net/releases/FB2023_04/precomputed_files/synonyms/fb_synonym_fb_2023_04.tsv.gz`
    `fb_synonym_latest.tsv`  

    `docker run  -v /Users/ilongden/harvard/gene-identifier/data:/usr/src/app/input_files  --entrypoint sh gene-identifier /usr/src/app/src//get_PMC.sh'
    `PMC-ids.csv` (**TODO**: Download `PMC-ids.csv` via GoCD.)

3. Run the Docker image (interactive mode):

    `docker run -v /data/harvdev/gene-identifier/input_files:/usr/src/app/input_files -v /data/harvdev/gene-identifier/output_files:/usr/src/app/output_files -it gene-identifier`

4. Cselect count(1) from feature f, featureloc fl where fl.feature_id =f.feature_id and f.type_id = 219 and f.organism_id = 1 and f.is_obsolete = 'f' and uniquename like 'FBgn%'hange to the bash shell inside the Docker container by typing `bash`.

5. Change to the directory `FlyBaseAnnotationHelper` by running `cd FlyBaseAnnotationHelper`/

6. Execute the command `python3 update_resources.py`.

7. Execute the command `python3 annotation_helper.py example_input.txt`

8. Output file can be found in the output directory, _e.g._ `/data/harvdev/gene-identifier/output_files`