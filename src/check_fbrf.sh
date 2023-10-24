#!/bin/sh

#DB={DB} PGPASSWORD={PGPASSWORD} SERVER=localhost PORT=9091
echo "Getting pubmed id for reference $1"
echo "python3 src/get_pubmed_from_fbrf.py -f /src/input/ -r $1 2>&1 /src/output/$1.gpff.log"
python3 src/get_pubmed_from_fbrf.py -f /src/input/ -r $1

echo "Run annotation helper"
cd FlyBaseAnnotationHelper
echo "python3 annotation_helper.py /src/input/$1.txt 2>&1 /src/output/$1.ah.log"
python3 annotation_helper.py /src/input/$1.txt
echo "Finished AH"

"Running Analysis on gene identifier output."
cd ..
echo "python3 src/analyse_output.py -f /src/output/$1.tsv --compare_database  2>&1 /src/output/$1.ao.log"
python3 src/analyse_output.py -f /src/output/$1.tsv --compare_database

cat /src/output/$1.db_compare

echo "Output file is /data/harvdev/gene-identifier/output_files/$1.tsv.db_compare"
