import argparse
import subprocess
import os

parser = argparse.ArgumentParser()

parser.add_argument('-r', '--reference', required=True)
args = parser.parse_args()


def process_fbrf(fbrf):
    #
    # Getting pubmed id for reference fbrf
    #
    (status, output) = subprocess.getstatusoutput(f"python3 src/get_pubmed_from_fbrf.py -f /src/input/ -r {fbrf}")
    if status:
        print("Getting pubmed id from FBrf failed, error output is:-")
        print(output)
        exit(-1)
    print("Getting pubmed id from FBrf successful")

    cwd = os.getcwd()
    # "Run annotation helper"
    # cd FlyBaseAnnotationHelper
    os.chdir(f"{cwd}/FlyBaseAnnotationHelper")

    # python3 update_resources.py
    (status, output) = subprocess.getstatusoutput("python3 update_resources.py")
    if status:
        print("Update resources failed, error output is:-")
        print(output)
        return
    print("Update resources successful")

    # "python3 annotation_helper.py /src/input/$1.txt"
    (status, output) = subprocess.getstatusoutput(f"python3 annotation_helper.py /src/input/{fbrf}.txt")
    if status:
        print("annotation helper failed, error output is:-")
        print(output)
        return
    print("Annotation helper successful")

    os.chdir(cwd)

    # "python3 src/analyse_output.py -f /src/output/output.tsv --compare_database"
    cmd = "python3 src/analyse_output.py -f /src/output/output.tsv --compare_database --ignore_gb"
    (status, output) = subprocess.getstatusoutput(cmd)
    if status:
        print("Analysis failed, error output is:-")
        print(output)
        return
    print("Analysis successful")

    # Rename generic files to fbrf specific ones.
    os.rename("/src/output/output.tsv", f"/src/output/{fbrf}.tsv")
    os.rename("/src/output/output.tsv.analysis.db_compare", f"/src/output/{fbrf}.tsv.analysis.db_compare")
    print(f"\nOutput file is /data/harvdev/gene-identifier/output_files/{fbrf}.tsv.analysis.db_compare")


process_fbrf(args.reference)