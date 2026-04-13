import psycopg2
from config import load_config


def connect():
    """Connect to the PostgreSQL database server."""
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return None


if __name__ == '__main__':
    conn = connect()
    if conn is not None:
        conn.close()