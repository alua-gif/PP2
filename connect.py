import psycopg2

def connect():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="фдгф2025"
    )
    print("CONNECTED")
    return conn





 