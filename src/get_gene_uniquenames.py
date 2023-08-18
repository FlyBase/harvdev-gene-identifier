import os
import psycopg2

def create_postgres_session():
    """Connect to database."""
    user = os.environ['USER']
    password = os.environ['PASSWORD']
    server = os.environ['SERVER']
    try:
        port = os.environ['PORT']
    except KeyError:
        port = '5432'

    database = os.environ['DATABASE']

    # 1. Set up database connection and queries.

    # Database connection.
    conn_string = "host=%s dbname=%s user=%s password='%s'" % (server, database, user, password)
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
            cursor.execute(sql)
            records = cursor.fetchall()
            for record in records:
                outfile.write(record)

def start_process():
    cursor = create_postgres_session()
    get_uniquenames(cursor, "./uniquenames.txt")

start_process()
