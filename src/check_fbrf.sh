#!/bin/sh

#DB={DB} PGPASSWORD={PGPASSWORD} SERVER=localhost PORT=9091
echo "Getting pubmed id for reference $1"
echo "python3 src/get_pubmed_from_fbrf.py -f /src/input/ -r $1"
python3 src/get_pubmed_from_fbrf.py -f /src/input/ -r $1

echo "Run annotation helper"
cd FlyBaseAnnotationHelper
python3 update_resources.py
echo "python3 annotation_helper.py /src/input/$1.txt"
python3 annotation_helper.py /src/input/$1.txt
echo "Finished AH"

echo "Running Analysis on gene identifier output."
cd ..
echo "python3 src/analyse_output.py -f /src/output/output.tsv --compare_database"
python3 src/analyse_output.py -f /src/output/output.tsv --compare_database

# cat /src/output/output.tsv
mv /src/output/output.tsv /src/output/$1.tsv

mv /src/output/output.tsv.analysis.db_compare /src/output/$1.tsv.analysis.db_compare
echo "Output file is /data/harvdev/gene-identifier/output_files/$1.tsv.analysis.db_compare"
