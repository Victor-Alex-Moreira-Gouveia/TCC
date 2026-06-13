# TCC - Web Site Maus Tratos ao Animais

## 📋 Contexto do Projeto

### Sobre o Sistema
- **Nome do Projeto**: Vozes que não podem gritar
- **Objetivo**: Plataforma web de denúncia, documentação e combate a maus-tratos com integração com ONGs e sistema de contribuições
- **Tipo**: Aplicação web com backend robusto e banco de dados relacional

### Status Atual
- ✅ Estrutura inicial do backend criada
- ✅ Banco de dados completamente modelado e estruturado
- ✅ Arquivos SQL e Docker configurados
- ✅ Endpoint de health check funcional
- ✅ Rotas CRUD implementadas
- ✅ Páginas de teste existem
- ✅ Testes automatizados existem

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
| **HTTP Client** | mysql-connector-python, pymemcache |

### Dependências Atuais (requirements.txt)
```
flask
gunicorn
pymemcache
mysql-connector-python
werkzeug
pytest
requests
```

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
- **Entidade**: Usuários do sistema
- **Chaves Únicas**: email
- **Uso**: Autenticação e gerenciamento de contas

#### 2️⃣ **Tabela: `noticias`**
```sql
CREATE TABLE noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
- **Entidade**: Notícias e artigos sobre combate a maus-tratos
- **Auto-gerado**: data_hora usa CURRENT_TIMESTAMP
- **Uso**: Feed de conteúdo informativo

#### 3️⃣ **Tabela: `ongs`**
```sql
CREATE TABLE ongs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_instituicao VARCHAR(150) NOT NULL,
    endereco_fisico VARCHAR(255) DEFAULT NULL,
    site VARCHAR(255) DEFAULT NULL,
    pix_doacao VARCHAR(100) NOT NULL,
    CONSTRAINT chk_endereco_ou_site CHECK (endereco_fisico IS NOT NULL OR site IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
- **Entidade**: ONGs parceiras do projeto
- **Validação**: Ao menos endereço físico OU site deve estar preenchido
- **Uso**: Listagem e integração com organizações

#### 4️⃣ **Tabela: `ajuda`**
```sql
CREATE TABLE ajuda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    pix_doacao VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
- **Entidade**: Seções de ajuda e suporte
- **Uso**: FAQ, guias de denúncia, instruções

---

## 🎯 Tarefas Requeridas

### 1️⃣ **Rotas CRUD Completas**

#### Operações por Tabela

| Tabela | CREATE | READ (All) | READ (Um) | UPDATE | DELETE |
|--------|--------|-----------|----------|--------|--------|
| **usuarios** | POST /api/usuarios | GET /api/usuarios | GET /api/usuarios/{id} | PUT /api/usuarios/{id} | DELETE /api/usuarios/{id} |
| **noticias** | POST /api/noticias | GET /api/noticias | GET /api/noticias/{id} | PUT /api/noticias/{id} | DELETE /api/noticias/{id} |
| **ongs** | POST /api/ongs | GET /api/ongs | GET /api/ongs/{id} | PUT /api/ongs/{id} | DELETE /api/ongs/{id} |
| **ajuda** | POST /api/ajuda | GET /api/ajuda | GET /api/ajuda/{id} | PUT /api/ajuda/{id} | DELETE /api/ajuda/{id} |

#### Requisitos por Operação

**CREATE (POST)**
- Validações de entrada (campos obrigatórios, tipos de dados)
- Verificação de unicidade (email na tabela usuarios)
- Tratamento de erros HTTP adequado (400, 409 para conflito)
- Retorno com ID gerado

**READ (GET)**
- Lista paginada com limite configurável (limite padrão: 10)
- Filtros por campo quando aplicável
- Busca por ID com erro 404 quando não encontrado
- Retorno estruturado com metadata (total, página)

**UPDATE (PUT)**
- Validação de ID existente (404 se não encontrado)
- Validação parcial de dados (campos opcionais)
- Verificação de restrições (ex: CHECK constraint de ongs)
- Retorno com dados atualizados

**DELETE (DELETE)**
- Validação de ID (404 se não encontrado)
- Sucesso retorna código 204 No Content
- Possibilidade de soft-delete em tabelas sensíveis

### 2️⃣ **Criar Páginas de Teste Funcionais**

Gerar páginas HTML simples (sem CSS avançado, apenas estrutura) para testar cada CRUD:

- **Uma página por tabela** em `/Server/templates/Tcc/`
- Exemplo: `test_usuarios.html`, `test_noticias.html`, `test_ongs.html`, `test_ajuda.html`
- Cada página deve conter:
  - Formulário para CREATE (POST)
  - Tabela/lista para READ (GET)
  - Botões para UPDATE (PUT) - editar cada item
  - Botões para DELETE (DELETE) - remover cada item
  - Botão de "Recarregar" para atualizar dados
  - Área de output/logs para exibir respostas da API
  - Tratamento visual de erros

- **Uma página INDEX** (`test_index.html`) com links para todas as páginas de teste

### 3️⃣ **Garantia de Qualidade e Testes**

Implementar testes automatizados para validar operações:

**Tipos de Testes a Implementar:**
- Testes unitários para validações de entrada
- Testes de integração para operações CRUD
- Testes de banco de dados para constraints e integridade
- Testes de erro (campos obrigatórios faltando, tipos inválidos, etc.)

**Arquivo sugerido**: `/Server/test_crud.py`
- Use `pytest` ou `unittest` do Python
- Testes devem ser executáveis via `pytest test_crud.py` ou `python -m unittest`
- Cada teste deve ter escopo independente (criar dados, testar, limpar)

**Validações Críticas:**
- ✅ POST cria registro e retorna ID
- ✅ GET busca registro criado
- ✅ PUT atualiza dados corretamente
- ✅ DELETE remove registro (não encontra mais)
- ✅ Validações de campo obrigatório funcionam
- ✅ Email único na tabela usuarios é enforçado
- ✅ Check constraint de ONGs (endereco_fisico OR site) funciona
- ✅ Erros HTTP apropriados retornam (400, 404, 409, 500)

---

## 📁 Estrutura de Arquivos Esperada

```
/Server/
├── main.py                          # ← MODIFICAR/EXPANDIR
├── requirements.txt                 # ← MANTER
├── Dockerfile                       # ← MANTER
├── start.sh                         # ← MANTER
├── Databases/
│   ├── MariaDB_MauTratos.sql       # ← MANTER
│   └── MySQL_MauTratos.sql         # ← MANTER
├── templates/Tcc/
│   ├── Index.html                  # ← MANTER
│   ├── style.css                   # ← MANTER
│   ├── test_index.html             # ← CRIAR
│   ├── test_usuarios.html          # ← CRIAR
│   ├── test_noticias.html          # ← CRIAR
│   ├── test_ongs.html              # ← CRIAR
│   └── test_ajuda.html             # ← CRIAR
└── test_crud.py                     # ← CRIAR
```

---

## 🔧 Especificações Técnicas Detalhadas

### Configuração da Aplicação
- URL base: `http://localhost:8080` (desenvolvimento)
- Prefix de APIs: `/api`
- Content-Type: `application/json`
- Charset: UTF-8

### Formato de Resposta Padrão

**Success (200, 201)**
```json
{
  "success": true,
  "data": { /* dados */ },
  "message": "Operação realizada com sucesso"
}
```

**Error (400, 404, 409, 500)**
```json
{
  "success": false,
  "error": "Descrição do erro",
  "code": "ERROR_CODE",
  "details": { /* informações adicionais */ }
}
```

**List Response (200)**
```json
{
  "success": true,
  "data": [ /* items */ ],
  "pagination": {
    "total": 42,
    "page": 1,
    "limit": 10,
    "pages": 5
  }
}
```

### Validações Obrigatórias

| Campo | Validação |
|-------|-----------|
| `email` (usuarios) | Formato válido + Único no banco |
| `senha` (usuarios) | Mínimo 8 caracteres |
| `titulo` | Não vazio, máximo 255 chars |
| `corpo` | Não vazio, máximo 65535 chars |
| `pix_doacao` | Formato válido de chave PIX |
| `endereco_fisico` + `site` (ongs) | Ao menos um preenchido |

### Tratamento de Erros

| Situação | HTTP Code | Message |
|----------|-----------|---------|
| Validação falhou | 400 | "Validação falhou: [detalhes]" |
| Recurso não encontrado | 404 | "Recurso não encontrado" |
| Email já existe | 409 | "Email já registrado no sistema" |
| Erro no banco de dados | 500 | "Erro interno do servidor" |
| Sucesso ao criar | 201 | "Criado com sucesso" |
| Sucesso ao deletar | 204 | (sem body) |

---

## 🎓 Requisitos Educacionais para o TCC

Este projeto deve demonstrar:
- ✅ Modelagem correta de banco de dados relacional
- ✅ Implementação de API RESTful seguindo boas práticas
- ✅ Validação e tratamento robusto de erros
- ✅ Testes automatizados e qualidade de código
- ✅ Documentação clara de endpoints e funcionalidades
- ✅ Containerização com Docker para reprodutibilidade

---

## 🚀 Como Usar Este Prompt

1. **Copie este prompt completo**
2. **Cole no Antigravity** ou sua ferramenta de IA preferida
3. **Especifique qual tarefa quer priorizar**:
   - "Implemente as rotas CRUD"
   - "Crie as páginas de teste"
   - "Escreva os testes automatizados"
   - "Gere tudo de uma vez"

### Exemplo de Uso
```
"Você é um desenvolvedor backend Python especializado em Flask. 
Com base no contexto da aplicação MausTratos descrito acima, 
implemente TODAS as rotas CRUD para a tabela 'usuarios' 
seguindo as especificações. Gere código pronto para produção 
com validações completas e tratamento de erros robusto."
```

---

## 📝 Informações Adicionais

**Configuração do Ambiente (via Docker Compose):**
```yaml
DATABASE_HOST: mariadb
DATABASE_PORT: 3306
DATABASE_USER: root
DATABASE_PASSWORD: 19032007
DATABASE_NAME: MausTratosDB
MEMCACHED_HOST: memcached
MEMCACHED_PORT: 11211
```

**Arquivo Docker Compose Existente**: `docker-compose.yml`
- Serviço MariaDB já configurado
- Serviço Memcached já configurado
- Volume para persistência de dados

**Como Executar Localmente:**
```bash
cd /Server
docker-compose up -d
python main.py
# Ou com Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 main:app
```

---

## 🔄 Novos Fluxos do Usuário e Sessões (Implementados)

### 1️⃣ Cadastro de Usuário Comum
- **Rota Frontend**: `/test/cadastro` (renderiza `templates/Tcc/Login/cadastro.html`)
- **Funcionamento**: Formulário estilizado com Bootstrap 5 que coleta: Nome de Usuário, E-mail e Senha. Faz disparo via Fetch (POST) para a API `/api/usuarios`.
- **Segurança**: A senha é criptografada no backend usando o algoritmo de hashing seguro `pbkdf2:sha256` da biblioteca `werkzeug.security` antes de ser salva na tabela `usuarios`.

### 2️⃣ Login Híbrido (Banco de Dados / Admin)
- **Rota Frontend**: `/test/login` (renderiza `templates/Tcc/Login/login.html`)
- **API Backend**: `/api/login` (POST)
- **Funcionamento**: 
  - Se o e-mail for `admin@sistema.com` e a senha coincidir com a chave estática do administrador, o acesso é concedido com a role `admin`.
  - Se for qualquer outro e-mail, é realizada uma consulta na tabela `usuarios` do MariaDB buscando por e-mail. A senha digitada é validada com a senha armazenada (hash) usando a função `check_password_hash`.
  - Em caso de sucesso, as variáveis de sessão `session['usuario_id']`, `session['usuario_nome']` e `session['role'] = 'user'` são definidas, redirecionando o usuário comum ao Index público.

### 3️⃣ Sistema de Sessão Convidado (Guest)
- **Implementação**: Controlado globalmente no backend através de um interceptor `@app.before_request`.
- **Funcionamento**: Sempre que um visitante não autenticado acessa o site, o sistema gera automaticamente um identificador temporário (ex: `anon#12345` a partir de um valor randômico entre 10000 e 99999) e define `session['role'] = 'guest'` e `session['usuario_nome'] = 'Visitante Anônimo'`.

### 4️⃣ Visualização Pública no Index e script `home.js`
- **Rota Frontend**: `/test` (renderiza `templates/Tcc/index.html`)
- **Funcionamento**: O arquivo `index.html` inclui dois containers dinâmicos para notícias e ONGs parceiras. Ao carregar a página (`DOMContentLoaded`), o script modular `static/Publico/home.js` faz chamadas assíncronas (Fetch GET) para `/api/noticias` e `/api/ongs`.
- **Integração com PIX**: Cada card de ONG rende uma interface com chave PIX doadora e botão de "Copiar" que salva o valor na área de transferência com retorno visual animado.

### 5️⃣ Pedido de Ajuda e Denúncia
- **Rota Frontend**: `/test/ajuda/pedir` (renderiza `templates/Tcc/Ajuda/pedir_ajuda.html`)
- **API Backend**: `/api/ajuda` (POST)
- **Funcionamento**: Permite registrar denúncias (Título, Corpo do relato e PIX de apoio).
- **Atribuição do Autor**: O backend lê a sessão ativa. Se for um visitante anônimo (`role == 'guest'`), grava o ID temporário `anon#XXXXX` na coluna `autor`. Se o usuário estiver logado (`role == 'user'`), grava o seu nome real.

### 6️⃣ Página de Leis de Maus-Tratos (Estática)
- **Rota Frontend**: `/test/leis` (renderiza `templates/Tcc/Leis/leis.html`)
- **Funcionamento**: Conteúdo informativo sobre a **Lei Sansão (Lei Federal nº 14.064/20)**, a **Lei de Crimes Ambientais (Lei nº 9.605/98)**, e canais de denúncia públicos (190 PM, DEPA, etc.).


