import os
import psycopg2
import argparse

description = f"""
Code to process the output file from gene_identifier and load into new chado table
"""

examples = """

Example:
Process an old set of results from a previous epicycle run, lets say last week of august 2023.

Files are named by the monday and friday dates, so here it would be 20230821-20230825.tsv

python3 src/tsv_load_to_chado.py -f /data/harvdev/gene_identifier/output_files/20230821-20230825.tsv

"""
parser = argparse.ArgumentParser(description=description,
                                 epilog=examples,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
d_txt = 'Debug prints out messages.'
f_txt = 'Specify the location of the output file from gene_identifier to be processed.'
parser.add_argument('-d', '--debug', help=d_txt,
                    default=False, action='store_true')
parser.add_argument('-f', '--filename', help=f_txt, required=True)
args = parser.parse_args()


def get_analysis_id(cursor):
    sql = """ SELECT analysis_id from analysis where program = 'flyBERT' AND not is_obsolete"""
    cursor.execute(sql)
    analysis_id = cursor.fetchone()[0]
    return analysis_id


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
    return conn


def get_lookups(cursor, filename, debug):
    pmid_to_pub_id = {}
    unique_to_feat_id = {}
    pmid_list = []
    gene_list = []
    # first pass of file to get lookups
    with open(filename, "r") as f:
        input_list = f.readlines()
        for line in input_list:
            (pubmed, uniquename, _) = line.split('\t')
            pmid_list.append(pubmed)
            gene_list.append(uniquename)

    genes_str = "'" + "' ,'".join(gene_list) + "'"
    genes_sql = f"""
        SELECT f.uniquename, f.feature_id
          FROM feature f 
          WHERE f.uniquename in ({genes_str});"""
    cursor.execute(genes_sql, (genes_str,))
    for line in cursor.fetchall():
        if debug:
            print(f"GENE {line[0]} {line[1]}")
        unique_to_feat_id[line[0]] = line[1]

    pubmed_str = "'" + "' ,'".join(pmid_list) + "'"
    fbrf_sql = f"""
        SELECT dx.accession, p.pub_id
          FROM db, dbxref dx, pub p, pub_dbxref px
          WHERE dx.db_id = db.db_id AND
                px.pub_id=p.pub_id AND
                px.dbxref_id=dx.dbxref_id AND
                dx.accession in ({pubmed_str});"""
    if debug:
        print(fbrf_sql)
    cursor.execute(fbrf_sql)
    for line in cursor.fetchall():
        if debug:
            print(f"PMID {line[0]} {line[1]}")
        pmid_to_pub_id[line[0]] = line[1]
    return pmid_to_pub_id, unique_to_feat_id


def process_tsv_file(cursor, filename, debug):
    analysis_id = get_analysis_id(cursor)
    pmid_to_pub_id, unique_to_feat_id = get_lookups(cursor, filename, debug)
    ins_sql = "INSERT INTO pub_analysis_feature (pub_id, analysis_id, feature_id, score, status) VALUES (%s, %s, %s, %s, 'Suggested')"
    with open(filename, "r") as f:
        input_list = f.readlines()
        for line in input_list:
            (pubmed, uniquename, score) = line.split('\t')
            if uniquename == 'Bad_pmcid' or uniquename == 'No_Matches' or uniquename == 'No_nxml':
                continue
            if debug:
                print(f"{pubmed} -> {pmid_to_pub_id[pubmed]}, {uniquename} -> {unique_to_feat_id[uniquename]}")
            try:
                cursor.execute(ins_sql, (pmid_to_pub_id[pubmed], analysis_id, unique_to_feat_id[uniquename], float(score)))
            except psycopg2.errors.UniqueViolation:
                print("Duplicate keys error, this pub must already have been analysed with flyBERTY!")
                pass
    cursor.close()


def start_process():
    conn = create_postgres_session()
    cursor = conn.cursor()
    process_tsv_file(cursor, args.filename, args.debug);
    conn.commit()


start_process()