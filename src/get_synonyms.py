import os
import psycopg2

def create_postgres_session():
    """Connect to database."""
    user = os.environ['USER']
    password = os.environ['connection']['PASSWORD']
    server = os.environ['connection']['SERVER']
    try:
        port = os.environ['connection']['PORT']
    except KeyError:
        port = '5432'

    database = os.environ['DATABASE']

    # 1. Set up database connection and queries.

    # Database connection.
    conn_string = "host=%s dbname=%s user=%s password='%s'" % (server, database, user, password)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    sql = """"""