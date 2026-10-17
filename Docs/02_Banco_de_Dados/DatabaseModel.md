# Modelo de dados — Vozes que não podem gritar

> **Modelo de referência atual, em Mermaid.** Este documento foi conferido com os modelos SQLAlchemy, os scripts MariaDB/MySQL e as migrações presentes no repositório em 17 de outubro de 2026. O arquivo pode ser visualizado em leitores Markdown que suportam Mermaid, incluindo o GitHub.
>
> Os arquivos `Versoes_anteriores/DatabaseModel_Versao_Anterior.png` e `Versoes_anteriores/DatabaseModel_Versao_Anterior.drawio` são materiais antigos: mostram uma tabela de ONGs que não existe no esquema atual e não contemplam comentários, curtidas, imagens ou a autoria dos anúncios de animais. Foram mantidos como histórico; este arquivo passa a ser a referência do modelo.

## 1. Diagrama entidade-relacionamento

O diagrama mostra como as tabelas de comentários e curtidas se relacionam por chaves estrangeiras com notícias e usuários. A autoria dos anúncios de animais é registrada por uma associação lógica, descrita separadamente abaixo, pois no esquema atual não existe chave estrangeira para esse vínculo.

~~~mermaid
erDiagram
    USUARIOS {
        INTEGER id PK
        VARCHAR nome_usuario
        VARCHAR email UK
        VARCHAR senha
    }

    NOTICIAS {
        INTEGER id PK
        VARCHAR titulo
        TEXT corpo
        LONGBLOB imagem_blob
        VARCHAR imagem_mime
        DATETIME data_hora
    }

    COMENTARIOS_NOTICIAS {
        INTEGER id PK
        INTEGER noticia_id FK
        INTEGER usuario_id FK
        VARCHAR autor_nome
        TEXT texto
        DATETIME data_criacao
        DATETIME data_atualizacao
    }

    CURTIDAS_NOTICIAS {
        INTEGER id PK
        INTEGER noticia_id FK
        INTEGER usuario_id FK
        DATETIME data_hora
    }

    AJUDA {
        INTEGER id PK
        VARCHAR titulo
        TEXT corpo
        VARCHAR tipo_denuncia
        VARCHAR nivel_urgencia
        VARCHAR autor
        VARCHAR idempotency_key UK
    }

    ANIMAIS_PERDIDOS {
        INTEGER id PK
        VARCHAR nome
        VARCHAR especie
        VARCHAR sexo
        TEXT descricao
        VARCHAR local
        DATE data_ocorrido
        VARCHAR contato
        LONGBLOB imagem_blob
        VARCHAR imagem_mime
        VARCHAR status
        VARCHAR autor
        VARCHAR usuario_id
        DATETIME criado_em
    }

    NOTICIAS ||--o{ COMENTARIOS_NOTICIAS : recebe
    USUARIOS ||--o{ COMENTARIOS_NOTICIAS : escreve
    NOTICIAS ||--o{ CURTIDAS_NOTICIAS : recebe
    USUARIOS ||--o{ CURTIDAS_NOTICIAS : registra
~~~

### Leitura da cardinalidade

- Uma notícia pode ter zero ou muitos comentários; cada comentário pertence a uma notícia.
- Um usuário pode escrever zero ou muitos comentários; cada comentário está vinculado a um usuário.
- Uma notícia pode ter zero ou muitas curtidas; cada curtida pertence a uma notícia.
- Um usuário pode registrar zero ou muitas curtidas em notícias diferentes.
- A combinação de notícia e usuário em `curtidas_noticias` é única. Portanto, cada usuário pode curtir uma notícia no máximo uma vez.
- Comentários e curtidas usam chaves estrangeiras com exclusão em cascata: ao excluir notícia ou usuário, os registros dependentes correspondentes são removidos pelo banco.

## 2. Associação de autoria das publicações de animais

O backend grava o identificador da conta em `animais_perdidos.usuario_id` e confere essa informação ao processar a mudança do status para “Encontrado”. No banco, porém, esse campo é `VARCHAR(64)`, pode ser nulo e não declara `FOREIGN KEY` para `usuarios.id`. A linha abaixo representa a intenção funcional, não uma restrição relacional aplicada pelo banco.

~~~mermaid
flowchart LR
    U["USUARIOS.id — INTEGER, chave primária"]
    A["ANIMAIS_PERDIDOS.usuario_id — VARCHAR(64), nulo permitido e indexado"]
    U -. "associação lógica de autoria; não é FOREIGN KEY" .-> A
    A --> R["O servidor compara os identificadores antes de permitir marcar como Encontrado"]
~~~

Registros antigos podem ter `usuario_id` nulo. A regra de mudança de estado só pode reconhecer como proprietário uma publicação que esteja associada à conta autenticada.

## 3. Esquema das tabelas

Os tipos abaixo refletem os scripts SQL e os modelos ORM. `NULL` indica que o campo é opcional; quando não indicado, o campo é obrigatório. Valores `DEFAULT` são os padrões declarados no esquema ou no model.

### 3.1 `usuarios`

| Campo | Tipo | Regra | Descrição |
|---|---|---|---|
| `id` | INT | PK, auto incremento | Identificador da conta. |
| `nome_usuario` | VARCHAR(100) | NOT NULL | Nome de exibição. |
| `email` | VARCHAR(150) | NOT NULL, UNIQUE | E-mail usado para identificar a conta. |
| `senha` | VARCHAR(255) | NOT NULL | O aplicativo grava o hash da senha, não o texto original. |

O papel `admin` ou `user` não é uma coluna desta tabela. O papel é mantido na sessão da aplicação; a conta raiz é configurada por variáveis de ambiente.

### 3.2 `noticias`

| Campo | Tipo | Regra | Descrição |
|---|---|---|---|
| `id` | INT | PK, auto incremento | Identificador da notícia. |
| `titulo` | VARCHAR(255) | NOT NULL | Título. |
| `corpo` | TEXT | NOT NULL | Texto principal. |
| `imagem_blob` | LONGBLOB | NULL | Conteúdo binário opcional da imagem. |
| `imagem_mime` | VARCHAR(100) | NULL | Tipo MIME da imagem, quando presente. |
| `data_hora` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Data e hora do registro. |

O esquema atual não armazena um identificador de autor da notícia.

### 3.3 `comentarios_noticias`

| Campo | Tipo | Regra | Descrição |
|---|---|---|---|
| `id` | INT | PK, auto incremento | Identificador do comentário. |
| `noticia_id` | INT | NOT NULL, FK → `noticias.id`, ON DELETE CASCADE | Notícia comentada. |
| `usuario_id` | INT | NOT NULL, FK → `usuarios.id`, ON DELETE CASCADE | Conta que publicou o comentário. |
| `autor_nome` | VARCHAR(150) | NOT NULL | Nome apresentado junto ao comentário. |
| `texto` | TEXT | NOT NULL | Conteúdo do comentário. |
| `data_criacao` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Momento da criação. |
| `data_atualizacao` | DATETIME | NULL, atualizado pelo ORM em alterações | Momento da última edição, quando houver. |

### 3.4 `curtidas_noticias`

| Campo | Tipo | Regra | Descrição |
|---|---|---|---|
| `id` | INT | PK, auto incremento | Identificador do registro de curtida. |
| `noticia_id` | INT | NOT NULL, FK → `noticias.id`, ON DELETE CASCADE | Notícia curtida. |
| `usuario_id` | INT | NOT NULL, FK → `usuarios.id`, ON DELETE CASCADE | Conta que curtiu. |
| `data_hora` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Momento da curtida. |

Há uma restrição UNIQUE composta em (`noticia_id`, `usuario_id`), que impede duplicar a curtida da mesma conta na mesma notícia.

### 3.5 `ajuda`

| Campo | Tipo | Regra | Descrição |
|---|---|---|---|
| `id` | INT | PK, auto incremento | Identificador do registro de ajuda/denúncia. |
| `titulo` | VARCHAR(255) | NOT NULL | Resumo do caso. |
| `corpo` | TEXT | NOT NULL | Relato enviado pela pessoa. |
| `tipo_denuncia` | VARCHAR(80) | NOT NULL, DEFAULT “Animal doméstico” | Tipo de caso informado. |
| `nivel_urgencia` | VARCHAR(80) | NOT NULL, DEFAULT “Não informado” | Urgência selecionada. |
| `autor` | VARCHAR(150) | NOT NULL, DEFAULT “anon” | Nome textual associado ao registro. |
| `idempotency_key` | VARCHAR(36) | NULL, UNIQUE | Chave que permite reconhecer um reenvio do mesmo formulário. |

`autor` é texto; a tabela não contém `usuario_id` nem chave estrangeira para `usuarios`. O esquema não declara data de criação para esta entidade.

### 3.6 `animais_perdidos`

| Campo | Tipo | Regra | Descrição |
|---|---|---|---|
| `id` | INT | PK, auto incremento | Identificador da publicação. |
| `nome` | VARCHAR(120) | NOT NULL | Nome do animal ou identificação usada no anúncio. |
| `especie` | VARCHAR(40) | NOT NULL | Espécie. |
| `sexo` | VARCHAR(30) | NOT NULL, DEFAULT “Não informado” | Sexo informado. |
| `descricao` | TEXT | NOT NULL | Características e detalhes. |
| `local` | VARCHAR(255) | NOT NULL | Local associado ao desaparecimento/ocorrência. |
| `data_ocorrido` | DATE | NOT NULL | Data informada no cadastro. |
| `contato` | VARCHAR(180) | NOT NULL | Meio de contato fornecido para o anúncio. |
| `imagem_blob` | LONGBLOB | NULL | Imagem opcional armazenada no banco. |
| `imagem_mime` | VARCHAR(100) | NULL | Tipo MIME da imagem, quando presente. |
| `status` | VARCHAR(30) | NOT NULL, DEFAULT “Perdido” | Situação, por exemplo “Perdido” ou “Encontrado”. |
| `autor` | VARCHAR(150) | NOT NULL, DEFAULT “Visitante” | Nome textual apresentado como autor. |
| `usuario_id` | VARCHAR(64) | NULL, INDEX | Identificador da conta criadora; associação lógica sem FK. |
| `criado_em` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Momento de criação da publicação. |

O backend define `autor` e `usuario_id` a partir da sessão autenticada ao criar uma publicação. O endpoint de mudança de status também compara o identificador da sessão com `usuario_id`.

## 4. Fluxos de gravação e leitura

### 4.1 Denúncia e prevenção de duplicidade

~~~mermaid
flowchart TD
    P["Pessoa preenche o formulário"]
    N["Navegador envia os campos e uma chave única de envio"]
    C["Controller Flask valida os dados e identifica a autoria"]
    M["Model consulta ou cria o registro em ajuda"]
    D[("Banco relacional")]
    J["API responde com confirmação e orientação inicial"]
    F["Se a resposta não puder ser interpretada, o navegador consulta a confirmação pela mesma chave"]
    P --> N --> C --> M --> D --> J
    J -. "problema ao atualizar a tela" .-> F
    F --> M
~~~

O uso da mesma chave permite recuperar uma denúncia já persistida em vez de inserir outra cópia. Isso não significa que o registro seja enviado a um órgão público.

### 4.2 Marcar um animal como encontrado

~~~mermaid
flowchart TD
    A["Usuário autenticado solicita status Encontrado"]
    V["Controller obtém o identificador da sessão"]
    Q["Banco verifica id da publicação, usuario_id e status atual"]
    S{"A publicação pertence à conta e ainda está Perdido?"}
    U["Atualiza o status para Encontrado"]
    X["Recusa a alteração: sem permissão, não encontrado ou já atualizado"]
    A --> V --> Q --> S
    S -->|Sim| U
    S -->|Não| X
~~~

O controle ocorre no backend. Esconder ou mostrar um botão na interface não substitui esta validação.

## 5. Objetos que não são entidades de negócio

- **Memcached:** cache opcional fora do banco relacional. Não aparece no diagrama ER.
- **Sessão e papel administrativo:** mantidos pela aplicação, não como tabela de papéis no esquema atual.
- **`vw_estatisticas_tabelas`:** view de monitoramento definida no script MariaDB; consulta metadados de tabelas e não representa uma entidade de domínio.
- **ONGs:** não há tabela de ONGs no esquema atual. A migração remove uma tabela legada `ongs`, portanto ela não deve aparecer no modelo atual.

## 6. Notas sobre o estado do esquema

1. Os scripts MariaDB/MySQL declaram as tabelas de usuários, notícias, ajuda, animais, comentários e curtidas. O ORM declara os mesmos modelos e campos principais.
2. `init_db_schema` cria tabelas que ainda não existam. As migrações próprias tratam colunas adicionadas em versões anteriores, incluindo a chave de idempotência e o identificador de proprietário do anúncio de animal.
3. Em bancos já existentes, o estado pode depender do histórico de migração. Para uma entrega acadêmica reproduzível, compare este modelo com uma instalação limpa e com uma base atualizada.
4. O identificador de proprietário em `animais_perdidos` não é uma FK; isso foi representado explicitamente para não sugerir uma restrição que o banco não aplica.
5. A conta de administrador raiz depende de configuração e sessão. Não há coluna `role` em `usuarios`.

## 7. Referências internas

- Modelos ORM: `Server/models/usuarios.py`, `Server/models/noticias.py`, `Server/models/ajuda.py` e `Server/models/animais_perdidos.py`.
- Scripts SQL: `Server/Databases/MariaDB_MauTratos.sql` e `Server/Databases/MySQL_MauTratos.sql`.
- Migrações: `Server/config/config.py`.
- Regras de propriedade: `Server/controllers/animais_perdidos.py`.
- Testes: `Server/test_crud.py`.

