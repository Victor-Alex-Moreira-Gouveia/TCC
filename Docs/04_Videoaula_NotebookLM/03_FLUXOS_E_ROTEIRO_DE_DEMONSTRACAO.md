# Fluxos do projeto e roteiro de demonstração

## 1. Registrar uma denúncia

**O que a pessoa faz:** informa título, descrição, tipo de caso e urgência e envia o formulário.

**O que o sistema faz:** valida os campos, associa a autoria à sessão, grava o registro e prepara uma orientação inicial. Uma chave de idempotência permite encontrar o mesmo registro caso a resposta de sucesso não chegue corretamente à tela.

**Como explicar:** “O site não considera que falhou só porque a tela não conseguiu mostrar a resposta. Ele consulta o servidor com o identificador do envio para saber se o registro foi salvo, evitando pedir que a pessoa envie tudo outra vez sem necessidade.”

**Demonstração:** usar dados fictícios, enviar uma vez e mostrar a confirmação. Não provocar repetição em banco real.

## 2. Publicar e encontrar um animal

**O que a pessoa faz:** entra na conta, preenche os dados do animal perdido e publica. Quando o animal for encontrado, o autor usa a ação disponível para mudar o estado.

**O que o sistema faz:** grava a publicação com o identificador da conta que criou o anúncio. Antes de alterar o estado, o backend compara a conta ativa com a autoria registrada.

**Como explicar:** “A permissão não depende só do botão aparecer. O servidor confere quem criou o anúncio antes de aceitar a mudança.”

**Demonstração:** criar publicação com a conta de demonstração A, marcá-la como encontrada e, se possível, tentar com a conta B. Fazer isso apenas em ambiente de teste.

## 3. Curtir e comentar notícias

**O que a pessoa faz:** entra na página de notícias, curte uma notícia ou envia um comentário.

**O que o sistema faz:** associa a ação à conta, grava a alteração e atualiza a interface. A curtida é limitada a uma por pessoa para cada notícia. O administrador também pode interagir com notícias usando uma conta registrada no banco.

**Como explicar:** “A aplicação guarda quem fez cada ação e atualiza a contagem. Se a tela não mostrar o resultado imediatamente, ela pode consultar o servidor de novo.”

## 4. Sincronizar a lista de usuários

**O que o administrador faz:** pressiona “Sincronizar” na tela de gerenciamento de usuários.

**O que o sistema faz:** consulta todas as páginas da listagem fornecida pela API e atualiza a tabela apresentada.

**Como explicar:** “Esse botão atualiza a lista da tela com os dados atuais do servidor. Não sincroniza bancos diferentes nem cria uma cópia em outro lugar.”

## 5. Cache opcional

**O que o sistema faz:** tenta usar Memcached para guardar temporariamente algumas respostas de leitura. Se o cache estiver desativado ou indisponível, busca os dados diretamente no banco.

**Como explicar:** “O cache é uma memória auxiliar para acelerar consultas. O banco continua sendo o lugar permanente onde os dados ficam guardados.”

## Roteiro sugerido para videoaula de 8 a 10 minutos

### 0:00–0:45 — Abertura

- Apresente o nome do projeto.
- Diga que a aula é para pessoas sem experiência avançada em programação.
- Explique o propósito em uma frase.

### 0:45–1:45 — Problema e proposta

- Explique que relatos, notícias e pedidos para encontrar animais podem estar dispersos.
- Mostre como o projeto reúne alguns desses fluxos.
- Reforce que a plataforma não substitui canais oficiais.

### 1:45–3:00 — O que as pessoas podem fazer

- Apresente denúncia e orientação inicial.
- Mostre notícias, curtidas e comentários.
- Apresente publicações de animais perdidos e mudança para “Encontrado”.
- Mostre brevemente as áreas administrativas.

### 3:00–4:30 — Como uma ação chega ao banco

- Use o exemplo do formulário de denúncia.
- Explique navegador, servidor, API e banco com uma analogia simples.
- Evite trechos longos de código.

### 4:30–6:30 — Demonstração

- Demonstrar uma publicação de animal com dados fictícios.
- Mostrar a atualização para “Encontrado”.
- Demonstrar notícias ou o botão “Sincronizar”, explicando seu funcionamento.

### 6:30–7:45 — Termos técnicos essenciais

Explique banco de dados, API, autenticação, autorização, cache e idempotência, com exemplos do guia técnico. Priorize só os termos necessários para acompanhar a demonstração.

### 7:45–8:45 — Limites e responsabilidade

- O sistema não encaminha denúncias automaticamente.
- As orientações são iniciais e precisam de revisão profissional.
- Não há estudo que prove impacto social.
- A proteção das APIs precisa ser revisada antes de uso público.

### 8:45–9:30 — Fechamento

- Recapitule o objetivo.
- Diga o que o projeto demonstra tecnicamente.
- Cite uma possibilidade de continuidade, como avaliação com usuários ou integração oficial após autorização.

## Recomendações para quem apresenta

- Fale em frases curtas e explique siglas na primeira ocorrência.
- Prefira “programa do servidor” a “backend” e “tela que a pessoa usa” a “frontend”; introduza o termo técnico depois.
- Não prometa que as orientações resolvem uma emergência.
- Não exiba contas, telefones, denúncias ou dados pessoais reais.
- Evite dizer “está 100% seguro” ou “foi aprovado por todos os usuários”.
- Mostre uma ação por vez: primeiro o que a pessoa vê, depois o que acontece no servidor.
