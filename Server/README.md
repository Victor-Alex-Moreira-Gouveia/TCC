# Meus Tratos - Backend

API REST do projeto Meus Tratos desenvolvida com Flask.

## 📁 Estrutura do Projeto

```
Server/
├── app/                      # Pacote principal da aplicação
│   ├── __init__.py          # Factory function da aplicação Flask
│   ├── config.py            # Configurações centralizadas (variáveis de ambiente)
│   ├── models/              # Camada de dados
│   │   ├── __init__.py
│   │   └── database.py      # Funções de conexão com banco de dados
│   ├── routes/              # Rotas/Endpoints da API
│   │   ├── __init__.py
│   │   ├── health.py        # Health check (status da aplicação)
│   │   ├── usuarios.py      # Endpoints de usuários
│   │   ├── noticias.py      # Endpoints de notícias
│   │   ├── ongs.py          # Endpoints de ONGs
│   │   └── ajuda.py         # Endpoints de ajudas
│   └── utils/               # Utilitários
│       ├── __init__.py
│       └── cache.py         # Funções de cache (Memcached)
├── wsgi.py                  # Entry point da aplicação (Gunicorn)
├── start.sh                 # Script de inicialização Docker
├── requirements.txt         # Dependências Python
├── Dockerfile               # Configuração Docker
└── Databases/               # Scripts de banco de dados
```

## 🚀 Como Executar

### Com Docker Compose (recomendado)
```bash
docker compose up -d
```

### Localmente
```bash
pip install -r requirements.txt
export FLASK_ENV=development
python wsgi.py
```

## 📊 Endpoints

### Health Check
- `GET /health/` - Status da aplicação e seus serviços

### Usuários
- `GET /usuarios/` - Listar usuários
- `GET /usuarios/<id>` - Obter usuário específico
- `POST /usuarios/` - Criar novo usuário
- `PUT /usuarios/<id>` - Atualizar usuário
- `DELETE /usuarios/<id>` - Deletar usuário

### Notícias
- `GET /noticias/` - Listar notícias
- `GET /noticias/<id>` - Obter notícia específica
- `POST /noticias/` - Criar nova notícia
- `PUT /noticias/<id>` - Atualizar notícia
- `DELETE /noticias/<id>` - Deletar notícia

### ONGs
- `GET /ongs/` - Listar ONGs
- `GET /ongs/<id>` - Obter ONG específica
- `POST /ongs/` - Criar nova ONG
- `PUT /ongs/<id>` - Atualizar ONG
- `DELETE /ongs/<id>` - Deletar ONG

### Ajudas
- `GET /ajuda/` - Listar ajudas
- `GET /ajuda/<id>` - Obter ajuda específica
- `POST /ajuda/` - Criar nova ajuda
- `PUT /ajuda/<id>` - Atualizar ajuda
- `DELETE /ajuda/<id>` - Deletar ajuda

## ⚙️ Configuração

As variáveis de ambiente estão definidas em `../.env`:

```env
DATABASE_HOST=mariadb
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=19032007
DATABASE_NAME=MeusTratosDB

CACHE_HOST=memcached
CACHE_PORT=11211

APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8080
```

## 📦 Tecnologias

- **Framework**: Flask
- **Banco de Dados**: MariaDB
- **Cache**: Memcached
- **WSGI Server**: Gunicorn
- **Container**: Docker

## 🔄 Próximos Passos

- [ ] Implementar conexão com banco de dados nos endpoints
- [ ] Adicionar validação de entrada
- [ ] Implementar autenticação/autorização
- [ ] Adicionar testes automatizados
- [ ] Documentação Swagger/OpenAPI
