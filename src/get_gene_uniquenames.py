import os
import psycopg2
import argparse

parser = argparse.ArgumentParser()
d_txt = 'debug prints out messages.'
c_txt = 'Specify the location of the output file.'
parser.add_argument('-d', '--debug', help=d_txt,
                    default=True, action='store_true')
parser.add_argument('-f', '--filepath', help=c_txt, required=True)
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
    # print(conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor


def get_uniquenames(cursor, outputfile):
    sql_dmel = """
        SELECT f.uniquename  
            FROM feature f, featureloc fl 
                WHERE fl.feature_id = f.feature_id AND
                      f.type_id = 219 AND
                      f.organism_id = 1 AND
                      f.is_obsolete = 'f' AND
                      uniquename like 'FBgn%'"""
    sql_hsap = """
        SELECT f.uniquename
            FROM feature f
                WHERE f.type_id = 219 AND
                      f.organism_id = 226 AND
                      f.is_obsolete = 'f' AND
                      uniquename like 'FBgn%'"""

    with open(outputfile, 'w') as outfile:
        for sql in [sql_dmel, sql_hsap]:
            i = 0
            cursor.execute(sql)
            records = cursor.fetchall()
            for record in records:
                i += 1
                if i < 10 and args.debug:
                    print(record[0])
                outfile.write(record[0] + '\n')
            if args.debug:
                print(f"Total for {sql} is {i}")


def start_process():
    cursor = create_postgres_session()
    get_uniquenames(cursor, f"{args.filepath}/currentDmelHsap.txt")

start_process()
