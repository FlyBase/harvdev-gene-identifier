#!/bin/sh

echo "Get PMC data"
curl https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz --output /usr/src/app/input_files/PMC-ids.csv.gz
gunzip /usr/src/app/input_files/PMC-ids.csv.gz

