# Vozes que não podem gritar — visão geral para o público

## Em uma frase

**Vozes que não podem gritar** é um site de apoio à proteção animal que reúne notícias, registros de denúncias, orientações iniciais e publicações de animais perdidos.

## Que necessidade o projeto atende?

Informações sobre animais em situação de risco, notícias de proteção animal e pedidos para encontrar um animal podem ficar espalhadas por lugares diferentes. O projeto organiza alguns desses conteúdos em um só site para que as pessoas possam registrar informações, acompanhar publicações e colaborar com a comunidade.

## O que o site permite fazer?

- Criar uma conta e entrar no sistema.
- Registrar um relato sobre uma suspeita de maus-tratos.
- Receber confirmação de que o relato foi salvo e uma orientação inicial ligada à urgência escolhida.
- Ler notícias sobre proteção animal.
- Curtir e comentar notícias depois de entrar na conta.
- Cadastrar um animal perdido com descrição, local, contato e foto opcional.
- Marcar como “Encontrado” uma publicação de animal perdido feita pela própria conta.
- Administrar notícias, usuários, denúncias e publicações por meio de páginas destinadas à administração.
- Atualizar a tabela de usuários com o botão “Sincronizar”.

O botão “Sincronizar” recarrega a lista da tela usando os dados que o servidor devolve. Não copia dados entre bancos nem envia a lista para outro serviço.

## Quem usa?

- **Visitante:** acessa páginas permitidas e pode iniciar cadastro ou login.
- **Usuário:** usa recursos que exigem conta, como comentar ou publicar um animal perdido.
- **Administrador:** cuida do conteúdo e das telas administrativas.

Os controles de acesso precisam ser aplicados pelo servidor. Não diga que todas as operações administrativas estão protegidas até que cada rota da API tenha sido revisada.

## Como funciona o registro de denúncia?

1. A pessoa preenche título, descrição, tipo de caso e urgência.
2. O site envia o formulário ao servidor.
3. O servidor verifica os campos e grava a denúncia no banco de dados.
4. O site informa que o registro foi realizado e apresenta a orientação inicial correspondente.
5. Se o navegador não conseguir mostrar a resposta normal, consulta o servidor usando o mesmo identificador de envio antes de sugerir nova tentativa.

Esse identificador funciona como um número de referência técnico para o envio. Ajuda o sistema a reconhecer uma repetição e reduz o risco de duplicar o registro.

## O que o site não faz

- Não envia a denúncia automaticamente à polícia, prefeitura, ONG ou órgão público.
- Não gera boletim de ocorrência ou protocolo oficial.
- Não confirma se um relato é verdadeiro nem decide se houve crime.
- Não substitui veterinário, serviço de emergência, resgate ou autoridade competente.
- Não comprova que o sistema reduziu maus-tratos ou aumentou resgates; isso exigiria avaliação específica.

## Mensagem sugerida

“Este projeto reúne ferramentas digitais para apoiar a comunidade na organização de informações sobre proteção animal. Ele permite registrar relatos, consultar notícias e divulgar animais perdidos. O sistema confirma quando salva um registro, mas não substitui os canais oficiais nem o atendimento profissional.”
