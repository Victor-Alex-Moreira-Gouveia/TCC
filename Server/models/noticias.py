from config.config import get_db
from mysql.connector import IntegrityError, DatabaseError


def count_noticias():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM noticias")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def list_noticias(limit, offset):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, titulo, corpo, data_hora FROM noticias ORDER BY data_hora DESC LIMIT %s OFFSET %s", (limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_noticia_by_id(nid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, titulo, corpo, data_hora FROM noticias WHERE id = %s", (nid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def create_noticia(titulo, corpo):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO noticias (titulo, corpo) VALUES (%s, %s)", (titulo, corpo))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id
    except IntegrityError:
        raise


def update_noticia_db(nid, updates_sql, params):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        params.append(nid)
        cur.execute(f"UPDATE noticias SET {updates_sql} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, titulo, corpo, data_hora FROM noticias WHERE id = %s", (nid,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return updated
    except IntegrityError:
        raise


def delete_noticia_db(nid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM noticias WHERE id = %s", (nid,))
    found = cur.fetchone()
    if not found:
        cur.close()
        conn.close()
        return False
    cur.execute("DELETE FROM noticias WHERE id = %s", (nid,))
    conn.commit()
    cur.close()
    conn.close()
    return True
