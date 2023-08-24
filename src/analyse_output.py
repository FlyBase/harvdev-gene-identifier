import os
import psycopg2
import argparse

parser = argparse.ArgumentParser()
d_txt = 'debug prints out messages.'
c_txt = 'Specify the location of the output file.'
parser.add_argument('-d', '--debug', help=d_txt,
                    default=True, action='store_true')
parser.add_argument('-f', '--filename', help=c_txt, required=True)
args = parser.parse_args()

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
            fp.pub_id = %s AND
            f.type_id = 219;"""

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
    for item in records:
        print(item)
        # outfile.write(f"{item}\n")
        # ('FBrf0252740', 399299, 'pubmed', '35037619')
        outfile.write(f"\nAnalysis for {item[0]} Pubmed {item[3]}\n")
        pub_id = item[1]
        print(type(pub_id))
        print(pub_id)
        print(genes_sql)
        cursor.execute(genes_sql, (pub_id,))
        genes = cursor.fetchall()
        if genes:
            outfile.write(f"{item[0]} has the following genes attached\n")
        for gene in genes:
            print(gene)
            gene_uniquenames.append(gene[0])
            outfile.write(f"\t{gene[0]}\t{gene[1]}\n")
        outfile.write(f"Gene identifier found the following genes:-\n")
    return gene_uniquenames


def print_gene_data(cursor, outfile, uniquename, score, gene_uniquenames):
    cursor.execute(gene_name_sql, (uniquename,))
    gene = cursor.fetchall()[0]
    status = "Good"
    if uniquename not in gene_uniquenames:
        status = "Bad"
    outfile.write(f"{uniquename}\t{gene[0]}\t{score}\t{status}\n")


def analyse_data(cursor, filename):
    last_pubmed = None
    with open(filename, 'r') as infile:
        lines = infile.readlines()

    with open(f"{filename}.anal", 'w') as outfile:
        for line in lines:
            (pubmed, uniquename, score) = line.split('\t')

            if not pubmed or pubmed != last_pubmed:
                last_pubmed = pubmed
                gene_uniquenames = print_pubmed_details(cursor, outfile, pubmed)
            print_gene_data(cursor, outfile, uniquename, score.strip(), gene_uniquenames)


def start_process():
    cursor = create_postgres_session()
    analyse_data(cursor, args.filename)


start_process()