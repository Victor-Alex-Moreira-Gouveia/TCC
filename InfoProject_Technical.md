# Visão técnica - Vozes que não podem gritar

## Arquitetura atual

A aplicação usa Flask como camada HTTP, Gunicorn como servidor de produção e uma organização MVC adaptada:

- `controllers/`: Blueprints, validação de entrada, sessão e respostas HTTP.
- `models/`: entidades SQLAlchemy e operações de persistência.
- `services/`: regras de negócio e orientações emergenciais.
- `config/`: carregamento do `.env`, engine, fábrica de sessões e migrações.
- `templates/` e `static/`: interface Jinja2, JavaScript reativo e CSS.
- `main.py`: bootstrap Flask, trava global de autenticação e registro de Blueprints.
- `wsgi.py`: entrada do Gunicorn.

Blueprints registrados:

- `usuarios_bp`
- `noticias_bp` (notícias, comentários, curtidas)
- `ajuda_bp` (denúncias e orientações)

## Persistência e ORM

O SQLAlchemy usa `mysql+pymysql` para conectar ao MariaDB. A classe declarativa está em `models/base.py`; as entidades estão em:

- `models/usuarios.py` - `Usuario`
- `models/noticias.py` - `Noticia`, `ComentarioNoticia`, `CurtidaNoticia`
- `models/ajuda.py` - `Ajuda`

As sessões são criadas por `SessionLocal` e obtidas por `get_db()`. A aplicação executa migrações automáticas no bootstrap.

## Modelo `ajuda` (Denúncias)

Campos persistidos:

| Campo | Tipo | Obrigatório | Origem |
|---|---|---|---|
| `id` | inteiro auto incremento | sim | banco |
| `titulo` | `VARCHAR(255)` | sim | formulário |
| `corpo` | `TEXT` | sim | formulário |
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
