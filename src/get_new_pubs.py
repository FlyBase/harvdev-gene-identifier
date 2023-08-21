
import psycopg2
import argparse
import os

parser = argparse.ArgumentParser()
d_txt = 'debug prints out messages.'
c_txt = 'Specify the location of the output file.'
parser.add_argument('-d', '--debug', help=d_txt,
                    default=False, action='store_true')
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
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor

#"""SELECT %s_id, pub_id, transaction_timestamp from audit_chado ac, %s pt
#    where ac.audited_table = '%s' and
#    record_pkey = %s_id and
#    transaction_timestamp between '%s'::date and
#    now() and audit_transaction in ('U','I')"""
#,$tab,$tab,$tab,$tab,$tstamp));

def get_new_pubs_dbxrefs(cursor, outputfile):
    sql = f"""
    SELECT pub_dbxref_id, pub_id, transaction_timestamp from audit_chado ac, pub_dbxref pt
        where ac.audited_table = 'pub_dbxref' and
              record_pkey = pub_dbxref_id and
              transaction_timestamp between '{os.environ['MONDAY_DATE']}'::date and now() and
              audit_transaction in ('U','I')"""

    cursor.execute(sql)
    dbxrefs = cursor.fetchall()
    print(dbxrefs)


def start_process():
    cursor = create_postgres_session()
    get_new_pubs_dbxrefs(cursor, f"{args.filepath}/new_pub_dbxrefs.txt")


start_process()


start_process()