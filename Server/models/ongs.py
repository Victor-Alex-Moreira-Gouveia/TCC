from config.config import get_db
from mysql.connector import IntegrityError, DatabaseError


def count_ongs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM ongs")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def list_ongs(limit, offset):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs LIMIT %s OFFSET %s", (limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_ong_by_id(oid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs WHERE id = %s", (oid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def create_ong(nome, endereco, site, pix):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO ongs (nome_instituicao, endereco_fisico, site, pix_doacao) VALUES (%s, %s, %s, %s)", (nome, endereco, site, pix))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id
    except IntegrityError:
        raise


def update_ong_db(oid, updates_sql, params):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        params.append(oid)
        cur.execute(f"UPDATE ongs SET {updates_sql} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs WHERE id = %s", (oid,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return updated
    except IntegrityError:
        raise


def delete_ong_db(oid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM ongs WHERE id = %s", (oid,))
    found = cur.fetchone()
    if not found:
        cur.close()
        conn.close()
        return False
    cur.execute("DELETE FROM ongs WHERE id = %s", (oid,))
    conn.commit()
    cur.close()
    conn.close()
    return True
