# Prompt para Antigravity

Você está trabalhando no projeto Flask **Vozes que não podem gritar**, uma plataforma para denúncias de maus-tratos, pedidos de ajuda, notícias e integração com ONGs.

Implemente uma nova etapa funcional com backend e frontend experimental, preservando a organização atual do projeto (`Server/templates/`, `Server/static/css/`, `Server/static/js/`, controllers, models e services).

## Objetivo

Criar uma experiência autenticada para administração de notícias e registro de denúncias, com confirmação visual de persistência e orientação imediata para situações urgentes.

## Requisitos funcionais

### 1. Notícias administráveis

- Criar um backend para inserir, listar, editar e excluir notícias.
- Somente usuários autenticados com papel `admin` podem criar, editar ou remover notícias.
- Usuários autenticados comuns podem visualizar as notícias, mas não podem alterá-las.
- Visitantes não autenticados devem ser redirecionados para `/login` ao tentar acessar áreas protegidas.
- Validar no backend, e não apenas no frontend, o papel do usuário em cada operação de escrita.
- Criar uma interface experimental para o administrador cadastrar e editar notícias.
- Exibir mensagens de sucesso e erro após cada operação.

### 2. Remoção completa de PIX e do módulo de ONGs

- Remover completamente a funcionalidade de ONGs, pois ela foi abandonada.
- Remover as páginas, rotas, controllers, models, serviços, scripts, imagens, menus, endpoints, testes e documentação relacionados a ONGs.
- Remover o campo `pix_doacao` e qualquer campo equivalente dos formulários, templates, JavaScript, validações, payloads, models, schemas, SQL e controllers.
- Remover campos PIX das tabelas de denúncias, ONGs ou qualquer outra tabela onde ainda existam.
- Atualizar o SQL inicial (`Server/Databases/MariaDB_MauTratos.sql` e demais scripts SQL) para não criar colunas, tabelas ou referências a ONGs e PIX.
- Criar uma migração segura e compatível para bancos existentes, removendo as colunas e tabelas abandonadas somente quando confirmado que não são mais usadas.
- Considerar dependências e chaves estrangeiras antes de remover tabelas.
- Atualizar modelos ORM, serializadores, validações, controllers, serviços e respostas da API.
- Remover links de navegação, cards, menus e chamadas JavaScript das ONGs.
- Atualizar documentação, exemplos JSON, README e testes para não mencionar ONGs ou PIX.
- Fazer uma busca global no repositório por `pix`, `pix_doacao`, `ONG`, `ongs`, `ong` e nomes equivalentes.
- Não deixar referências órfãs, campos sem uso, rotas quebradas, tabelas abandonadas ou dados sendo enviados para propriedades removidas.
- Confirmar que o formulário de denúncia, o backend e o banco possuem exatamente o mesmo contrato de dados.

### 3. Autenticação obrigatória

- Somente usuários cadastrados e autenticados podem acessar o conteúdo da plataforma.
- Visitantes não autenticados podem acessar apenas as telas de login e cadastro.
- A página inicial, notícias, leis, ONGs, denúncias, comentários, curtidas e painéis devem exigir autenticação.
- Remover o acesso funcional anônimo às áreas que exigem conta.
- Usuários sem sessão devem ser direcionados para o login.
- Usuários comuns devem acessar apenas recursos permitidos para o papel `user`.
- Administradores devem acessar os painéis de gerenciamento.
- Manter a configuração compatível com execução local e Docker:
  - local/WAMP: `DATABASE_HOST=localhost`
  - Docker: `DATABASE_HOST=mariadb`
- Não fixar o host do banco de forma que impeça uma dessas duas formas de execução.

### 4. Confirmações de persistência

Após salvar, editar ou remover dados com sucesso:

- Mostrar uma notificação clara para o usuário.
- Exemplos:
  - `Notícia cadastrada com sucesso.`
  - `Notícia atualizada com sucesso.`
  - `Denúncia registrada com sucesso.`
  - `Dados removidos com sucesso.`
- A mensagem só deve aparecer como sucesso quando a API confirmar a operação no banco.
- Em caso de erro, mostrar uma mensagem de falha sem esconder o problema.
- Usar um componente visual reutilizável para alertas/toasts, com estados de sucesso, erro e aviso.
- Garantir que a mensagem seja acessível e não dependa apenas de cor.

### 5. Denúncia com orientação imediata

Ao registrar uma denúncia:

- Mostrar a confirmação de que a denúncia foi salva no banco.
- Exibir também uma orientação imediata relacionada ao nível de urgência e ao tipo de ocorrência.
- Exemplos de orientações:
  - Ferimento grave: procurar veterinário ou serviço de resgate imediatamente.
  - Atropelamento: acionar resgate veterinário, zoonoses ou polícia ambiental.
  - Envenenamento: não induzir vômito e procurar atendimento veterinário urgente.
  - Doença contagiosa: isolar o animal e contatar veterinário ou vigilância sanitária.
  - Situação em andamento com risco: acionar polícia/serviço de emergência apropriado.
- As orientações devem ser informativas e prudentes, sem substituir atendimento profissional.
- Centralizar o mapa de orientações no backend ou em um módulo de serviço/configuração, evitando regras duplicadas nos templates.
- Não exibir orientação de emergência antes de o usuário marcar ou selecionar a opção correspondente, salvo quando o risco exigir aviso imediato.

