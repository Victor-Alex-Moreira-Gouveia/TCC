# Pendências de validação

## Windows 11 com WAMP Server e MySQL

- [ ] Executar a aplicação usando `.env.local` derivado de `.env.local.example`, com o MySQL do WAMP ativo e Memcached desativado.
- [ ] Confirmar a migração sobre uma base local existente: anúncios anteriores continuam públicos; novas solicitações ficam pendentes; a coluna de situação da denúncia é criada.
- [ ] Executar a suíte de integração a partir de `Server/` contra a aplicação local e registrar comando, data, versão do MySQL e resultado.
- [ ] Conferir no navegador Windows a fila administrativa, aprovação/negação, mensagens pós-cadastro e os links `tel:`/canais oficiais.
- [ ] Confirmar que o sistema continua funcionando sem Memcached.

Esta verificação ainda não foi executada porque o computador Windows/WAMP não está disponível neste momento. Preencher os resultados quando esse ambiente puder ser acessado; não tratar a validação Docker como substituta.

## Execução Docker

- [x] Executar a suíte em containers Docker com banco de teste isolado.
- [x] Validar a migração de registros legados: solicitações antigas de animais foram mantidas como aprovadas e denúncias antigas receberam a situação padrão `relato_passado`.

**Execução registrada em 25/11/2026:**

- Comando da suíte: `docker compose -p tcc-vqnp-test -f docker-compose.yml -f /tmp/tcc-docker-test/compose.override.yml exec -T server pytest -q test_crud.py` (executado a partir da raiz do projeto).
- Resultado: `25 passed`.
- A migração foi verificada em um banco MariaDB descartável, criado só para esta execução. O banco/volume habitual do projeto não foi usado.
- A verificação Windows 11/WAMP/MySQL permanece pendente e deve ser registrada separadamente quando esse computador estiver disponível.
