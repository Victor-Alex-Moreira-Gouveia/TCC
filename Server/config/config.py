import os
import mysql.connector 
from mysql.connector import IntegrityError, DatabaseError
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configurações vindas do ambiente (Docker Compose)
# ---------------------------------------------------------------------------

load_dotenv('../../.env')

DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST'),
    'port': int(os.getenv('DATABASE_PORT')),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'database': os.getenv('DATABASE_NAME')
}

MEMCACHED_HOST = os.getenv('MEMCACHED_HOST')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT'))

ROOT_USER = os.getenv('ROOT_USERNAME')
ROOT_EMAIL = os.getenv('ROOT_EMAIL')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD')

# ---------------------------------------------------------------------------
# Helpers de banco de dados e resposta
# ---------------------------------------------------------------------------

def get_db():
    """Retorna uma nova conexão com o MariaDB."""
    return mysql.connector.connect(**DB_CONFIG)

def init_db_schema():
    """Garante a estrutura correta do banco de dados (coluna autor em ajuda)."""
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
    
