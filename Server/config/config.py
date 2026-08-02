import os
from dotenv import load_dotenv

# Load .env from app root (works when running inside container or locally)
load_dotenv()

# Database config
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'mariadb'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', '19032007'),
    'database': os.getenv('DATABASE_NAME', 'MausTratosDB')
}

# Memcached
MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', 'memcached')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))

# Admin / root defaults (optional)
ROOT_USER = os.getenv('ROOT_USERNAME', 'admin')
ROOT_EMAIL = os.getenv('ROOT_EMAIL', 'admin@sistema.com')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD', 'admin123')

# Provide a helper to construct DB connection (keeps usage consistent)
import mysql.connector

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db_schema():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SHOW COLUMNS FROM ajuda LIKE 'autor'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE ajuda ADD COLUMN autor VARCHAR(150) NOT NULL DEFAULT 'anon'")
            conn.commit()
            print("Migração automática: Coluna 'autor' inserida na tabela 'ajuda'.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Alerta de migração (inicialização rápida): {e}")


def test_mariadb():
    try:
        conn = get_db()
        if conn.is_connected():
            conn.close()
            return True, "Conexão com MariaDB: OK"
    except Exception as e:
        return False, f"Erro MariaDB: {str(e)}"

