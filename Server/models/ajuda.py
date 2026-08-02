from config.config import get_db
from mysql.connector import IntegrityError, DatabaseError


def count_ajuda():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM ajuda")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def list_ajuda(limit, offset):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda LIMIT %s OFFSET %s", (limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_ajuda_by_id(aid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda WHERE id = %s", (aid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def create_ajuda_db(titulo, corpo, pix, autor):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO ajuda (titulo, corpo, pix_doacao, autor) VALUES (%s, %s, %s, %s)", (titulo, corpo, pix, autor))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id
    except IntegrityError:
        raise


def update_ajuda_db(aid, updates_sql, params):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        params.append(aid)
        cur.execute(f"UPDATE ajuda SET {updates_sql} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda WHERE id = %s", (aid,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return updated
    except IntegrityError:
        raise


def delete_ajuda_db(aid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM ajuda WHERE id = %s", (aid,))
    found = cur.fetchone()
    if not found:
        cur.close()
        conn.close()
        return False
    cur.execute("DELETE FROM ajuda WHERE id = %s", (aid,))
    conn.commit()
    cur.close()
    conn.close()
    return True
