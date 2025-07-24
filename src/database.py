import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración del pool de conexiones
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20, dsn=os.environ.get("DATABASE_URL")
)

def get_db_connection():
    """Obtiene una conexión del pool."""
    return db_pool.getconn()

def release_db_connection(conn):
    """Devuelve una conexión al pool."""
    db_pool.putconn(conn)

def execute_query(query, params=None, fetch=None):
    """
    Ejecuta una consulta SQL genérica.
    :param query: La consulta SQL a ejecutar.
    :param params: Tupla de parámetros para la consulta.
    :param fetch: 'one', 'all' o None (para INSERT, UPDATE, DELETE).
    """
    conn = None
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
            
        cur.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error en la base de datos: {error}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            release_db_connection(conn)