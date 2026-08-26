import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError

# Carrega o .env a partir da raiz[cite: 11, 12]
load_dotenv()

# Configuração do banco lendo das variáveis de ambiente padrão do projeto[cite: 11, 12]
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
    'database': os.getenv('DATABASE_NAME', 'MausTratosDB')
}

# Memcached
MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', 'memcached')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))

# Admin / root defaults (optional)[cite: 11]
ROOT_USER = os.getenv('ROOT_USERNAME', 'admin')
ROOT_EMAIL = os.getenv('ROOT_EMAIL', 'admin@sistema.com')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD', 'admin123')

# Monta a URL de conexão usando o driver pymysql
DATABASE_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Cria a Engine do SQLAlchemy[cite: 12]
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Cria a fábrica de sessões[cite: 12]
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)

def get_db():
    """Retorna uma 'Session' que deve ser fechada após o uso[cite: 12]."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_schema(Base):
    """Sincroniza as tabelas com o banco de dados[cite: 12]."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Migração automática: Tabelas sincronizadas com sucesso.")
    except Exception as e:
        print(f"Alerta de migração (inicialização rápida): {e}")

def test_mariadb():
    """Testa a conexão executando um comando SQL nativo via SQLAlchemy[cite: 12]."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True, "Conexão com Banco de Dados: OK"
    except OperationalError as e:
        return False, f"Erro de conexão: {str(e)}"

def detect_db_engine():
    """Detecta qual banco está rodando lendo a VERSION()[cite: 12]."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar() 
            
            if not version:
                return 'unknown', ''
            
            version_str = str(version)
            if 'MariaDB' in version_str:
                return 'mariadb', version_str
            if 'MySQL' in version_str:
                return 'mysql', version_str
            
            return 'unknown', version_str
    except Exception as e:
        return 'unknown', str(e)