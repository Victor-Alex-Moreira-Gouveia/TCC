# Guia de uso do servidor do TCC

Os arquivos versionados de produção ficam em `deploy/production/`. Execute os comandos a partir da raiz do checkout usando `./deploy/production/compose.sh`; esse wrapper fixa o Compose de produção e o `.env` local da raiz. A preparação deste guia não alterou a instalação ativa do Tardis.

## 1. O que foi instalado

O projeto **Vozes que não podem gritar** roda no Tardis como uma unidade própria chamada `vozes-tcc`. O servidor pessoal continua com seu Nginx, Nextcloud, Collabora, n8n e demais serviços. O TCC tem seu próprio Nginx, aplicação Flask, MariaDB, Memcached e phpMyAdmin.

O nome do banco permanece **`MausTratosDB`**, conforme o SQL e as configurações da aplicação. O projeto não usa login nem banco de usuários do Tardis: os usuários e a conta administrativa são próprios do TCC.

No arquivo `.env`, mantenha `DATABASE_NAME=MausTratosDB`. O Compose encaminha esse valor ao aplicativo e a configuração de produção recusa outro nome.

| Parte | Função | Acesso |
|---|---|---|
| Aplicação Flask | Site, cadastro e recursos do TCC | Por meio do Nginx exclusivo |
| Nginx do TCC | Encaminha as páginas para a aplicação | Somente `127.0.0.1:18080` no host |
| MariaDB | Guarda contas, notícias, denúncias e publicações | Rede privada dos contêineres; banco `MausTratosDB` |
| Memcached | Cache interno | Rede privada dos contêineres |
| phpMyAdmin | Consulta e manutenção visual do banco | Somente `127.0.0.1:18081` no host |
| Tailscale Serve | HTTPS/TLS e acesso privado por MagicDNS | Portas Tailscale `8445` e `8446` |

O tráfego para o site passa pelo TLS do Tailscale Serve e chega às portas locais do TCC. MariaDB e Memcached não têm portas publicadas no servidor.

Essa é uma separação por contêineres, redes e volumes no mesmo Tardis. O projeto ainda compartilha o hardware, o kernel Linux e o daemon Docker do servidor; o uso de CPU, memória e disco também é compartilhado.

## 2. Como acessar

É necessário instalar e conectar o dispositivo ao **Tailscale** com uma conta autorizada na rede privada. Depois, abra:

- **Site:** <https://tardis.tail24530a.ts.net:8445>
- **Painel do banco:** <https://tardis.tail24530a.ts.net:8446>

O MagicDNS resolve o nome `tardis.tail24530a.ts.net` dentro da rede Tailscale. Os endereços não são publicados para acesso aberto pela internet.

### Primeiro login administrativo

A conta inicial do site é exclusiva do TCC. O arquivo protegido com as informações iniciais fica no servidor em:

```text
/home/vamg/Desktop/school-services/vozes-tcc/INITIAL_ADMIN_LOGIN.txt
```

Para consultá-lo pelo computador que tenha acesso SSH:

```bash
ssh vamg@192.168.2.1 'cat ~/Desktop/school-services/vozes-tcc/INITIAL_ADMIN_LOGIN.txt'
```

O arquivo e o `.env` ficam restritos ao usuário `vamg`. Não compartilhe o conteúdo em capturas de tela ou mensagens. A senha administrativa é conferida pelo próprio aplicativo através das variáveis `ROOT_EMAIL` e `ROOT_PASSWORD` do `.env`.

### Acesso ao phpMyAdmin

Na tela do phpMyAdmin, informe:

- Servidor: `mariadb`
- Usuário: `tcc_db_admin`
- Senha: valor de `TCC_DB_ADMIN_PASSWORD` no `.env` protegido da instalação
- Banco do projeto: `MausTratosDB`

O usuário `tcc_db_admin` tem privilégios de manutenção somente no banco do TCC. A aplicação usa o usuário separado `tcc_app`. A senha de administrador global do MariaDB não é usada para entrar no phpMyAdmin.

Se estiver no servidor via SSH, consulte a senha no `.env` sem copiá-la para documentos:

