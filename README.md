# TCC - Web Site Maus Tratos ao Animais

## 📋 Contexto do Projeto

### Sobre o Sistema
- **Nome do Projeto**: Vozes que não podem gritar
- **Objetivo**: Plataforma web de denúncia, documentação e combate a maus-tratos com integração com ONGs e sistema de contribuições
- **Tipo**: Aplicação web com backend robusto, banco de dados relacional e cache para melhor desempenho

## 🛠️ Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Linguagem** | Python 3.x |
| **Framework Backend** | Flask |
| **Servidor de Aplicação** | Gunicorn |
| **Banco de Dados** | MariaDB |
| **Cache** | Memcached |
| **Containerização** | Docker + Docker Compose |
| **Conexão com Banco** | mysql-connector-python |
| **Conexão com Cache** | pymemcache |

---

## 📁 Estrutura de Arquivos

```
/Server/
├── main.py                          
├── requirements.txt                 
├── Dockerfile                       
├── start.sh                         
├── Databases/
│   ├── MariaDB_MauTratos.sql       
│   └── MySQL_MauTratos.sql         
├── templates/Tcc/
│   ├── Ajuda/
│   ├── Login/
│   ├── Leis/
│   ├── Noticias/
│   ├── ONGs/
│   ├── Usuario/
│   └── index.html
└── test_crud.py                     
```

---

## ▶️ Como Executar com Docker

1. A partir da raiz do projeto, execute o comando abaixo:

```bash
docker compose up --build
```

2. Após a inicialização, a aplicação estará disponível em:

- http://localhost:8080/
- http://localhost:8080/health

3. Para encerrar os containers, utilize:

```bash
docker compose down
```

---

## 🧩 Funcionalidades e Serviços

- Backend Flask rodando na porta 8080
- Banco de dados MariaDB disponível na porta 3307
- Cache Memcached disponível na porta 11211
- O banco é inicializado automaticamente com o script SQL presente em `Server/Databases/MariaDB_MauTratos.sql`
- O backend só sobe após o banco e o cache estarem prontos para uso
- O endpoint `/health` verifica a conexão com MariaDB e Memcached

---

## ⚙️ Configuração do Ambiente

O Docker Compose já disponibiliza as variáveis de ambiente necessárias para a aplicação, incluindo:

- `DATABASE_HOST=mariadb`
- `DATABASE_PORT=3306`
- `DATABASE_USER=root`
- `DATABASE_PASSWORD=19032007`
- `DATABASE_NAME=MausTratosDB`
- `MEMCACHED_HOST=memcached`
- `MEMCACHED_PORT=11211`

---

## 📌 Observações

- O projeto contém templates HTML para as páginas de teste e navegação do sistema
- A estrutura de containerização foi ajustada para garantir uma inicialização mais estável e previsível
- O README foi reorganizado para refletir melhor o estado atual do projeto

---

**Gerado em**: 05 de junho de 2026  
**Projeto**: TCC - Vozes que não podem gritar
**Desenvolvedores:**
  - Victor Alex Moreira Gouveia
  - Taila Fonseca de Souza
  - Sophia Santos Castellini
  - Julia de Souza Alves
  - Marilisy Barbosa Oliveira
