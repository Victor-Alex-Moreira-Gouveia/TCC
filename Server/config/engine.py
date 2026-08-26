import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError

# Carrega o .env a partir da raiz, conforme recomendado
load_dotenv()

# Configuração do banco lendo das variáveis de ambiente padrão do projeto
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
    'database': os.getenv('DATABASE_NAME', 'MausTratosDB')
}

# Monta a URL de conexão usando o driver pymysql
DATABASE_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Cria a Engine do SQLAlchemy
# pool_pre_ping=True verifica se a conexão caiu antes de usá-la, evitando erros em containers
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Cria a fábrica de sessões (scoped_session é ideal para lidar com múltiplas requisições no Flask)
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)

def get_db():
    """
    Substitui a antiga conexão do mysql.connector[cite: 3].
    No SQLAlchemy com Flask, retornamos uma 'Session' que deve ser fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_schema(Base):
    """
    Substitui a migração manual[cite: 3]. 
    No padrão MVC do SQLAlchemy, você importa sua classe Base contendo 
    os modelos (usuarios, noticias, etc) e roda o create_all.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Migração automática: Tabelas sincronizadas com sucesso.")
    except Exception as e:
        print(f"Alerta de migração (inicialização rápida): {e}")

def test_mariadb():
    """Testa a conexão executando um comando SQL nativo via SQLAlchemy[cite: 3]."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True, "Conexão com Banco de Dados: OK"
    except OperationalError as e:
        return False, f"Erro de conexão: {str(e)}"

def detect_db_engine():
    """Detecta qual banco está rodando lendo a VERSION()[cite: 3]."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            # .scalar() extrai a primeira coluna da primeira linha do resultado
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