# Prompt para gerar a videoaula no NotebookLM

Adicione como fontes os materiais de `01` a `04` desta pasta, o dossiê acadêmico `../01_TCC/Projeto_Vozes_que_nao_podem_gritar_Dossie_Integrado.docx` e o modelo atual `../02_Banco_de_Dados/DatabaseModel.md`. Se usar capturas de tela, escolha imagens atualizadas com dados fictícios. Depois, copie o prompt abaixo para a instrução de geração.

---

## Prompt copiável

Crie uma videoaula em português brasileiro sobre o projeto “Vozes que não podem gritar”, usando somente as fontes fornecidas.

### Público e tom

O público é formado por pessoas curiosas sobre o projeto, estudantes e membros da comunidade. Não são desenvolvedores avançados. Explique com calma, em linguagem simples, exemplos cotidianos e frases curtas. Não presuma experiência prévia em programação. Use tom acolhedor, informativo e respeitoso; não trate maus-tratos de forma sensacionalista.

### Objetivo

Ao final, quem assistir deve conseguir explicar:

1. qual necessidade o projeto procura atender;
2. o que uma pessoa pode fazer no site;
3. como uma informação sai do formulário, chega ao servidor e fica registrada no banco;
4. o significado de alguns termos técnicos básicos;
5. os limites do sistema e por que ele não substitui canais oficiais.

### Estrutura narrativa

Organize a aula em aproximadamente 8 a 10 minutos:

1. **Abertura:** apresente o nome e o propósito do projeto em uma frase.
2. **Contexto:** explique que relatos, notícias e pedidos sobre animais podem ficar dispersos e que o sistema reúne alguns desses fluxos.
3. **Experiência de uso:** descreva cadastro/login, denúncia e confirmação, notícias com comentários e curtidas e publicação de animal perdido com mudança de estado para “Encontrado”.
4. **Como funciona por trás:** use uma analogia simples para explicar navegador, tela do site, servidor, API e banco de dados.
5. **Termos técnicos:** explique, no máximo, oito conceitos. Priorize frontend, backend, API, banco de dados, autenticação, autorização, cache e idempotência. Dê uma definição curta e um exemplo do projeto para cada conceito.
6. **Modelo de dados:** mostre como usuários e notícias se relacionam com comentários e curtidas. Explique que a publicação de animal guarda o identificador do autor como associação lógica sem chave estrangeira no banco e que o identificador pode ser nulo em registros antigos. Não invente uma tabela de ONGs nem uma coluna de papel administrativo.
7. **Demonstração:** descreva uma sequência de tela fácil de acompanhar, usando somente dados fictícios.
8. **Limites e responsabilidade:** deixe claro que o sistema grava informações na aplicação, não envia automaticamente denúncias às autoridades, não substitui atendimento veterinário e ainda precisa de revisão da proteção das APIs antes de uso público.
9. **Fechamento:** resuma o valor do projeto e cite uma possibilidade de continuidade, sem afirmar resultados sociais que as fontes não comprovam.

### Regras de precisão

- Use as fontes como base factual. Não invente funcionalidades, integrações, resultados, usuários, organizações parceiras, métricas ou aprovações.
- Diferencie o que está implementado do que é recomendação ou trabalho futuro.
- Não diga que a plataforma protocola denúncias em órgãos oficiais.
- Não diga que a ferramenta diagnostica ou trata animais.
- Não afirme que houve pesquisa com usuários, auditoria de acessibilidade ou avaliação de impacto sem uma fonte que comprove isso.
- Informe que o relatório existente documenta 17 testes aprovados em 29/09/2026, mas é anterior a mudanças posteriores. Não diga que toda a suíte atual passou sem uma execução final registrada.
- Mencione diretamente a pendência de autorização no CRUD da API de usuários. A página administrativa protegida não resolve por si só esse ponto.
- Não leia em voz alta nomes de arquivos, rotas, comandos, código, senhas ou valores de configuração.
- Não mostre dados reais de usuários. Use exemplos fictícios.

### Recursos visuais e didáticos

- Se houver fontes visuais disponíveis, mostre a tela de início, o formulário de denúncia, uma publicação de animal e páginas administrativas.
- Se apresentar o modelo de dados, use `DatabaseModel.md`; os diagramas em `../02_Banco_de_Dados/Versoes_anteriores/` incluem entidades que não existem no esquema atual.
- Use um diagrama simples com setas: pessoa → navegador → servidor → banco de dados → confirmação.
- Ao falar de cache, mostre uma memória temporária auxiliar ao lado do banco permanente.
- Evite telas cheias de texto ou código. Destaque uma ideia por cena.
- Inclua legendas, texto grande, cores contrastantes e exemplos que façam sentido sem áudio.

### Entrega desejada

Produza uma explicação com abertura, desenvolvimento, demonstração, resumo final e transições naturais. Defina cada sigla na primeira ocorrência. Se as fontes não responderem a uma pergunta, diga que a informação não está documentada em vez de completar por suposição.
