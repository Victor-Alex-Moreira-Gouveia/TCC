# Visão técnica - Vozes que não podem gritar

## Arquitetura atual

A aplicação usa Flask como camada HTTP, Gunicorn como servidor de produção e uma organização MVC adaptada:

- `controllers/`: Blueprints, validação de entrada e respostas HTTP.
- `models/`: entidades SQLAlchemy e operações de persistência.
- `config/`: carregamento do `.env`, engine e fábrica de sessões.
- `templates/` e `static/`: interface Jinja2, JavaScript e CSS.
- `main.py`: criação da aplicação e registro dos Blueprints.
- `wsgi.py`: exportação da aplicação para o Gunicorn.

Blueprints registrados:

- `usuarios_bp`
- `noticias_bp`
- `ongs_bp`
- `ajuda_bp`

## Persistência e ORM

O SQLAlchemy usa `mysql+pymysql` para conectar ao MariaDB. A classe declarativa está em `models/base.py`; as entidades estão em:

- `models/usuarios.py` - `Usuario`
- `models/noticias.py` - `Noticia`
- `models/ongs.py` - `Ong`
- `models/ajuda.py` - `Ajuda`

As sessões são criadas por `SessionLocal` e obtidas por `get_db()`. A aplicação executa `Base.metadata.create_all()` no bootstrap e garante a compatibilidade da tabela `ajuda` com bancos criados anteriormente.

## Modelo `ajuda`

Campos persistidos:

| Campo | Tipo | Obrigatório | Origem |
|---|---|---|---|
| `id` | inteiro auto incremento | sim | banco |
| `titulo` | `VARCHAR(255)` | sim | formulário |
| `corpo` | `TEXT` | sim | formulário |
| `pix_doacao` | `VARCHAR(100)` | sim | formulário |
| `tipo_denuncia` | `VARCHAR(80)` | sim | formulário, com default |
| `nivel_urgencia` | `VARCHAR(80)` | sim | formulário, com default |
| `autor` | `VARCHAR(150)` | sim | sessão/backend |

## Configuração

O `.env` deve existir na raiz, ser baseado em `.env.example` e permanecer fora do Git. Dentro do Compose, o host do banco é `mariadb`, a porta interna é `3306` e o banco é `MausTratosDB`.

## Execução e verificação

```bash
docker compose up -d --build
curl http://localhost:8080/health
docker compose exec server pytest -q test_crud.py
```

O health check valida MariaDB com SQLAlchemy (`SELECT 1` e `SELECT VERSION()`) e Memcached com uma operação de escrita/leitura. A validação atual retorna HTTP 200 e 48 testes aprovados.

## Passo a passo para adicionar um novo template/site

Use esta checklist sempre que criar uma nova página. Um template só fica acessível quando a view, a rota, os assets e os links estão conectados.

### 1. Defina o fluxo da página

Antes de editar arquivos, registre:

- URL que será acessada, por exemplo `/leis` ou `/ongs`.
- Quem pode acessar: público, usuário autenticado ou administrador.
- Se a página apenas exibe conteúdo ou também consulta/altera dados.
- Quais campos serão enviados e qual endpoint de API será utilizado.

### 2. Crie o template no diretório correto

Crie o arquivo dentro de `Server/templates/Tcc/`, agrupado pelo domínio:

```text
Server/templates/Tcc/
└── MeuDominio/
    └── minha_pagina.html
```

No HTML:

- mantenha `lang="pt-BR"` e o viewport;
- carregue a identidade visual com `url_for('static', filename='css/pages.css')`;
- carregue scripts com `url_for('static', filename='MeuDominio/script.js')`;
- use `url_for()` para links e rotas, em vez de caminhos relativos;
- use IDs únicos nos campos que serão acessados pelo JavaScript;
- adicione `required`, limites e textos de validação quando aplicável;
- evite colocar credenciais, URLs de banco ou regras de persistência no template.

Exemplo mínimo de template público:

```html
<!-- Server/templates/Tcc/Noticias/minha_noticia.html -->
<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/pages.css') }}">
    <title>{{ titulo }}</title>
</head>
<body>
    <h1>{{ titulo }}</h1>
    <p>{{ texto }}</p>
    <a href="{{ url_for('test_index') }}">Voltar ao início</a>
</body>
</html>
```

O `{{ titulo }}` e o `{{ texto }}` são valores enviados pela rota. Se a página não precisar de dados, o conteúdo pode ser escrito diretamente no HTML.

### 3. Adicione a rota Flask

Para uma página simples, registre a rota em `Server/main.py`:

```python
@app.route('/minha-pagina', methods=['GET'])
def minha_pagina():
    return render_template('Tcc/MeuDominio/minha_pagina.html')
```

Exemplo passando dados para o template:

```python
@app.route('/sobre')
def sobre():
    return render_template(
        'Tcc/Sobre/sobre.html',
        titulo='Sobre o projeto',
        texto='Esta página apresenta o objetivo da plataforma.',
    )
```

Se a página tiver API própria, crie ou atualize um Blueprint em `Server/controllers/` e registre-o no `main.py`. Mantenha a regra de negócio fora do template.

### 4. Implemente os assets

Coloque JavaScript, CSS e imagens nos diretórios de `Server/static/`. No JavaScript:

