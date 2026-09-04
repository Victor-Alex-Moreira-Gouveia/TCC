# Plano de implementação: recuperação de senha

## 1. Objetivo

Adicionar um fluxo seguro para que um usuário cadastrado solicite a redefinição da senha por e-mail, sem revelar se o endereço existe e sem armazenar tokens em texto puro.

Fluxo esperado:

1. Usuário acessa `/recuperar-senha`.
2. Informa o e-mail cadastrado.
3. Backend responde sempre com uma mensagem neutra.
4. Se o usuário existir, um token temporário é criado e enviado por e-mail.
5. Usuário acessa `/redefinir-senha?token=...`.
6. Informa e confirma a nova senha.
7. Backend valida o token, atualiza o hash da senha e invalida o token.
8. Usuário volta para `/login`.

## 2. Viabilidade

### Viável com a arquitetura atual

- Flask já centraliza as rotas em `main.py` e nos Blueprints de `controllers/`.
- Usuários já estão mapeados pelo SQLAlchemy em `models/usuarios.py`.
- A senha já é armazenada com `generate_password_hash` e validada com `check_password_hash`.
- O MariaDB já possui persistência e o projeto já executa sincronização inicial do ORM.
- O frontend usa templates Jinja2 e JavaScript com `fetch`, o mesmo padrão que pode ser usado nas novas telas.

### Dependência externa necessária

O envio real exige um servidor SMTP ou um serviço de e-mail. O desenvolvimento pode começar com um adaptador que registra o link no log, mas produção deve usar SMTP configurado por variáveis de ambiente.

Memcached não deve ser usado como único armazenamento do token, pois o fluxo precisa continuar seguro e previsível mesmo com reinicialização do cache. O token deve ficar no MariaDB, armazenado somente como hash.

## 3. Estrutura proposta

```text
Server/
├── config/config.py
│   └── configura SMTP, validade e limite de solicitações
├── controllers/
│   └── autenticacao.py
│       └── telas e endpoints de recuperação
├── models/
│   ├── usuarios.py
│   │   └── busca do usuário e atualização do hash
│   └── recuperacao_senha.py
│       └── entidade e operações dos tokens
├── templates/Tcc/Login/
│   ├── recuperar_senha.html
│   └── redefinir_senha.html
├── static/Login/
│   └── script_recuperar_senha.js
└── test_recuperacao_senha.py
```

Se o projeto crescer, a lógica de geração, consumo e envio pode ser extraída para `Server/services/recuperacao_senha.py`. O controller deve continuar responsável apenas por HTTP e validação de entrada.

## 4. Modelo de dados

Adicionar uma tabela `tokens_recuperacao`:

```sql
CREATE TABLE tokens_recuperacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expira_em DATETIME NOT NULL,
    usado_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tentativas INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_token_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,
    INDEX idx_token_expiracao (expira_em),
    INDEX idx_token_usuario (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Regras do token

- Gerar com `secrets.token_urlsafe(32)` ou mais.
- Nunca salvar o token original no banco.
- Salvar `sha256(token)` em `token_hash`.
- Validade sugerida: 30 minutos.
- Aceitar apenas token não usado e não expirado.
- Marcar `usado_em` no mesmo fluxo que altera a senha.
- Invalidar tokens anteriores do mesmo usuário ao criar um novo.
- Remover tokens expirados periodicamente ou durante novas solicitações.
- Não colocar e-mail ou senha dentro do token.

## 5. Configuração por ambiente

Adicionar ao `.env.example`, sem valores secretos reais:

```dotenv
APP_PUBLIC_URL=http://localhost:8080
PASSWORD_RESET_TOKEN_MINUTES=30
PASSWORD_RESET_RATE_LIMIT_MINUTES=15

SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true
```

No Docker, `APP_PUBLIC_URL` deve apontar para a URL acessível pelo navegador. No Wamp, o host do banco continua sendo `localhost`, enquanto no Compose é `mariadb`.

Não usar credenciais SMTP de exemplo no repositório. Em produção, preferir secrets do ambiente.

## 6. Rotas e contrato HTTP

### Páginas

| Método | Rota | Ação |
|---|---|---|
| GET | `/recuperar-senha` | Exibe o formulário de solicitação |
| GET | `/redefinir-senha` | Exibe o formulário com token |

### API

| Método | Rota | Corpo |
|---|---|---|
| POST | `/api/recuperar-senha` | `{"email":"usuario@exemplo.com"}` |
| POST | `/api/redefinir-senha` | `{"token":"...","senha":"...","confirmar_senha":"..."}` |

Resposta neutra para solicitação:

```json
{
  "success": true,
  "message": "Se o e-mail estiver cadastrado, enviaremos as instruções."
}
```

Essa resposta deve ser igual para e-mail existente, inexistente ou com formato válido que não encontre usuário. Isso evita enumeração de contas.

Resposta de redefinição bem-sucedida:

```json
{
  "success": true,
  "message": "Senha redefinida com sucesso."
}
```

Token inválido, expirado ou usado deve retornar erro genérico, sem informar qual condição ocorreu.

## 7. Frontend

### `recuperar_senha.html`

Deve conter:

- campo de e-mail;
- botão de envio;
- mensagem neutra de resultado;
- link para `/login`;
- carregamento do CSS global e do JavaScript com `url_for()`.

Exemplo de envio:

```javascript
const response = await fetch('/api/recuperar-senha', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        email: document.getElementById('email').value.trim()
    })
});
const data = await response.json();
mensagem.textContent = data.message;
```

### `redefinir_senha.html`

Deve conter:

- nova senha;
- confirmação da senha;
- token obtido da query string;
- validação de igualdade no navegador;
- mensagem de sucesso ou erro;
- redirecionamento para `/login` após sucesso.

O JavaScript pode ler o token assim:

```javascript
const token = new URLSearchParams(window.location.search).get('token');
```

A validação do navegador é apenas uma melhoria de UX. O backend deve repetir todas as validações.

## 8. Backend e integração com o ORM

### Model

Criar a classe `TokenRecuperacao` com `Mapped` e `mapped_column`, seguindo o padrão de `models/ajuda.py`:

- `usuario_id`;
- `token_hash`;
- `expira_em`;
- `usado_em`;
- `criado_em`;
- `tentativas`.

Adicionar métodos para:

1. invalidar tokens antigos;
2. criar token;
3. buscar token válido por hash;
4. marcar token como usado;
5. atualizar o hash da senha do usuário.

### Controller

O controller deve:

1. aceitar JSON com `request.get_json(silent=True)`;
2. validar e normalizar o e-mail;
3. aplicar limite de solicitações;
4. consultar o usuário sem expor o resultado;
5. criar e enviar o token apenas quando necessário;
6. responder com o formato padrão do projeto;
7. validar token, senha e confirmação no endpoint de redefinição;
8. fazer commit atômico da senha e do consumo do token.

Não usar `except Exception` amplo para esconder falhas. Erros de banco e envio devem ser registrados de acordo com o padrão da aplicação e tratados sem revelar dados ao cliente.

## 9. E-mail

Criar uma pequena abstração, por exemplo:

```python
def enviar_email_recuperacao(destinatario: str, link: str) -> None:
    ...
