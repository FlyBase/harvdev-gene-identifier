#!/bin/sh

echo "Get PMC data"
cd /src/input
curl https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz --output PMC-ids.csv.gz
gunzip --force PMC-ids.csv.gz

