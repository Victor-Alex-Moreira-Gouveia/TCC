# TCC - Web Site Maus Tratos ao Animais

## 📋 Contexto do Projeto

### Sobre o Sistema
- **Nome do Projeto**: Vozes que não podem gritar
- **Objetivo**: Plataforma web de denúncia de maus-tratos a animais, orientação emergencial imediata, divulgação de notícias e conscientização.
- **Tipo**: Aplicação web com backend Flask, SQLAlchemy e banco de dados relacional.

### Status Atual
- ✅ Backend Flask organizado em controllers, models e services
- ✅ Entidades ORM implementadas com SQLAlchemy 2.x
- ✅ MariaDB, Memcached e backend configurados no Docker Compose
- ✅ Endpoint `/health` valida banco e cache
- ✅ CRUD implementado para usuários, notícias, comentários, curtidas e ajuda
- ✅ Formulário de denúncia alinhado ao ORM e ao banco, com orientação imediata
- ✅ Autenticação obrigatória para todo o conteúdo do site
- ✅ Suíte de testes atualizada e validada

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Linguagem** | Python 3.x |
| **Framework Backend** | Flask |
| **Banco de Dados** | MariaDB / MySQL |
| **Cache** | Memcached |
| **Containerização** | Docker + Docker Compose |
| **Server Production** | Gunicorn |
| **Persistência** | SQLAlchemy 2.x + PyMySQL |
| **Cache** | pymemcache |

---

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### 1️⃣ **Tabela: `usuarios`**
```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 2️⃣ **Tabela: `noticias`**
```sql
CREATE TABLE noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 3️⃣ **Tabela: `ajuda`**
```sql
CREATE TABLE ajuda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    tipo_denuncia VARCHAR(80) NOT NULL DEFAULT 'Animal doméstico',
    nivel_urgencia VARCHAR(80) NOT NULL DEFAULT 'Não informado',
    autor VARCHAR(150) NOT NULL DEFAULT 'anon'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4️⃣ **Tabela: `comentarios_noticias`**
```sql
CREATE TABLE comentarios_noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    noticia_id INT NOT NULL,
    usuario_id VARCHAR(80) NOT NULL,
    autor_nome VARCHAR(150) NOT NULL,
    texto TEXT NOT NULL,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (noticia_id) REFERENCES noticias(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 5️⃣ **Tabela: `curtidas_noticias`**
```sql
CREATE TABLE curtidas_noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    noticia_id INT NOT NULL,
    usuario_id VARCHAR(80) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_noticia_usuario (noticia_id, usuario_id),
    FOREIGN KEY (noticia_id) REFERENCES noticias(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 🎯 Funcionalidades Implementadas

### 1️⃣ **Rotas CRUD e Interações**

| Tabela / Recurso | CREATE | READ (All) | READ (Um) | UPDATE | DELETE |
|--------|--------|-----------|----------|--------|--------|
| **usuarios** | POST /api/usuarios | GET /api/usuarios | GET /api/usuarios/{id} | PUT /api/usuarios/{id} | DELETE /api/usuarios/{id} |
| **noticias** | POST /api/noticias (admin) | GET /api/noticias | GET /api/noticias/{id} | PUT /api/noticias/{id} (admin) | DELETE /api/noticias/{id} (admin) |
| **comentarios** | POST /api/noticias/{id}/comentarios | GET /api/noticias/{id}/comentarios | - | PUT /api/comentarios/{id} | DELETE /api/comentarios/{id} |
| **curtidas** | POST /api/noticias/{id}/curtida | - | - | - | DELETE /api/noticias/{id}/curtida |
| **ajuda** | POST /api/ajuda | GET /api/ajuda | GET /api/ajuda/{id} | PUT /api/ajuda/{id} | DELETE /api/ajuda/{id} |

---

## 🚀 Como Executar

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec server pytest -q test_crud.py
```
