from config.config import get_db
from mysql.connector import IntegrityError, DatabaseError


def count_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM usuarios")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def list_users(limit, offset):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome_usuario, email FROM usuarios LIMIT %s OFFSET %s", (limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_usuario_by_id(uid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome_usuario, email FROM usuarios WHERE id = %s", (uid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def create_usuario(nome, email, senha_hash):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome_usuario, email, senha) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id
    except IntegrityError:
        raise


def update_usuario_db(uid, updates_sql, params):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        params.append(uid)
        cur.execute(f"UPDATE usuarios SET {updates_sql} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, nome_usuario, email FROM usuarios WHERE id = %s", (uid,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return updated
    except IntegrityError:
        raise


def delete_usuario_db(uid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE id = %s", (uid,))
    found = cur.fetchone()
    if not found:
        cur.close()
        conn.close()
        return False
    cur.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
    conn.commit()
    cur.close()
    conn.close()
    return True
