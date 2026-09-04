# Visão técnica - Vozes que não podem gritar

## Arquitetura atual

A aplicação usa Flask como camada HTTP, Gunicorn como servidor de produção e uma organização MVC adaptada:

- `controllers/`: Blueprints, validação de entrada e respostas HTTP.
- `models/`: entidades SQLAlchemy e operações de persistência.
- `config/`: carregamento do `.env`, engine e fábrica de sessões.
- `templates/` e `static/`: interface Jinja2, JavaScript e CSS.
- `main.py`: criação da aplicação e registro dos Blueprints.
- `wsgi.py`: exportação da aplicação para o Gunicorn.

Blueprints registrados:

- `usuarios_bp`
- `noticias_bp`
- `ongs_bp`
- `ajuda_bp`

## Persistência e ORM

O SQLAlchemy usa `mysql+pymysql` para conectar ao MariaDB. A classe declarativa está em `models/base.py`; as entidades estão em:

- `models/usuarios.py` - `Usuario`
- `models/noticias.py` - `Noticia`
- `models/ongs.py` - `Ong`
- `models/ajuda.py` - `Ajuda`

As sessões são criadas por `SessionLocal` e obtidas por `get_db()`. A aplicação executa `Base.metadata.create_all()` no bootstrap e garante a compatibilidade da tabela `ajuda` com bancos criados anteriormente.

## Modelo `ajuda`

Campos persistidos:

| Campo | Tipo | Obrigatório | Origem |
|---|---|---|---|
| `id` | inteiro auto incremento | sim | banco |
| `titulo` | `VARCHAR(255)` | sim | formulário |
| `corpo` | `TEXT` | sim | formulário |
| `pix_doacao` | `VARCHAR(100)` | sim | formulário |
| `tipo_denuncia` | `VARCHAR(80)` | sim | formulário, com default |
| `nivel_urgencia` | `VARCHAR(80)` | sim | formulário, com default |
| `autor` | `VARCHAR(150)` | sim | sessão/backend |

## Configuração

O `.env` deve existir na raiz, ser baseado em `.env.example` e permanecer fora do Git. Dentro do Compose, o host do banco é `mariadb`, a porta interna é `3306` e o banco é `MausTratosDB`.

## Execução e verificação

```bash
docker compose up -d --build
curl http://localhost:8080/health
docker compose exec server pytest -q test_crud.py
```

O health check valida MariaDB com SQLAlchemy (`SELECT 1` e `SELECT VERSION()`) e Memcached com uma operação de escrita/leitura. A validação atual retorna HTTP 200 e 48 testes aprovados.

## Operação e segurança

- Não versionar `.env`, credenciais ou volumes locais.
- Usar secrets do ambiente de implantação em produção.
- `docker compose down -v` é destrutivo para os dados locais do MariaDB.
- O login administrativo atual é híbrido e possui credenciais definidas no código de autenticação; isso deve ser substituído por configuração segura antes de produção.