### 6. Comentários e curtidas em notícias

Preparar o sistema para interação autenticada nas notícias:

- Somente usuários cadastrados e autenticados podem curtir ou comentar.
- Visitantes devem ser redirecionados para o login ao tentar interagir.
- Cada usuário pode ter no máximo uma curtida por notícia.
- Permitir remover a própria curtida sem duplicar registros.
- Usuários podem criar comentários associados à notícia e ao autor autenticado.
- Usuários comuns podem editar ou remover apenas os próprios comentários.
- Administradores podem moderar, editar ou remover qualquer comentário.
- Exibir autor, data de criação e, quando aplicável, data de atualização.
- Validar no backend o vínculo entre sessão, comentário e usuário.
- Validar tamanho mínimo e máximo do comentário.
- Rejeitar comentários vazios, conteúdo inválido e requisições sem autenticação.
- Escapar o conteúdo dos comentários para impedir XSS.
- Criar endpoints separados e consistentes, por exemplo:
  - `GET /api/noticias/<id>/comentarios`
  - `POST /api/noticias/<id>/comentarios`
  - `PUT /api/comentarios/<id>`
  - `DELETE /api/comentarios/<id>`
  - `POST /api/noticias/<id>/curtida`
  - `DELETE /api/noticias/<id>/curtida`
- Retornar a quantidade de curtidas e comentários na resposta da notícia.
- Atualizar a interface sem recarregar a página quando for simples e seguro fazê-lo.
- Mostrar estados de carregamento, lista vazia, erro e sucesso.
- Pedir confirmação antes de remover um comentário.

Criar as entidades necessárias no banco, com chaves estrangeiras, índices e restrições para evitar curtidas duplicadas.

## Requisitos técnicos

- Seguir os padrões existentes de Flask, SQLAlchemy, Blueprints e respostas JSON.
- Reutilizar autenticação e sessão existentes quando possível.
- Manter CSS fora dos templates, usando `Server/static/css/pages.css` para a identidade visual e arquivos JS externos em `Server/static/js/`.
- Preservar o padrão visual atual: fundo roxo com efeito de patinhas, navbar conforme a página, marrom da marca e rosa de destaque.
- Não reintroduzir `Server/static/style.css`.
- Não colocar CSS ou JavaScript inline nos templates.
- Usar `url_for('static', filename=...)` para assets locais.
- Manter o `docker-compose.yml` compatível com banco local e Docker.
- Atualizar README e documentação de API/estrutura.
- Documentar claramente que todo o conteúdo e toda interação exigem usuário autenticado.
- Manter o contrato entre frontend, backend e banco sincronizado após a remoção de módulos e campos.

## Testes obrigatórios

Adicionar ou atualizar testes para verificar:

- visitante não acessa endpoints ou telas protegidas;
- usuário comum não altera notícias;
- administrador cria, edita e remove notícias;
- campos PIX não existem mais em formulários, payloads e respostas;
- não existem páginas, rotas, tabelas, models, scripts ou referências funcionais de ONGs;
- não existem colunas PIX ou tabelas abandonadas após a migração do banco;
- o SQL de instalação limpa e a migração de banco existente produzem o mesmo schema esperado;
- o formulário de denúncia, o endpoint correspondente e o model usam os mesmos campos;
- nenhuma requisição envia campos removidos ou desconhecidos;
- mensagens de sucesso só aparecem após resposta positiva do backend;
- denúncia salva retorna confirmação e orientação correspondente;
- usuário não autenticado não acessa páginas, comentários ou curtidas;
- usuário autenticado pode curtir uma notícia apenas uma vez;
- usuário pode criar, editar e remover o próprio comentário;
- usuário não pode editar ou remover comentário de outra pessoa;
- administrador pode moderar comentários;
- tentativa de comentário com HTML malicioso não gera XSS;
- contagem de curtidas permanece correta após repetir ou desfazer a ação;
- mensagens de erro são exibidas quando a persistência falha;
- execução permanece compatível com Docker e com banco local configurado por `.env`.

## Critérios de aceite

Considere a tarefa concluída somente quando:

1. O backend bloquear operações não autorizadas mesmo que sejam chamadas diretamente pela API.
2. O frontend experimental permitir ao admin gerenciar notícias de ponta a ponta.
3. Não houver referências funcionais ou documentais a PIX.
4. Usuários não autenticados forem encaminhados para login nas áreas protegidas.
5. As confirmações visuais refletirem o resultado real da persistência.
6. Toda denúncia registrada exibir confirmação e orientação imediata adequada.
7. CSS e JavaScript permanecerem separados dos templates.
8. Os testes automatizados e as validações de sintaxe passarem.
9. A configuração `DATABASE_HOST` continuar selecionável pelo `.env`, sem quebrar execução local ou Docker.
10. Comentários e curtidas funcionarem somente para usuários autenticados e respeitarem as permissões definidas.
11. ONGs e PIX estiverem removidos de forma consistente do frontend, backend, banco, documentação e testes.
12. Uma busca global não encontrar referências funcionais a módulos ou campos removidos.

Antes de editar, faça uma leitura breve das rotas, controllers, models, templates, scripts e testes relacionados. Faça mudanças pequenas e verificáveis, sem reescrever módulos não envolvidos.
