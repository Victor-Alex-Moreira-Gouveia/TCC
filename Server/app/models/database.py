import mysql.connector
from app.config import Config

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return mysql.connector.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD,
        database=Config.DATABASE_NAME
    )

def close_db_connection(conn):
    """Fecha conexão com o banco de dados"""
    if conn.is_connected():
        conn.close()
