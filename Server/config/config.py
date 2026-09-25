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
    """Realiza migrações seguras: garante colunas novas, seed de notícias e descarta colunas/tabelas abandonadas."""
    import mimetypes

    # Caminho base para as imagens estáticas dentro do container/projeto
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IMG_DIR = os.path.join(BASE_DIR, 'static', 'img_posts')

    def _read_image(filename):
        """Lê bytes e mime type de uma imagem, retorna (bytes, mime) ou (None, None)."""
        filepath = os.path.join(IMG_DIR, filename)
        if not os.path.isfile(filepath):
            return None, None
        with open(filepath, 'rb') as f:
            data = f.read()
        mime, _ = mimetypes.guess_type(filepath)
        return data, mime or 'image/jpeg'

    SEED_NOTICIAS = [
        {
            'titulo': 'Mais de 100 animais são resgatados em situação de maus-tratos na Grande SP',
            'corpo': 'Mais de 100 animais foram resgatados de uma situação de maus-tratos em um sítio localizado em Mairiporã, na Grande São Paulo.\n\nA ação teve início após uma denúncia registrada em boletim de ocorrência. Policiais da 3ª Delegacia de Crimes contra Animais (Diima) cumpriram mandados de busca e apreensão no local.\n\nAo todo, foram encontrados 125 animais, sendo 60 cães, 55 gatos e 10 porcos. O responsável pelo local é investigado por não prestar os cuidados necessários aos animais.',
            'imagem': 'Imagem1.jpg',
            'data_hora': '2025-08-26 10:00:00',
        },
        {
            'titulo': "'Serial killer' de gatos: homem é preso por suspeita de maus-tratos a animais em São Paulo",
            'corpo': 'Um homem foi preso em Francisco Morato por maus-tratos a 18 animais, ameaça a pessoas e crime ambiental após denúncias de moradores e familiares.\n\nGuardas civis foram até o imóvel e encontraram 18 animais (13 gatos e 5 cães) em estado crítico, além de quatro gatos mortos e restos de animais enterrados.\n\nOs animais vivos foram encaminhados para atendimento veterinário. A polícia solicitou perícia no local e pediu a conversão da prisão em flagrante para preventiva.',
            'imagem': 'Imagem2.png',
            'data_hora': '2025-08-21 10:00:00',
        },
        {
            'titulo': 'Caso Cão Orelha: agressão a cachorro comunitário mobiliza investigação em Florianópolis',
            'corpo': 'Na madrugada entre 3 e 4 de janeiro, o cão comunitário Orelha foi vítima de maus-tratos no bairro Praia Brava, em Florianópolis (SC).\n\nEncontrado por moradores em uma área de mata com graves ferimentos na cabeça, o cão foi socorrido, mas precisou ser submetido à eutanásia devido à severidade das lesões.\n\nO caso ganhou repercussão nacional. Mandados de busca e apreensão foram cumpridos contra suspeitos e pessoas indiciadas por coação de testemunhas.',
            'imagem': 'Imagem3.jpg',
            'data_hora': '2026-01-26 10:00:00',
        },
        {
            'titulo': 'Tutor que cortou patas de cavalo em Bananal é investigado pela Polícia Civil',
            'corpo': 'A morte de um cavalo branco em Bananal, no interior de SP, gerou revolta nacional após imagens mostrarem o animal mutilado com um facão durante uma cavalgada.\n\nO tutor de 21 anos prestou depoimento e alegou acreditar que o equino já estivesse morto ao golpeá-lo, versão contestada por testemunhas.\n\nA Polícia Civil de São Paulo abriu inquérito para apurar as circunstâncias e responsabilidades pelo crime de maus-tratos.',
            'imagem': 'Imagem5.jpg',
            'data_hora': '2025-08-18 10:00:00',
        },
        {
            'titulo': 'China: Advogado de Xangai é acusado de torturar e matar milhares de gatos para vídeos online',
            'corpo': 'Um caso chocante de crueldade contra animais veio à tona em Xangai, onde um advogado local é acusado de torturar e matar felinos desde 2017 para comercializar vídeos na internet.\n\nA descoberta ocorreu após flagrante em um estacionamento subterrâneo por voluntários de proteção animal. Análises indicam mais de 300 vídeos produzidos e cerca de 4.000 gatos vitimados.\n\nOrganizações internacionais e protetores locais cobram punições severas e endurecimento das leis de proteção animal no país.',
            'imagem': 'Imagem6.jpg',
            'data_hora': '2025-09-26 10:00:00',
        },
        {
            'titulo': 'PRF resgata dois bezerros em situação de maus-tratos na BR-116 na Bahia',
            'corpo': 'Dois bezerros foram resgatados pela Polícia Rodoviária Federal (PRF) em ação conjunta com a Agência de Defesa Agropecuária da Bahia (Adab) na BR-116 em Vitória da Conquista.\n\nOs animais eram transportados trancados na gaveta lateral de um caminhão boiadeiro, sem ventilação, higiene ou espaço mínimo de mobilidade.\n\nOs bezerros foram encaminhados para assistência e o motorista assinou um Termo Circunstanciado de Ocorrência (TCO) por crime de maus-tratos.',
            'imagem': 'Imagem7.jpg',
            'data_hora': '2025-08-18 11:00:00',
        },
        {
            'titulo': 'Cavalos mantidos amarrados sob sol forte e feridos geram denúncias em Santarém',
            'corpo': 'Vídeos gravados por moradores do bairro São Cristóvão, em Santarém (PA), mostram dois cavalos mantidos amarrados e abandonados sob sol escaldante em um terreno baldio.\n\nUm dos animais apresentava ferimento visível na pata dianteira e exaustão extrema. Moradores relatam que a situação é recorrente e cobram fiscalização dos órgãos ambientais.',
            'imagem': 'Imagem8.jpg',
            'data_hora': '2025-08-15 10:00:00',
        },
        {
            'titulo': 'Homem é preso com mais de 1 mil aves silvestres no RJ; 180 morreram no transporte',
            'corpo': 'Em uma operação conjunta na BR-040 em Petrópolis, a PRF e a Polícia Federal resgataram 1.080 pássaros silvestres trazidos de Minas Gerais para venda ilegal em feiras no Rio de Janeiro.\n\nAproximadamente 180 aves foram encontradas mortas por asfixia e amontoamento em caixas de madeira e papelão. 820 pássaros com condições de saúde foram reabilitados para soltura.',
            'imagem': 'Imagem9.jpg',
            'data_hora': '2025-09-10 10:00:00',
        },
        {
            'titulo': 'Cão negligenciado com corrente pesada recebe resgate emocionante em Minas Gerais',
            'corpo': 'Denúncias mobilizaram a Sociedade Viçosense de Proteção aos Animais (SOVIPA) e a Polícia Ambiental em uma propriedade rural em Viçosa (MG).\n\nCães eram mantidos acorrentados entre entulhos e sujeira. O cão Ted foi resgatado debilitado e assustado, recebendo tratamento médico veterinário e acolhimento adequado.',
            'imagem': 'Imagem10.jpg',
            'data_hora': '2025-10-15 10:00:00',
        },
        {
            'titulo': '"Zara, a mamãe esqueleto": cadela em pele e osso usa últimas forças para amamentar no lixo em SP',
            'corpo': 'Uma cadela com severo quadro de desnutrição foi resgatada em Itariri (SP) após um pedido de socorro mobilizar voluntários e protetores locais.\n\nMesmo sem forças, Zara se mantinha deitada sob blocos de concreto e entulho para amamentar sua ninhada recém-nascida. A família foi transferida para um centro de reabilitação e adoção.',
            'imagem': 'Imagem4.jpg',
            'data_hora': '2025-06-30 10:00:00',
        },
        {
            'titulo': 'Filhote de anta de 15 dias é resgatado com fratura na pata no interior de SP',
            'corpo': 'Um filhote de anta de apenas 15 dias de vida foi resgatado nas proximidades de Planalto do Sul, interior paulista, apresentando fratura na pata traseira.\n\nO animal recebeu atendimento da Polícia Ambiental e da Associação Protetora dos Animais Silvestres de Assis. Assim que se recuperar, será reintroduzido ao habitat natural.',
            'imagem': 'Imagem12.jpg',
            'data_hora': '2025-09-07 10:00:00',
        },
        {
            'titulo': 'Polícia investiga maus-tratos após descoberta de animais enterrados em terreno em Adamantina',
            'corpo': 'A Polícia Civil de Adamantina (SP) instaurou inquérito para apurar crime ambiental após encontrar corpos de animais de pequeno e grande porte enterrados em um terreno.\n\nAs buscas iniciaram a partir de vídeos gravados por moradores. Cães sobreviventes encontrados no local foram acolhidos por uma ONG parceira.',
            'imagem': 'Imagem13.jpg',
            'data_hora': '2025-10-07 10:00:00',
        },
    ]

    try:
        with engine.begin() as conn:
            # ---------------------------------------------------------------
            # 1. Migração da tabela ajuda
            # ---------------------------------------------------------------
            try:
                cols = conn.execute(text('SHOW COLUMNS FROM ajuda')).fetchall()
                existing = {row[0] for row in cols}
                desired = {
                    'tipo_denuncia': "VARCHAR(80) NOT NULL DEFAULT 'Animal doméstico'",
                    'nivel_urgencia': "VARCHAR(80) NOT NULL DEFAULT 'Não informado'",
                }
                for column, definition in desired.items():
                    if column not in existing:
                        conn.execute(text(f'ALTER TABLE ajuda ADD COLUMN {column} {definition}'))
                if 'pix_doacao' in existing:
                    conn.execute(text('ALTER TABLE ajuda DROP COLUMN pix_doacao'))
            except Exception as exc:
                print(f'Alerta de schema Ajuda: {exc}')

            # ---------------------------------------------------------------
            # 2. Migração da tabela noticias para BLOB
            # ---------------------------------------------------------------
            try:
                cols_not = conn.execute(text('SHOW COLUMNS FROM noticias')).fetchall()
                existing_not = {row[0] for row in cols_not}
                # Adiciona imagem_blob se não existir
                if 'imagem_blob' not in existing_not:
                    conn.execute(text('ALTER TABLE noticias ADD COLUMN imagem_blob LONGBLOB NULL'))
                # Adiciona imagem_mime se não existir
                if 'imagem_mime' not in existing_not:
                    conn.execute(text('ALTER TABLE noticias ADD COLUMN imagem_mime VARCHAR(100) NULL'))
                # Remove imagem_url legada se existir
                if 'imagem_url' in existing_not:
                    conn.execute(text('ALTER TABLE noticias DROP COLUMN imagem_url'))
            except Exception as exc:
                print(f'Alerta de schema Notícias: {exc}')

            # ---------------------------------------------------------------
            # 3. Seed das 12 notícias com imagens binárias
            # ---------------------------------------------------------------
            try:
                count = conn.execute(text('SELECT COUNT(*) FROM noticias')).scalar()
                if count == 0:
                    for item in SEED_NOTICIAS:
                        img_bytes, img_mime = _read_image(item['imagem'])
                        conn.execute(
                            text(
                                'INSERT INTO noticias (titulo, corpo, imagem_blob, imagem_mime, data_hora) '
                                'VALUES (:titulo, :corpo, :imagem_blob, :imagem_mime, :data_hora)'
                            ),
                            {
                                'titulo': item['titulo'],
                                'corpo': item['corpo'],
                                'imagem_blob': img_bytes,
                                'imagem_mime': img_mime,
                                'data_hora': item['data_hora'],
                            }
                        )
                    print(f'Seed: {len(SEED_NOTICIAS)} notícias inseridas com imagens binárias.')
            except Exception as exc:
                print(f'Alerta de seed Notícias: {exc}')

            # ---------------------------------------------------------------
            # 4. Remove tabela ongs se ainda existir
            # ---------------------------------------------------------------
            try:
                conn.execute(text('DROP TABLE IF EXISTS ongs'))
            except Exception as exc:
                print(f'Alerta remoção ongs: {exc}')
    except Exception as exc:
        print(f'Alerta geral de migração: {exc}')


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