Padrão MVC (adaptado para este projeto Flask)

Objetivo
- Deixar a base de código mais organizada, com responsabilidades separadas: controllers (rotas e handlers), models (acesso/representação do banco), services/repositories (lógica de negócio) e views (templates).

Estrutura recomendada (já criada como skeleton):

/Server/
├── config/                # arquivo(s) de configuração centralizados (.env lidos aqui)
│   └── config.py
├── controllers/           # rotas e handlers (mapeamento das APIs)
│   └── __init__.py
├── models/                # acessos ao banco, mapeamentos e helpers SQL
│   └── __init__.py
├── services/              # regras de negócio e integração entre models e controllers
│   └── __init__.py
├── templates/             # views (HTML)
├── static/                # estáticos (JS, CSS, imagens)
├── main.py                # ponto de entrada (registra blueprints e configura app)

Como migrar (passos sugeridos):
1. Criar blueprints por área (ex: users, noticias, ongs, ajuda) em controllers/.
2. Mover funções de CRUD do main.py para controllers/<area>.py e expor como Blueprint.
3. Implementar modelos simples (funções de acesso ao banco) em models/<area>.py que retornem dicionários.
4. Implementar services para lógica que envolva múltiplos modelos (opcional).
5. Registrar blueprints em main.py (mantendo main.py apenas como ponto de bootstrap e registro).

Notas:
- As variáveis de configuração são centralizadas em Server/config/config.py e carregam .env automaticamente. Isso evita espalhar valores fixos no código.
- Antes de mover grandes blocos, garantir cobertura de testes e rodá-los constantemente (pytest já configurado).

