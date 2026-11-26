# Limites, verificações e pontos a confirmar

Este arquivo distingue fatos implementados de resultados ainda não demonstrados.

## Fatos confirmados nos arquivos

- O sistema usa Flask/Python, SQLAlchemy e MariaDB/MySQL.
- O Compose declara aplicação, banco, Memcached opcional e phpMyAdmin.
- Há páginas e fluxos para notícias, denúncias, comentários, curtidas e publicações de animais.
- Denúncias usam chave de idempotência e têm rota de consulta de confirmação.
- O cadastro de animais exige sessão; o backend registra autoria e identificador do usuário.
- Cadastros novos de animais ficam pendentes até aprovação administrativa; anúncios existentes são preservados como aprovados na migração.
- O administrador pode aprovar uma solicitação para publicação pública ou negá-la, caso em que ela é excluída.
- A denúncia fica armazenada internamente; a tela recomenda canais conforme tipo e situação, mas não liga, não encaminha o relato a órgãos nem gera protocolo oficial.
- A leitura e a alteração de denúncias e decisões de aprovação exigem papel administrativo no backend.
- O endpoint de mudança para “Encontrado” verifica propriedade no servidor.
- A página de usuários tem botão “Sincronizar”, que recarrega a listagem paginada da API.
- O dossiê integrado relata uma execução histórica de 17 testes aprovados em 29/09/2026; o arquivo original do relatório não está disponível nesta pasta organizada.
- O arquivo de testes contém casos posteriores para denúncia idempotente, propriedade de animais e páginas administrativas.

## Evidências de teste: como apresentar sem exagerar

O Dossiê Integrado registra uma execução histórica de 17 testes aprovados em 29 de setembro de 2026 e relata verificações direcionadas posteriores. O relatório original não está disponível nesta pasta organizada; consulte `../05_Testes/LEIA-ME.md`. Esses registros não comprovam execução integral da suíte na versão final.

O registro histórico de 17 testes é anterior a alterações posteriores e não documenta execução integral de toda a suíte no estado final. Os novos casos existem no arquivo de testes, mas sua presença não prova, por si só, que todos foram aprovados na última versão. Se houver uma nova execução completa, atualize este material com data, comando e resultado reais.

## Pendência de autorização identificada

A página de gerenciamento de usuários exige perfil administrativo. As rotas CRUD de usuários ainda precisam de revisão independente: a proteção da página, sozinha, não comprova a autorização de cada endpoint. Não use dados reais nem exponha publicamente o sistema enquanto essa revisão permanecer pendente.

## Outros limites

- **Canal de denúncia:** o sistema grava relatos internamente para consulta administrativa; não os envia automaticamente à polícia, prefeitura, ONG ou serviço de emergência e não gera protocolo oficial. O encaminhamento exibido é orientação para a pessoa iniciar o contato.
- **Responsabilidade operacional:** a plataforma não realiza resgate, atendimento veterinário ou acionamento de serviços. A pessoa decide e inicia o contato com o canal indicado.
- **Orientações de urgência:** são mensagens informativas, não diagnóstico ou tratamento. Recomenda-se revisão veterinária antes de divulgação ampla.
- **Impacto:** não há estudo de campo ou métrica que demonstre aumento de resgates, redução de maus-tratos ou satisfação de usuários.
- **Acessibilidade:** não há evidência de auditoria formal ou conformidade WCAG.
- **Privacidade:** há nomes, e-mails, contatos e relatos. A existência de funcionalidades não comprova conformidade integral com a LGPD.
- **Conteúdo:** notícias e imagens de exemplo precisam de origem, crédito, data e licença confirmáveis.
- **Implantação:** há configuração local documentada; isso não comprova prontidão para tráfego público em produção.
- **Credenciais:** padrões de desenvolvimento devem ser substituídos por segredos fortes e locais antes de qualquer exposição.

## Frases seguras

- “O sistema permite registrar uma denúncia na aplicação e consultar se ela foi salva.”
- “A aplicação ajuda a organizar informações e não substitui os canais oficiais.”
- “O autor da publicação pode marcá-la como encontrada; o servidor verifica essa permissão.”
- “O relatório registra uma execução anterior de 17 testes aprovados; a versão final precisa de nova execução completa.”
- “O botão Sincronizar atualiza a lista exibida usando a API.”

## Frases a evitar

- “A denúncia foi enviada à polícia.”
- “O sistema resolve emergências veterinárias.”
- “O sistema é totalmente seguro e cumpre integralmente a LGPD.”
- “Todos os testes da versão final passaram”, sem execução registrada.
- “A ferramenta já reduziu maus-tratos ou aumentou resgates.”
- “O botão sincroniza os bancos de dados.”
