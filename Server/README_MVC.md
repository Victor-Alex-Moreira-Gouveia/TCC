# Organização MVC adaptada

## Estrutura implementada

```text
Server/
├── config/
│   ├── config.py             # .env, engine e sessões SQLAlchemy
│   └── __init__.py
├── controllers/
│   ├── usuarios.py           # Blueprint /api/usuarios
│   ├── noticias.py           # Blueprint /api/noticias
│   ├── ongs.py               # Blueprint /api/ongs
│   └── ajuda.py              # Blueprint /api/ajuda
├── models/
│   ├── base.py               # DeclarativeBase
│   ├── usuarios.py           # entidade e operações de usuários
│   ├── noticias.py           # entidade e operações de notícias
│   ├── ongs.py               # entidade e operações de ONGs
│   └── ajuda.py              # entidade e operações de ajuda
├── templates/                # views HTML
├── static/                   # JavaScript, CSS e imagens
├── main.py                   # bootstrap Flask
└── wsgi.py                   # entrada do Gunicorn
```

## Fluxo de uma requisição

1. O Blueprint recebe JSON em uma rota `/api`.
2. O controller valida campos e regras HTTP.
3. O model obtém uma sessão com `config.get_db()`.
4. O SQLAlchemy consulta ou altera a entidade ORM.
5. O controller devolve uma resposta JSON padronizada.

## Contrato do formulário de ajuda

O formulário público `templates/Tcc/Ajuda/pedir_ajuda.html` envia `titulo`, `corpo`, `pix_doacao`, `tipo_denuncia` e `nivel_urgencia`. O backend acrescenta `autor` com base na sessão. Todos esses campos possuem correspondência no modelo `Ajuda`.

## Evolução

Ao alterar um formulário:

1. conferir os IDs usados no JavaScript;
2. conferir as chaves JSON enviadas;
3. atualizar a validação do controller;
4. atualizar o model e o script SQL;
5. adicionar compatibilidade para bancos existentes;
6. executar `docker compose exec server pytest -q test_crud.py`.
