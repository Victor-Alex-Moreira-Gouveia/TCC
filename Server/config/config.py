import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

# Carrega o .env a partir da raiz do projeto
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
    'database': os.getenv('DATABASE_NAME', 'MausTratosDB'),
}

MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', 'memcached')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))

ROOT_USER = os.getenv('ROOT_USERNAME', 'admin')
ROOT_EMAIL = os.getenv('ROOT_EMAIL', 'admin@sistema.com')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD', 'admin123')

DATABASE_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)


def get_db():
    """Retorna uma sessão SQLAlchemy do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_ajuda_schema():
    """Adiciona colunas compatíveis com o formulário de ajuda em bancos antigos."""
    try:
        with engine.begin() as conn:
            cols = conn.execute(text('SHOW COLUMNS FROM ajuda')).fetchall()
            existing = {row[0] for row in cols}
            desired = {
                'tipo_denuncia': "VARCHAR(80) NOT NULL DEFAULT 'Animal doméstico'",
                'nivel_urgencia': "VARCHAR(80) NOT NULL DEFAULT 'Não informado'",
            }
            for column, definition in desired.items():
                if column not in existing:
                    conn.execute(text(f'ALTER TABLE ajuda ADD COLUMN {column} {definition}'))
    except Exception as exc:
        print(f'Alerta de schema Ajuda: {exc}')


def init_db_schema(Base=None):
    """Cria as tabelas do ORM quando a aplicação inicializa."""
    try:
        if Base is None:
            from models import Base as BaseModel
            BaseModel.metadata.create_all(bind=engine)
        else:
            Base.metadata.create_all(bind=engine)
        ensure_ajuda_schema()
        print('Migração automática: Tabelas sincronizadas com sucesso.')
    except Exception as exc:
        print(f'Alerta de migração (inicialização rápida): {exc}')


def test_mariadb():
    """Testa a conexão executando um comando SQL nativo via SQLAlchemy."""
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
            return True, 'Conexão com Banco de Dados: OK'
    except OperationalError as exc:
        return False, f'Erro de conexão: {str(exc)}'


def detect_db_engine():
    """Detecta o tipo de banco a partir da versão do servidor."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT VERSION()'))
            version = result.scalar()

            if not version:
                return 'unknown', ''

            version_str = str(version)
            if 'MariaDB' in version_str:
                return 'mariadb', version_str
            if 'MySQL' in version_str:
                return 'mysql', version_str

            return 'unknown', version_str
    except Exception as exc:
        return 'unknown', str(exc)