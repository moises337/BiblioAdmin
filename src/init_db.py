#!/usr/bin/env python3
"""
Script para inicializar la base de datos con las tablas y datos de ejemplo.
Este script se puede ejecutar en Render para configurar la base de datos.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def read_sql_file(filename):
    """Lee un archivo SQL y devuelve su contenido."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_dir = os.path.join(script_dir, '..', 'database')
    file_path = os.path.join(database_dir, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {file_path}")
        return None

def execute_sql_script(conn, sql_content, script_name):
    """Ejecuta un script SQL."""
    if not sql_content:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
        cur.close()
        print(f"✓ {script_name} ejecutado correctamente")
        return True
    except Exception as e:
        print(f"✗ Error ejecutando {script_name}: {e}")
        conn.rollback()
        return False

def init_database():
    """Inicializa la base de datos con todas las tablas y datos."""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        print("Error: DATABASE_URL no está configurada")
        return False
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        print("✓ Conectado a la base de datos")
        
        # Lista de scripts a ejecutar en orden
        scripts = [
            ('create_tables.sql', 'Creación de tablas'),
            ('functions_procedures.sql', 'Funciones y procedimientos'),
            ('triggers.sql', 'Triggers'),
            ('sample_data.sql', 'Datos de ejemplo')
        ]
        
        success = True
        for filename, description in scripts:
            sql_content = read_sql_file(filename)
            if not execute_sql_script(conn, sql_content, description):
                success = False
                break
        
        conn.close()
        
        if success:
            print("\n🎉 Base de datos inicializada correctamente")
            return True
        else:
            print("\n❌ Hubo errores durante la inicialización")
            return False
            
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)