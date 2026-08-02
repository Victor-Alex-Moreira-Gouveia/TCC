TCC - Web Site Maus Tratos ao Animais — Visão Técnica

Este arquivo é a versão técnica atualizada do InfoProject, focada em arquitetura, configuração e passos práticos para evolução.

1) Resumo técnico
- Aplicação: Flask + Gunicorn
- Banco: MariaDB
- Cache: Memcached
- Containerização: Docker Compose
- Gestão de configuração: .env carregado por Server/config/config.py (python-dotenv)
- Testes: pytest (rodados dentro do container do servidor)

2) Estrutura recomendada (MVC adaptado)
Server/
  config/        # configurações centrais (config.py)
  controllers/   # Blueprints (rotas)
  models/        # Funções/DAO de acesso ao banco
  services/      # Lógica de negócio
  templates/     # Jinja2 templates
  static/        # JS/CSS/Imagens
  main.py        # bootstrap (registro de blueprints)

3) Configuração central (.env)
- Edite .env na raiz do projeto para alterar credenciais e hosts.
- docker-compose.yml utiliza env_file: .env para consistência em containers.

4) Arquivos sensíveis a ignorar (.gitignore criado)
- .env
- mariadb_data/
- venv/, .venv/
- __pycache__/, *.pyc
- .pytest_cache/
- .vscode/, .idea/
- *.log, .DS_Store

5) Plano de migração incremental
- Criar Blueprints em controllers/ e mover handlers do main.py
- Implementar models/<dominio>.py com queries e mapping para dicionários
- Testar suite a cada migração

6) Observações operacionais
- Não commitar .env em repositórios públicos
- Para produção, usar secrets da plataforma
- Testes executados: `docker compose exec server pytest -q` (48 passed atualmente)

7) Proposta de próximos passos (automatizáveis)
- Migrar `usuarios` para controllers/models (prova de conceito)
- Remover segredos do índice do Git e deixar somente .env.example
- Gerar script de bootstrap para criar usuário admin a partir de variáveis de ambiente


Se aprovar, prossigo com a migração do domínio `usuarios` (controllers + models) e atualizo os testes e as imports automaticamente, mantendo a suíte de testes passando.
