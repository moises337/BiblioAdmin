import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (solo en desarrollo)
load_dotenv()

# Configuración del pool de conexiones
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20, dsn=DATABASE_URL
    )
except Exception as e:
    print(f"Error creating database pool: {e}")
    db_pool = None

def get_db_connection():
    """Obtiene una conexión del pool."""
    if db_pool is None:
        raise Exception("Database pool is not initialized")
    return db_pool.getconn()

def release_db_connection(conn):
    """Devuelve una conexión al pool."""
    if db_pool is None:
        raise Exception("Database pool is not initialized")
    db_pool.putconn(conn)

def execute_query(query, params=None, fetch=None):
    """
    Ejecuta una consulta SQL genérica.
    :param query: La consulta SQL a ejecutar.
    :param params: Tupla de parámetros para la consulta.
    :param fetch: 'one', 'all' o None (para INSERT, UPDATE, DELETE).
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        
        if fetch == "one":
            result = cur.fetchone()
        elif fetch == "all":
            result = cur.fetchall()
        else:
            conn.commit()
            result = None
            
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error en la base de datos: {error}")
        if conn:
            conn.rollback()
        raise error  # Re-raise the error to handle it in the calling function
    finally:
        if cur:
            cur.close()
        if conn:
            release_db_connection(conn)