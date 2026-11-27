#!/bin/sh
set -eu

: "${MARIADB_ROOT_PASSWORD:?MARIADB_ROOT_PASSWORD ausente}"
: "${TCC_DB_ADMIN_PASSWORD:?TCC_DB_ADMIN_PASSWORD ausente}"

# Passe a senha como literal hexadecimal para que caracteres especiais não
# possam alterar a instrução SQL executada no bootstrap.
password_hex="$(printf '%s' "$TCC_DB_ADMIN_PASSWORD" | od -An -v -tx1 | tr -d ' \n')"
if [ -z "$password_hex" ]; then
    echo 'A senha do usuário administrativo do TCC não pode estar vazia.' >&2
    exit 1
fi

mariadb --protocol=socket --user=root --password="$MARIADB_ROOT_PASSWORD" <<SQL
SET @tcc_db_admin_password = CONVERT(0x${password_hex} USING utf8mb4);
SET @tcc_db_admin_create = CONCAT(
  "CREATE USER IF NOT EXISTS 'tcc_db_admin'@'%' IDENTIFIED BY ",
  QUOTE(@tcc_db_admin_password)
);
PREPARE tcc_db_admin_statement FROM @tcc_db_admin_create;
EXECUTE tcc_db_admin_statement;
DEALLOCATE PREPARE tcc_db_admin_statement;
GRANT ALL PRIVILEGES ON MausTratosDB.* TO 'tcc_db_admin'@'%';
SQL
