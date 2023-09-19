import os
import psycopg2
import argparse

cutoff = 0.7

description = f"""
Code to process the output file from gene_identifier and add more information, to make it more readable.
Added information include FBrf number, gene synonym and any flags for that paper 
(cam_flag, dis_flag, harv_flag and pmid_added).

If compare_database flag added then a list of the papers genes are added at the start and at the end of each gene line a
status value which can be Good, Bad or Below_cutoff:
    Good: Found in list of genes for that paper.
    Bad:  Not found in list of genes for that paper.
    Below_cutoff: No lookup done as it is below the check threshold.

A cutoff value of {cutoff} is used to determine the correctness of the call against the database.
i.e. if a gene has a score of 0.03 then this will just be marked as Below_cutoff. 

gene_identifier is ran each epicycle and the output is placed in the directory
/data/harvdev/gene_identifier/output_files and is ran without the --compare_database flag.

--compare_database 
  Should only be added if the papers have already had their genes added.
  It looks up what genes have been added to a paper in the database so if this has not been done yet
  then the results will look terrible.
  
"""

examples = """

Example:
Process an old set of results from a previous epicycle run, lets say last week of august 2023.

Files are named by the monday and friday dates, so here it would be 20230821-20230825.tsv

python3 src/analyse_output.py -f /data/harvdev/gene_identifier/output_files/20230821-20230825.tsv --compare_database

Output can be found in /data/harvdev/gene_identifier/output_files/20230821-20230825.tsv.analysis

Run the docker image if repo not installed.

docker run --network='host' --rm -e SERVER=$SERVER -e USER=$USER -e PGPASSWORD=$PGPASSWORD -e PORT=$PORT -e DB=$DB \
-v /var/go/harvdev-gene-identifier/src:/src -v /data/harvdev/gene-identifier/output_files:/src/output \
--entrypoint python3 flybase/harvdev-gene-identifier  /src/analyse_output.py \
-f /src/output/20230821-20230825.tsv -c

"""
parser = argparse.ArgumentParser(description=description,
                                 epilog=examples,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
d_txt = 'Debug prints out messages.'
f_txt = 'Specify the location of the output file from gene_identifier to be processed.'
c_txt = """Compare genes to those in the database for each paper.
         (Off by default as we mostly process new papers here and as a new paper has no genes 
          attached to it yet this is pointless)"""

parser.add_argument('-d', '--debug', help=d_txt,
                    default=True, action='store_true')
parser.add_argument('-f', '--filename', help=f_txt, required=True)
parser.add_argument('-c', '--compare_database', help=c_txt, required=False, default=False, action='store_true')
args = parser.parse_args()



error_codes = {'Bad_pmcid': 1,
               'No_Matches': 1,
               'No_nxml': 1}

bad_count = 0
good_count = 0

flag_sql = """
    SELECT cvt.name, pp.value
    FROM cvterm cvt, pubprop pp
    WHERE pp.type_id = cvt.cvterm_id AND 
          cvt.name in ('harv_flag', 'cam_flag', 'pmid_added', 'dis_flag') AND 
          pp.pub_id = %s;"""

fbrf_sql = """
    SELECT p.uniquename, p.pub_id, db.name, dx.accession 
      FROM db, dbxref dx, pub p, pub_dbxref px
      WHERE dx.db_id = db.db_id AND
            px.pub_id=p.pub_id AND
            px.dbxref_id=dx.dbxref_id AND
            dx.accession = %s;"""

genes_sql = """
    SELECT f.uniquename, f.name
      FROM feature_pub fp, feature f 
      WHERE fp.feature_id = f.feature_id AND
            f.type_id = 219 AND
            fp.pub_id = %s ;"""

gene_name_sql = """SELECT name from feature where uniquename = %s"""


def create_postgres_session():
    """Connect to database."""
    user = os.environ['USER']
    password = os.environ['PGPASSWORD']
    server = os.environ['SERVER']
    try:
        port = os.environ['PORT']
    except KeyError:
        port = '5432'

    database = os.environ['DB']

    # 1. Set up database connection and queries.

    # Database connection.
    conn_string = "host=%s dbname=%s user=%s password='%s' port=%s" % (server, database, user, password, port)
    # print(conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor


def print_pubmed_details(cursor, outfile, pubmed):
    cursor.execute(fbrf_sql, (pubmed,))
    records = cursor.fetchall()
    gene_uniquenames = []
    count = 0
    for item in records:
        count += 1
        outfile.write(f"\nAnalysis for {item[0]} Pubmed {item[3]}\n")
        pub_id = int(item[1])

        cursor.execute(flag_sql, (pub_id,))
        flags = cursor.fetchall()
        if flags:
            outfile.write(f"\nFlags for {item[0]}:-\n")
            for flag in flags:
                outfile.write(f"\t{flag[0]}\t{flag[1]}\n")

        cursor.execute(genes_sql, (pub_id,))
        genes = cursor.fetchall()
        if genes:
            outfile.write(f"{item[0]} has the following genes attached\n")
            for gene in genes:
                gene_uniquenames.append(gene[0])
                outfile.write(f"\t{gene[0]}\t{gene[1]}\n")
        else:
            outfile.write(f"{item[0]}, {item[1]}, {item[2]}, {item[3]} has No genes attached\n")

    if not count:
        outfile.write(f"\nPubmed {pubmed} Not in db therefore no analysis\n")
    return gene_uniquenames


def print_gene_data(cursor, outfile, uniquename, score, gene_uniquenames, compare_database):
    global good_count, bad_count
    if uniquename in error_codes:
        bad_count += 1
        return
    cursor.execute(gene_name_sql, (uniquename,))
    gene = cursor.fetchall()[0]
    score = float(score)
    if score < cutoff:
        status = "Below_cutoff"
    else:
        status = "Good"
        if uniquename not in gene_uniquenames:
            status = "Bad"
    if compare_database:
        outfile.write(f"{uniquename}\t{gene[0]}\t{score:.4f}\t{status}\n")
    else:
        outfile.write(f"{uniquename}\t{gene[0]}\t{score:.4f}\n")
    good_count += 1


def mail_message():
    global good_count, bad_count
    print(f"{good_count} {bad_count} Need to email, Victoria and harvdev?")


def process_gene_list(cursor, gene_list, last_pubmed, outfile, compare_database):
    if not last_pubmed:
        return
    count = 0
    gene_uniquenames = print_pubmed_details(cursor, outfile, last_pubmed)
    for item in sorted(gene_list.items(), key=lambda item: item[1], reverse=True):
        if not count and item[0] not in error_codes:
            outfile.write(f"Gene identifier found the following genes:-\n")
            count += 1
        print_gene_data(cursor, outfile, item[0], item[1], gene_uniquenames, compare_database)
    if not count:
        outfile.write(f"Gene identifier could not process {last_pubmed}:-\n")


def analyse_data(cursor, filename, compare_database):
    global good_count, bad_count

    last_pubmed = None
    with open(filename, 'r') as infile:
        lines = infile.readlines()
    bad_count = 0
    good_count = 0
    gene_list = {}
    outfile = open(f"{filename}.analysis", 'w')
    for line in lines:
        (pubmed, uniquename, score) = line.split('\t')
        score = float(score.strip())
        if not pubmed or pubmed != last_pubmed:
            # process last set
            process_gene_list(cursor, gene_list, last_pubmed, outfile, compare_database)
            last_pubmed = pubmed
            gene_list = {uniquename: score}
        else:
            gene_list[uniquename] = score

    if last_pubmed:
        process_gene_list(cursor, gene_list, last_pubmed, outfile, compare_database)
    if bad_count > good_count:
        mail_message()
    print(f"good:{good_count}, bad:{bad_count}")


def start_process():
    cursor = create_postgres_session()
    analyse_data(cursor, args.filename, args.compare_database)


start_process()