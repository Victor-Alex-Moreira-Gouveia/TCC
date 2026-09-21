# TCC - Vozes que não podem gritar

Plataforma web para registro de denúncias de maus-tratos, orientação emergencial imediata, gerenciamento de notícias e interação comunitária.

## Stack atual

- Python 3.11
- Flask + Gunicorn
- SQLAlchemy 2.x com PyMySQL
- MariaDB
- Memcached com `pymemcache`
- Docker Compose
- Testes de integração com `pytest` e `requests`

## Funcionalidades Principais

1. **Autenticação Obrigatória:** Apenas usuários autenticados possuem acesso ao conteúdo e às funcionalidades da plataforma. Visitantes não autenticados são redirecionados para `/login`.
2. **Denúncia com Orientação Imediata:** Ao registrar uma denúncia, o sistema orienta imediatamente o usuário sobre ações emergenciais condizentes com a gravidade do caso.
3. **Notícias Administráveis:** Administradores (`admin`) possuem painel/modal para cadastrar, editar e excluir notícias. Usuários cadastrados (`user`) podem visualizar as notícias, curtir e comentar.
4. **Comentários e Curtidas:** Sistema de interação em tempo real com controle de permissões (1 curtida por usuário, comentários moderáveis por autor ou admin).

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
- Registro de denúncia: http://localhost:8080/ajuda/pedir

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

Em `Server/config/config.py`, o SQLAlchemy cria a engine, as sessões e executa a sincronização inicial das tabelas ORM e migrações automáticas.

## API REST

Todas as APIs usam JSON, exigem autenticação prévia (exceto login/cadastro/health) e usam o prefixo `/api`:

| Recurso | Operações |
|---|---|
| `usuarios` | `GET/POST /api/usuarios`, `GET/PUT/DELETE /api/usuarios/<id>` |
| `noticias` | `GET/POST /api/noticias`, `GET/PUT/DELETE /api/noticias/<id>` (Write ops apenas admin) |
| `comentarios` | `GET/POST /api/noticias/<id>/comentarios`, `PUT/DELETE /api/comentarios/<id>` |
| `curtidas` | `POST/DELETE /api/noticias/<id>/curtida` |
| `ajuda` | `GET/POST /api/ajuda`, `GET/PUT/DELETE /api/ajuda/<id>` |

As listagens são paginadas com `page` e `limit`. Respostas de sucesso usam `success`, `data` e `message`; erros usam `success`, `error`, `code` e `details`.

## Testes

Com os containers ativos:

```bash
docker compose exec server pytest -q test_crud.py
```

## Estrutura

```text
Server/
├── config/config.py          # .env, engine e migrações SQLAlchemy
├── controllers/              # Blueprints e validação das rotas
├── models/                   # Entidades ORM e operações de persistência
├── services/                 # Serviços de negócios (orientações emergenciais)
├── templates/                # Páginas Jinja2
├── static/                   # Assets da aplicação
│   ├── css/                  # Estilos de páginas e notificações
│   └── js/                   # Scripts reativos e interações
├── Databases/                # Scripts de inicialização MariaDB/MySQL
├── main.py                   # bootstrap e travas de segurança Flask
├── wsgi.py                   # entrada do Gunicorn
└── test_crud.py              # testes de integração automatizados
```
