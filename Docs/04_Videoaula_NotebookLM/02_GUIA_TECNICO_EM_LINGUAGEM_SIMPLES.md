# Como o sistema funciona — guia técnico sem jargão

Este guia explica os componentes do projeto com comparações simples. As analogias ajudam a começar, mas não descrevem todos os detalhes da implementação.

## O caminho de uma ação no site

Imagine alguém preenchendo o formulário de denúncia:

1. **Tela do site:** é o balcão onde a pessoa preenche as informações.
2. **JavaScript no navegador:** é o mensageiro que envia os dados e atualiza a tela.
3. **Servidor Flask:** é a equipe que recebe o pedido, confere os campos e aplica as regras.
4. **Banco MariaDB:** é o arquivo organizado onde o registro fica guardado.
5. **Resposta:** o servidor informa se deu certo; a tela apresenta a confirmação.

**Pessoa → navegador → servidor → banco de dados → resposta na tela**

## Glossário

| Termo | Explicação simples | Exemplo no projeto |
|---|---|---|
| Aplicação web | Programa aberto pelo navegador que conversa com um servidor. | Páginas de notícias e de animais. |
| Frontend | Parte que aparece e responde no navegador. | Formulários, botões, cores e mensagens. |
| Backend | Parte executada no servidor que valida regras e acessa dados. | Login, gravação de denúncia e verificação de autoria. |
| Servidor | Programa que recebe solicitações e devolve páginas ou dados. | Flask atende o site e a API. |
| API | Endereços e regras para a tela pedir dados ao servidor; pense em um balcão com pedidos definidos. | Uma tela pede notícias ou envia uma denúncia. |
| Rota/endpoint | Endereço do servidor que realiza uma operação específica. | Rota que procura uma denúncia pelo identificador de envio. |
| Banco de dados | Arquivo organizado em tabelas para guardar e localizar informações. | MariaDB guarda usuários, notícias e denúncias. |
| Tabela | Conjunto de registros de um mesmo tipo, parecido com uma planilha com regras. | Usuários têm nome, e-mail e hash da senha. |
| Banco relacional | Banco com tabelas que se relacionam por identificadores. | Comentários guardam o identificador da notícia e de quem comentou. |
| SQLAlchemy/ORM | Tradutor entre objetos Python e registros nas tabelas do banco. | Ajuda a salvar um objeto de denúncia como uma linha. |
| CRUD | Criar, consultar, atualizar e excluir dados. | Operações usadas na gestão de notícias ou usuários. |
| Autenticação | Confirmar quem entrou no sistema. | Conferir e-mail e senha no login. |
| Autorização | Decidir o que aquela conta pode fazer. | Verificar no servidor quem pode alterar uma publicação. |
| Sessão | Lembrança temporária de que a pessoa entrou na conta. | Permite associar a ação à conta autenticada. |
| Hash de senha | Representação protegida usada para conferir uma senha sem guardar o texto original. | O sistema usa uma função de hash para senhas. |
| Chave de idempotência | Identificador que reconhece uma repetição do mesmo pedido; como número técnico de protocolo para evitar gravar duas vezes. | O navegador consulta se uma denúncia com aquela chave já foi salva. |
| JSON | Formato organizado de dados trocados entre programas. | O formulário envia os campos da denúncia. |
| Cache | Memória temporária que pode acelerar algumas consultas. | Memcached pode guardar resultados de notícias por pouco tempo. |
| Fallback | Caminho alternativo usado se um componente opcional falhar. | Se o cache não responder, consulta-se o MariaDB. |
| Docker Compose | Ferramenta que inicia vários serviços juntos usando uma configuração. | Inicia servidor, banco e serviços auxiliares em contêineres. |
| Contêiner | Ambiente isolado que reúne um programa e suas dependências. | Aplicação e banco rodam como serviços separados. |
| WampServer | Pacote local que pode fornecer banco MySQL/MariaDB e ferramentas de administração. | Pode hospedar o banco enquanto Flask serve o site. |
| phpMyAdmin | Interface visual para consultar e administrar o banco. | Ajuda a inspecionar tabelas; não substitui o servidor Flask. |
| Teste de integração | Teste que confere se partes diferentes funcionam juntas. | Envia uma requisição e confirma a persistência no banco. |
| Teste de autorização | Confirma que uma conta sem permissão recebe bloqueio. | Outra pessoa não deve mudar o estado do anúncio alheio. |
| Interface responsiva | Interface que ajusta o layout a diferentes tamanhos de tela. | Reorganiza colunas em celular e computador. |
| Contraste | Diferença visual entre texto e fundo que facilita a leitura. | Títulos e controles precisam continuar visíveis sobre o fundo roxo. |
| Acessibilidade | Práticas para que pessoas com diferentes capacidades consigam usar o sistema. | Teclado, foco visível, descrição de imagens e rótulos claros. |
| LGPD | Lei brasileira sobre tratamento de dados pessoais. | Nomes, e-mails e contatos exigem tratamento cuidadoso. |

## Três comparações úteis

### Site e servidor

O navegador é como o balcão de atendimento. O servidor é a equipe que recebe o pedido e aplica as regras. Um formulário pode estar bonito, mas o pedido só foi gravado quando o servidor e o banco confirmam a operação.

### Banco e cache

O banco é o arquivo permanente. O cache é uma memória auxiliar e temporária que pode acelerar algumas consultas. Se o cache não estiver disponível, o banco continua sendo a fonte dos dados.

### Autenticação e autorização

Autenticação responde “quem entrou?”. Autorização responde “o que essa conta pode fazer?”. Estar conectado não deve permitir alterar a publicação de outra pessoa.

## Tecnologias em uma frase

- **Python e Flask:** recebem pedidos e executam regras no servidor.
- **HTML/Jinja2, CSS e JavaScript:** montam páginas e respondem às ações no navegador.
- **SQLAlchemy e MariaDB/MySQL:** organizam e armazenam informações em tabelas relacionadas.
- **Docker Compose:** inicia os serviços locais necessários.
- **Memcached:** cache opcional; se não funcionar, a aplicação pode consultar o banco.
- **pytest e requests:** apoiam testes automatizados dos fluxos.

## Segurança e privacidade em linguagem simples

O servidor precisa conferir as permissões mesmo que a tela esconda botões. O sistema também deve proteger senhas, manter segredos fora do código e tratar nomes, e-mails, contatos e relatos com cuidado. Estar conectado não significa que toda ação esteja autorizada.
