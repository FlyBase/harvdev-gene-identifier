
import psycopg2
import argparse
import os

parser = argparse.ArgumentParser()
d_txt = 'debug prints out messages.'
r_txt = 'refernce "FBrf" of paper to analyse.'
c_txt = 'Specify the location of the output file.'
parser.add_argument('-d', '--debug', help=d_txt,
                    default=False, action='store_true')
parser.add_argument('-f', '--filepath', help=c_txt, required=True)
parser.add_argument('-r', '--reference', help=r_txt, required=True)

args = parser.parse_args()


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
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor


def get_pubmed(cursor, filepath, fbrf):
    sql = f"""
    SELECT dx.accession
    FROM pub_dbxref pd, pub p, dbxref dx
    WHERE p.uniquename = '{fbrf}' AND 
          pd.pub_id = p.pub_id AND 
          pd.dbxref_id = dx.dbxref_id AND 
          dx.db_id = 50 -- pubmed
    """
    cursor.execute(sql)
    pids = cursor.fetchall()
    print(pids)
    filename = f"{filepath}/{fbrf}.txt"
    count = 0
    with open(filename, 'w') as outfile:
        for pid in pids:
            count += 1
            outfile.write(f"{pid[0]}\n")
    if count > 1:
        print(f"Could not find Pubmed id for {fbrf}")
        exit(-1)
    if count > 1:
        print(f"Warning: Multiple Pubmed id's for {fbrf} see {filename} for details.")


def start_process():
    cursor = create_postgres_session()
    get_pubmed(cursor, args.filepath, args.reference)

start_process()