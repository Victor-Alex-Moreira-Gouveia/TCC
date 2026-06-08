# TCC - Web Site Maus Tratos ao Animais

## 📋 Contexto do Projeto

### Sobre o Sistema
- **Nome do Projeto**: Vozes que não podem gritar
- **Objetivo**: Plataforma web de denúncia, documentação e combate a maus-tratos com integração com ONGs e sistema de contribuições
- **Tipo**: Aplicação web com backend robusto e banco de dados relacional

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
│   ├── Index.html                  
│   ├── style.css                   
│   ├── test_index.html             
│   ├── test_usuarios.html          
│   ├── test_noticias.html          
│   ├── test_ongs.html              
│   └── test_ajuda.html             
└── test_crud.py                     
```

---

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

- ✅ Modelagem correta de banco de dados relacional
- ✅ Implementação de API RESTful seguindo boas práticas
- ✅ Validação e tratamento robusto de erros
- ✅ Testes automatizados e qualidade de código
- ✅ Documentação clara de endpoints e funcionalidades
- ✅ Containerização com Docker para reprodutibilidade

---

## ✅ Checklist de Conclusão

- [x] Todas 4 rotas CRUD totalmente implementadas
- [x] Validações em todos os campos críticos
- [x] Tratamento de erros com HTTP codes apropriados
- [x] Páginas HTML de teste funcionais
- [ ] Frontend das páginas web
- [x] Testes automatizados passando 100%
- [x] Código bem documentado com docstrings
- [x] Sem warnings ao executar testes
- [x] Funciona perfeitamente com Docker
- [ ] Pronto para apresentação final do TCC

---

**Gerado em**: 05 de junho de 2026  
**Projeto**: TCC - Vozes que não podem gritar
**Desenvolvedores:**
  - Victor Alex Moreira Gouveia
  - Taila Fonseca de Souza
  - Sophia Santos Castellini
  - Julia de Souza Alves
  - Marilisy Barbosa Oliveira
