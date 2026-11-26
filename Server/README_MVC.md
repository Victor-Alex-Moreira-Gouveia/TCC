# Organização MVC adaptada

## Estrutura implementada

```text
Server/
├── config/
│   ├── config.py             # .env, engine e sessões SQLAlchemy
│   └── __init__.py
├── controllers/
│   ├── usuarios.py           # Blueprint /api/usuarios
│   ├── noticias.py           # Blueprint /api/noticias (comentários, curtidas e gestão)
│   └── ajuda.py              # Blueprint /api/ajuda (denúncias e orientações)
├── models/
│   ├── base.py               # DeclarativeBase
│   ├── usuarios.py           # entidade e operações de usuários
│   ├── noticias.py           # entidades Noticia, ComentarioNoticia e CurtidaNoticia
│   └── ajuda.py              # entidade e operações de ajuda/denúncias
├── services/
│   └── orientacoes.py        # mapa de conduta emergencial imediata
├── templates/                # views HTML
├── static/                   # JavaScript, CSS e imagens
├── main.py                   # bootstrap Flask e trava de autenticação
└── wsgi.py                   # entrada do Gunicorn
```

## Fluxo de uma requisição

1. O Blueprint recebe JSON em uma rota `/api`.
2. O controller valida permissões de sessão e regras HTTP.
3. O model obtém uma sessão com `config.get_db()`.
4. O SQLAlchemy consulta ou altera a entidade ORM.
5. O controller devolve uma resposta JSON padronizada.

## Contrato do formulário de denúncia

O formulário `templates/Tcc/Ajuda/pedir_ajuda.html` envia `titulo`, `corpo`, `tipo_denuncia`, `nivel_urgencia` e `situacao_ocorrencia`. O backend acrescenta `autor` com base na sessão quando disponível. O relato é interno; após gravá-lo, a API retorna canais recomendados a partir do tipo e da situação, mas não aciona serviços externos. Consultas e alterações de relatos são administrativas.

## Aprovação de publicações de animais

Novos registros recebem `status_aprovacao=Pendente`. A API pública lista apenas os aprovados; o painel usa `/api/admin/animais-perdidos` e `/api/admin/animais-perdidos/<id>/aprovacao`, restritos a administradores. Aprovar publica; negar exclui a solicitação. O campo de moderação é separado de `status` (Perdido/Encontrado). A migração marca anúncios antigos como aprovados.

## Evolução

Ao alterar um formulário:

1. conferir os IDs usados no JavaScript;
2. conferir as chaves JSON enviadas;
3. atualizar a validação do controller;
4. atualizar o model e o script SQL;
5. adicionar compatibilidade para bancos existentes;
6. executar `docker compose exec server pytest -q test_crud.py`.
