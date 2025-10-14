import psycopg2
from psycopg2.extras import RealDictCursor

# PostgreSQL connection parameters
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "orders_db"
DB_USER = "postgres"
DB_PASSWORD = "root"

def get_connection():
    """
    Returns a connection object to the PostgreSQL database.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor  # returns rows as dictionaries
    )
    return conn
