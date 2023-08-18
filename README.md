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

    `fb_synonym_latest.tsv`  

    `PMC-ids.csv` (**TODO**: Download `PMC-ids.csv` via GoCD.)

3. Run the Docker image (interactive mode):

    `docker run -v /data/harvdev/gene-identifier/input_files:/usr/src/app/input_files -v /data/harvdev/gene-identifier/output_files:/usr/src/app/output_files -it gene-identifier`

4. Change to the bash shell inside the Docker container by typing `bash`.

5. Change to the directory `FlyBaseAnnotationHelper` by running `cd FlyBaseAnnotationHelper`/

6. Execute the command `python3 update_resources.py`.

7. Execute the command `python3 annotation_helper.py example_input.txt`

8. Output file can be found in the output directory, _e.g._ `/data/harvdev/gene-identifier/output_files`