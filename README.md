# TCC - Vozes que não podem gritar

Plataforma web para denúncias de maus-tratos, pedidos de ajuda, divulgação de notícias e integração com ONGs.

## Stack atual

- Python 3.11
- Flask + Gunicorn
- SQLAlchemy 2.x com PyMySQL
- MariaDB
- Memcached com `pymemcache`
- Docker Compose
- Testes de integração com `pytest` e `requests`

## Executando com Docker

Na raiz do projeto, crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
docker compose up -d --build
```

O arquivo `.env` é interno e não deve ser versionado. O Compose o utiliza nos serviços `server` e `mariadb`.

Endpoints principais:

- Aplicação: http://localhost:8080/
- Health check: http://localhost:8080/health
- Formulário público de ajuda: http://localhost:8080/ajuda/pedir

Para acompanhar ou encerrar os serviços:

```bash
docker compose ps
docker compose logs -f server
docker compose down
```

O comando `docker compose down -v` remove também o volume do MariaDB e apaga os dados locais.

## Serviços e portas

| Serviço | Porta local | Uso |
|---|---:|---|
| `server` | 8080 | Flask/Gunicorn |
| `mariadb` | 3307 | Banco MariaDB (3306 dentro da rede Docker) |
| `memcached` | 11211 | Cache |

O backend espera MariaDB e Memcached ficarem saudáveis antes de iniciar. O script `Server/Databases/MariaDB_MauTratos.sql` inicializa o banco em um volume novo.

## Configuração

Variáveis principais do `.env`:

```dotenv
DATABASE_HOST=mariadb
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=definida-localmente
DATABASE_NAME=MausTratosDB
MEMCACHED_HOST=memcached
MEMCACHED_PORT=11211
```

Em `Server/config/config.py`, o SQLAlchemy cria a engine, as sessões e executa a sincronização inicial das tabelas ORM. Bancos já existentes recebem as colunas novas do formulário de ajuda quando necessário.

## API REST

Todas as APIs usam JSON e o prefixo `/api`:

| Recurso | Operações |
|---|---|
| `usuarios` | `GET/POST /api/usuarios`, `GET/PUT/DELETE /api/usuarios/<id>` |
| `noticias` | `GET/POST /api/noticias`, `GET/PUT/DELETE /api/noticias/<id>` |
| `ongs` | `GET/POST /api/ongs`, `GET/PUT/DELETE /api/ongs/<id>` |
| `ajuda` | `GET/POST /api/ajuda`, `GET/PUT/DELETE /api/ajuda/<id>` |

As listagens são paginadas com `page` e `limit`. Respostas de sucesso usam `success`, `data` e `message`; erros usam `success`, `error`, `code` e, quando aplicável, `details`.

## Formulário de ajuda

O formulário envia:

```json
{
  "titulo": "Título do caso",
  "corpo": "Descrição da ocorrência",
  "pix_doacao": "contato@pix.com",
  "tipo_denuncia": "Animal doméstico",
  "nivel_urgencia": "Ferimento grave"
}
```

O campo `autor` é preenchido pelo backend a partir da sessão. `tipo_denuncia` e `nivel_urgencia` possuem valores padrão para manter compatibilidade com registros antigos.

## Testes

Com os containers ativos:

```bash
docker compose exec server pytest -q test_crud.py
```

A suíte valida health check, paginação e CRUD completo dos quatro recursos. A última validação executada resultou em **48 testes aprovados**.

## Estrutura

```text
Server/
├── config/config.py          # .env, engine e sessões SQLAlchemy
├── controllers/              # Blueprints e validação das rotas
├── models/                   # Entidades ORM e operações de persistência
├── templates/                # Páginas Jinja2
├── static/                   # Assets da aplicação
│   ├── css/                  # Estilos específicos de páginas
│   ├── js/                   # Scripts específicos de páginas
│   └── img_posts/            # Imagens das notícias
├── Databases/                # Scripts de inicialização MariaDB/MySQL
├── main.py                   # bootstrap Flask
├── wsgi.py                   # entrada do Gunicorn
└── test_crud.py              # testes de integração
```

A convenção detalhada de organização dos templates, assets e documentos está em [`Docs/README.md`](Docs/README.md).