```bash
cd ~/Desktop/school-services/vozes-tcc
grep '^TCC_DB_ADMIN_PASSWORD=' .env
```

## 3. Verificar e operar os serviços

Entre na pasta da instalação:

```bash
cd ~/Desktop/school-services/vozes-tcc
```

Ver estado e saúde:

```bash
./deploy/production/compose.sh ps
curl -fsS http://127.0.0.1:18080/health
tailscale serve status
```

Ver os registros de execução:

```bash
./deploy/production/compose.sh logs --tail=100 app proxy mariadb phpmyadmin
```

Reiniciar o projeto sem apagar os dados:

```bash
./deploy/production/compose.sh restart
```

Aplicar uma atualização de código que já tenha sido copiada para esta pasta:

```bash
./deploy/production/compose.sh build app
./deploy/production/compose.sh up -d
./deploy/production/compose.sh ps
```

O Compose usa volumes e redes com o nome do projeto `vozes-tcc`. Não edite o nome do banco; mantenha `MausTratosDB`.

## 4. Testes automatizados

Execute os testes somente em uma instalação isolada, com banco de teste próprio. Não use o Compose de produção para isso: definir `APP_ENV=testing` não troca o banco configurado, que continua sendo `MausTratosDB`, e os testes podem gravar ou remover registros.

## 5. Backup e restauração

Criar uma cópia SQL, guardada no diretório do servidor com permissão restrita:

```bash
cd ~/Desktop/school-services/vozes-tcc
mkdir -p backups
chmod 700 backups
./deploy/production/compose.sh exec -T mariadb sh -c 'exec mariadb-dump --user=tcc_db_admin --password="$TCC_DB_ADMIN_PASSWORD" --single-transaction MausTratosDB' > "backups/MausTratosDB-$(date +%F-%H%M).sql"
chmod 600 backups/*.sql
```

Restaurar um arquivo escolhido para o banco existente (a restauração substitui dados conforme o conteúdo do SQL):

```bash
./deploy/production/compose.sh exec -T mariadb sh -c 'exec mariadb --user=tcc_db_admin --password="$TCC_DB_ADMIN_PASSWORD" MausTratosDB' < backups/ARQUIVO-ESCOLHIDO.sql
```

Substitua `ARQUIVO-ESCOLHIDO.sql` pelo nome real do backup. Guarde uma cópia fora do servidor antes de remover a instalação.

## 6. Desligar sem apagar o banco

Para parar e remover os contêineres, mantendo o volume `MausTratosDB`:

```bash
cd ~/Desktop/school-services/vozes-tcc
./deploy/production/compose.sh down
```

Para voltar a iniciar:

```bash
./deploy/production/compose.sh up -d
```

## 7. Remover definitivamente o TCC

Primeiro, faça e copie para outro lugar os backups necessários. Depois, retire apenas os dois encaminhamentos usados pelo TCC no Tailscale Serve:

```bash
sudo tailscale serve --https=8445 off
sudo tailscale serve --https=8446 off
```

Confirme com `tailscale serve status` que os endereços de `8445` e `8446` sumiram e que as entradas pessoais nas portas `443`, `8443` e `8444` continuam presentes. Então remova somente o projeto do TCC e seu volume:

```bash
cd ~/Desktop/school-services/vozes-tcc
./deploy/production/compose.sh down -v --remove-orphans
```

O `-v` apaga permanentemente o volume de dados dedicado ao projeto. Só depois de confirmar os backups e que não precisa mais dos dados, remova os arquivos da pasta `~/Desktop/school-services/vozes-tcc`.

## 8. Se algo não abrir

1. Confirme que o dispositivo está conectado ao Tailscale e autorizado na tailnet.
2. No Tardis, consulte `./deploy/production/compose.sh ps` e `tailscale serve status`.
3. Se `app` estiver reiniciando, consulte `./deploy/production/compose.sh logs --tail=100 app mariadb`.
4. Verifique se o `.env` existe e tem permissão restrita (`chmod 600 .env`). Não cole senhas em mensagens de suporte.
5. A porta local `18080` atende a aplicação; `18081` atende o phpMyAdmin; `8445` e `8446` são os acessos HTTPS do Tailscale Serve.
