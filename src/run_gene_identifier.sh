#!/bin/sh

echo "Run update resource"
cd FlyBaseAnnotationHelper
python3 update_resources.py

echo "Run annotation helper"
python3 annotation_helper.py /src/input/new_pub_dbxrefs.txt