```

Implementações previstas:

- desenvolvimento: logger controlado para visualizar o link;
- produção: SMTP com TLS;
- testes: fake sender injetável, sem enviar e-mail real.

O link deve ser montado com `APP_PUBLIC_URL` e conter somente o token original no fragmento de URL ou query string. O servidor recebe o token, calcula seu hash e compara com o banco.

## 10. Segurança obrigatória

- Resposta neutra para impedir enumeração de usuários.
- Token criptograficamente aleatório.
- Hash do token no banco.
- Token de uso único e validade curta.
- Limite por e-mail e por IP.
- Senha com no mínimo 8 caracteres, igual ao cadastro atual.
- Rejeitar senha e confirmação diferentes.
- Invalidar sessões existentes após troca de senha, se o mecanismo de sessão for ampliado.
- Nunca registrar senha ou token original em logs.
- Não enviar token em resposta de API.
- Usar HTTPS em produção.
- Configurar `FLASK_SECRET_KEY` fora do código.
- Escapar conteúdo apresentado no frontend.

## 11. Migração e compatibilidade

1. Atualizar `Server/Databases/MariaDB_MauTratos.sql` para instalações novas.
2. Adicionar uma rotina idempotente em `config/config.py` ou, preferencialmente, uma migração versionada para instalações existentes.
3. Testar em MariaDB do Docker.
4. Testar em MySQL/MariaDB do Wamp com o banco já criado.
5. Não apagar a tabela `usuarios` nem alterar hashes existentes.

Para a primeira versão, uma migração idempotente pode criar a tabela se ela não existir. Quando houver mais alterações futuras, adotar Alembic para evitar que `create_all()` seja usado como sistema completo de migrações.

## 12. Plano por fases

### Fase 1 - Preparação

- [ ] Criar branch `feature/recuperar-senha`.
- [ ] Definir SMTP, URL pública, validade e limites.
- [ ] Confirmar política de senha existente.
- [ ] Escolher logger em desenvolvimento e SMTP em produção.

### Fase 2 - Banco e ORM

- [ ] Criar `TokenRecuperacao`.
- [ ] Adicionar tabela ao SQL de inicialização.
- [ ] Implementar migração compatível com bancos existentes.
- [ ] Testar criação, expiração, uso único e remoção por usuário.

### Fase 3 - Serviço e controllers

- [ ] Implementar geração e hash de tokens.
- [ ] Implementar envio de e-mail por adaptador.
- [ ] Criar `autenticacao_bp` ou adicionar as rotas ao controller de autenticação.
- [ ] Implementar respostas neutras e tratamento de erros.
- [ ] Implementar limite de solicitações.

### Fase 4 - Templates

- [ ] Criar `recuperar_senha.html`.
- [ ] Criar `redefinir_senha.html`.
- [ ] Criar JavaScript específico.
- [ ] Adicionar link “Esqueci minha senha” à tela de login.
- [ ] Conferir `url_for`, IDs HTML e payload JSON.

### Fase 5 - Testes

- [ ] Solicitação com e-mail existente.
- [ ] Solicitação com e-mail inexistente, sem diferença na resposta.
- [ ] E-mail inválido.
- [ ] Token válido.
- [ ] Token expirado.
- [ ] Token já usado.
- [ ] Token adulterado.
- [ ] Senhas diferentes.
- [ ] Senha curta.
- [ ] Token anterior invalidado.
- [ ] Falha do SMTP sem expor detalhes.
- [ ] Regressão do login e dos 48 testes existentes.

### Fase 6 - Validação operacional

```bash
docker compose up -d --build
curl -i http://localhost:8080/recuperar-senha
curl -i http://localhost:8080/health
docker compose exec server pytest -q test_crud.py test_recuperacao_senha.py
```

No Wamp:

1. criar o banco `MausTratosDB` uma única vez;
2. configurar `.env` com `DATABASE_HOST=localhost`;
3. executar a migração da tabela de tokens;
4. iniciar o servidor Flask;
5. testar o fluxo com um SMTP de desenvolvimento ou logger.

## 13. Critérios de conclusão

O recurso estará pronto quando:

- as duas telas funcionarem no navegador;
- o link de recuperação aparecer na tela de login;
- nenhum endpoint revelar se um e-mail existe;
- tokens expirados/usados/adulterados forem rejeitados;
- a nova senha for salva com hash;
- o token original não for salvo nem registrado;
- Docker e Wamp forem compatíveis;
- a API e o ORM tiverem os mesmos nomes e tipos;
- os testes novos e os testes existentes passarem;
- a documentação de configuração SMTP estiver atualizada.