- confirme que os IDs do HTML são exatamente os mesmos usados no script;
- envie JSON com nomes de campos iguais aos esperados pelo controller e pelo ORM;
- trate respostas de sucesso e erro (`success`, `data`, `error`, `details`);
- trate erros de rede sem esconder falhas do servidor;
- escape valores antes de inseri-los em HTML;
- não duplique listeners nem funções globais já existentes.

Exemplo de formulário simples com envio para uma API:

```html
<form id="formContato">
    <input id="nome" required>
    <textarea id="mensagem" required></textarea>
    <button type="submit">Enviar</button>
</form>
<p id="resultado"></p>
<script>
document.getElementById('formContato').addEventListener('submit', async (event) => {
    event.preventDefault();
    const resultado = document.getElementById('resultado');
    const payload = {
        nome: document.getElementById('nome').value.trim(),
        mensagem: document.getElementById('mensagem').value.trim()
    };

    const response = await fetch('/api/contato', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    const data = await response.json();
    resultado.textContent = response.ok ? 'Enviado com sucesso.' : (data.error || 'Falha ao enviar.');
});
</script>
```

Neste exemplo, os nomes `nome` e `mensagem` são o contrato: o HTML, o JavaScript e o controller precisam usar exatamente as mesmas chaves.

### 5. Conecte a navegação

Adicione o link para a nova página nos locais adequados, normalmente:

- `Server/templates/Tcc/index.html`;
- menu/navbar das páginas relacionadas;
- redirecionamentos e links de retorno;
- scripts que carregam conteúdo dinâmico.

Teste a URL diretamente mesmo que ela ainda não esteja no menu.

### 6. Conecte a API, se necessário

Para uma página que salva dados:

1. defina o contrato JSON;
2. valide os campos no controller;
3. crie ou ajuste o model SQLAlchemy em `Server/models/`;
4. confira se os nomes, tipos, tamanhos e campos obrigatórios coincidem com o SQL;
5. atualize `Server/Databases/MariaDB_MauTratos.sql`;
6. crie compatibilidade para bancos já existentes quando houver novas colunas;
7. retorne o formato padrão da API.

No formulário de ajuda, por exemplo, `titulo`, `corpo`, `pix_doacao`, `tipo_denuncia` e `nivel_urgencia` precisam coincidir entre HTML, JavaScript, controller, ORM e tabela MariaDB.

Exemplo de payload correto para a API de ajuda:

```json
{
  "titulo": "Cão encontrado ferido",
  "corpo": "Animal precisa de atendimento na Rua Flores.",
  "pix_doacao": "apoio@pix.com",
  "tipo_denuncia": "Animal doméstico",
  "nivel_urgencia": "Ferimento grave"
}
```

O `autor` não deve ser digitado no formulário: ele é preenchido pelo backend a partir da sessão. Se você adicionar um novo campo, por exemplo `localidade`, atualize todos os pontos:

```text
HTML (id="localidade")
  -> JavaScript (localidade: ...)
  -> controller (data.get("localidade"))
  -> ORM (localidade = mapped_column(...))
  -> SQL/migração (ALTER TABLE ... ADD COLUMN localidade ...)
  -> resposta da API e testes
```

Exemplo de teste rápido do payload usando `curl`:

```bash
curl -X POST http://localhost:8080/api/ajuda \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Teste","corpo":"Relato de teste","pix_doacao":"teste@pix.com","tipo_denuncia":"Animal doméstico","nivel_urgencia":"Ferimento grave"}'
```

### 7. Revise permissões e sessão

Se a página for restrita, valide a role no backend. Nunca dependa apenas de esconder um link no frontend. Confira também:

- comportamento para visitante (`guest`);
- comportamento para usuário (`user`);
- comportamento para administrador (`admin`);
- destino correto quando o acesso for negado;
- dados da sessão usados para preencher `autor` ou identificar o usuário.

### 8. Teste antes de considerar concluído

Com os containers ativos:

```bash
docker compose up -d --build
curl -i http://localhost:8080/minha-pagina
curl -i http://localhost:8080/health
docker compose exec server pytest -q test_crud.py
```

Para páginas com formulário, teste manualmente:

- carregamento sem erros no navegador;
- envio válido;
- campos vazios e valores inválidos;
- resposta exibida ao usuário;
- atualização da listagem após salvar;
- edição e exclusão, se existirem;
- acesso em uma nova sessão anônima;
- layout em tela pequena.

### 9. Checklist final

- [ ] Template criado em `Server/templates/Tcc/`.
- [ ] Rota Flask criada e testada diretamente.
- [ ] Links e botão de retorno atualizados.
- [ ] CSS, JavaScript e imagens carregados com `url_for()`.
- [ ] IDs HTML e seletores JavaScript conferidos.
- [ ] Payload JSON conferido com controller e ORM.
- [ ] Schema SQL/ORM atualizado, se houver persistência.
- [ ] Regras de sessão e permissão conferidas.
- [ ] Tratamento de erro implementado.
- [ ] Health check e suíte de testes executados.

## Operação e segurança

- Não versionar `.env`, credenciais ou volumes locais.
- Usar secrets do ambiente de implantação em produção.
- `docker compose down -v` é destrutivo para os dados locais do MariaDB.
- O login administrativo atual é híbrido e possui credenciais definidas no código de autenticação; isso deve ser substituído por configuração segura antes de produção.
