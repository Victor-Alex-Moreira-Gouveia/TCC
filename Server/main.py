import os
import re
import math
import time
from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import IntegrityError, DatabaseError
from pymemcache.client.base import Client
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configurações vindas do ambiente (Docker Compose)
# ---------------------------------------------------------------------------
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'mariadb'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', '19032007'),
    'database': os.getenv('DATABASE_NAME', 'MausTratosDB')
}

MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', 'memcached')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))


# ---------------------------------------------------------------------------
# Helpers de banco de dados e resposta
# ---------------------------------------------------------------------------

def get_db():
    """Retorna uma nova conexão com o MariaDB."""
    return mysql.connector.connect(**DB_CONFIG)


def success_response(data, message="Operação realizada com sucesso", status=200, pagination=None):
    """Monta uma resposta de sucesso padronizada."""
    body = {"success": True, "data": data, "message": message}
    if pagination:
        body["pagination"] = pagination
    return jsonify(body), status


def error_response(message, code="ERROR", details=None, status=400):
    """Monta uma resposta de erro padronizada."""
    body = {"success": False, "error": message, "code": code}
    if details:
        body["details"] = details
    return jsonify(body), status


def parse_pagination(args):
    """Extrai parâmetros de paginação da query string."""
    try:
        page = max(1, int(args.get('page', 1)))
        limit = max(1, min(100, int(args.get('limit', 10))))
    except (ValueError, TypeError):
        page, limit = 1, 10
    offset = (page - 1) * limit
    return page, limit, offset


def build_pagination(total, page, limit):
    """Monta o objeto de paginação."""
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if limit else 1
    }


# ---------------------------------------------------------------------------
# Validações
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
PIX_RE = re.compile(
    r'^(\d{11}|\d{14}|[^@\s]+@[^@\s]+\.[^@\s]+|\+\d{1,3}\d{10,11}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$'
)


def validate_email(email: str):
    return EMAIL_RE.match(email.strip()) is not None


def validate_pix(pix: str):
    return PIX_RE.match(pix.strip()) is not None


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_mariadb():
    try:
        conn = get_db()
        if conn.is_connected():
            conn.close()
            return True, "Conexão com MariaDB: OK"
    except Exception as e:
        return False, f"Erro MariaDB: {str(e)}"


def test_memcached():
    try:
        client = Client((MEMCACHED_HOST, MEMCACHED_PORT))
        client.set('test_key', 'funcionando')
        result = client.get('test_key')
        if result == b'funcionando':
            return True, "Conexão com Memcached: OK"
        return False, "Memcached: Falha na integridade dos dados"
    except Exception as e:
        return False, f"Erro Memcached: {str(e)}"


@app.route('/health')
def health_check():
    db_status, db_msg = test_mariadb()
    cache_status, cache_msg = test_memcached()
    status_code = 200 if db_status and cache_status else 500
    return jsonify({
        "status": "online" if status_code == 200 else "unstable",
        "checks": {"mariadb": db_msg, "memcached": cache_msg}
    }), status_code


# ---------------------------------------------------------------------------
# Páginas de teste (renderização de templates)
# ---------------------------------------------------------------------------

@app.route('/test')
def test_index():
    return render_template('Tcc/test_index.html')

@app.route('/test/usuarios')
def test_usuarios():
    return render_template('Tcc/test_usuarios.html')

@app.route('/test/noticias')
def test_noticias():
    return render_template('Tcc/test_noticias.html')

@app.route('/test/ongs')
def test_ongs():
    return render_template('Tcc/test_ongs.html')

@app.route('/test/ajuda')
def test_ajuda():
    return render_template('Tcc/test_ajuda.html')


# ===========================================================================
# CRUD — Usuarios
# ===========================================================================

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    """Lista usuários com paginação."""
    page, limit, offset = parse_pagination(request.args)
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM usuarios")
        total = cur.fetchone()['total']
        cur.execute(
            "SELECT id, nome_usuario, email FROM usuarios LIMIT %s OFFSET %s",
            (limit, offset)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/usuarios/<int:uid>', methods=['GET'])
def get_usuario(uid):
    """Busca um usuário pelo ID."""
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nome_usuario, email FROM usuarios WHERE id = %s", (uid,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    """Cria um novo usuário."""
    data = request.get_json(silent=True) or {}
    errors = {}

    nome = (data.get('nome_usuario') or '').strip()
    email = (data.get('email') or '').strip()
    senha = (data.get('senha') or '').strip()

    if not nome:
        errors['nome_usuario'] = 'Campo obrigatório'
    if not email:
        errors['email'] = 'Campo obrigatório'
    elif not validate_email(email):
        errors['email'] = 'Formato de e-mail inválido'
    if not senha:
        errors['senha'] = 'Campo obrigatório'
    elif len(senha) < 8:
        errors['senha'] = 'A senha deve ter no mínimo 8 caracteres'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    senha_hash = generate_password_hash(senha)

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
        return success_response({"id": new_id, "nome_usuario": nome, "email": email},
                                "Criado com sucesso", 201)
    except IntegrityError:
        return error_response("Email já registrado no sistema", "EMAIL_CONFLICT", status=409)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/usuarios/<int:uid>', methods=['PUT'])
def update_usuario(uid):
    """Atualiza dados de um usuário."""
    data = request.get_json(silent=True) or {}

    # Verifica existência
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nome_usuario, email FROM usuarios WHERE id = %s", (uid,))
        existing = cur.fetchone()
        if not existing:
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    updates = []
    params = []
    errors = {}

    if 'nome_usuario' in data:
        nome = (data['nome_usuario'] or '').strip()
        if not nome:
            errors['nome_usuario'] = 'Não pode ser vazio'
        else:
            updates.append("nome_usuario = %s")
            params.append(nome)

    if 'email' in data:
        email = (data['email'] or '').strip()
        if not email:
            errors['email'] = 'Não pode ser vazio'
        elif not validate_email(email):
            errors['email'] = 'Formato de e-mail inválido'
        else:
            updates.append("email = %s")
            params.append(email)

    if 'senha' in data:
        senha = (data['senha'] or '').strip()
        if len(senha) < 8:
            errors['senha'] = 'A senha deve ter no mínimo 8 caracteres'
        else:
            updates.append("senha = %s")
            params.append(generate_password_hash(senha))

    if errors:
        cur.close()
        conn.close()
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not updates:
        cur.close()
        conn.close()
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        params.append(uid)
        cur.execute(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, nome_usuario, email FROM usuarios WHERE id = %s", (uid,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return success_response(updated, "Atualizado com sucesso")
    except IntegrityError:
        return error_response("Email já registrado no sistema", "EMAIL_CONFLICT", status=409)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/usuarios/<int:uid>', methods=['DELETE'])
def delete_usuario(uid):
    """Remove um usuário."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE id = %s", (uid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        cur.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


# ===========================================================================
# CRUD — Noticias
# ===========================================================================

@app.route('/api/noticias', methods=['GET'])
def get_noticias():
    page, limit, offset = parse_pagination(request.args)
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM noticias")
        total = cur.fetchone()['total']
        cur.execute(
            "SELECT id, titulo, corpo, data_hora FROM noticias ORDER BY data_hora DESC LIMIT %s OFFSET %s",
            (limit, offset)
        )
        rows = cur.fetchall()
        # Serializar datetime para string
        for r in rows:
            if r.get('data_hora'):
                r['data_hora'] = r['data_hora'].isoformat()
        cur.close()
        conn.close()
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/noticias/<int:nid>', methods=['GET'])
def get_noticia(nid):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, titulo, corpo, data_hora FROM noticias WHERE id = %s", (nid,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        if row.get('data_hora'):
            row['data_hora'] = row['data_hora'].isoformat()
        return success_response(row)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/noticias', methods=['POST'])
def create_noticia():
    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    elif len(titulo) > 255:
        errors['titulo'] = 'Máximo 255 caracteres'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("INSERT INTO noticias (titulo, corpo) VALUES (%s, %s)", (titulo, corpo))
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT id, titulo, corpo, data_hora FROM noticias WHERE id = %s", (new_id,))
        row = cur.fetchone()
        if row.get('data_hora'):
            row['data_hora'] = row['data_hora'].isoformat()
        cur.close()
        conn.close()
        return success_response(row, "Criado com sucesso", 201)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/noticias/<int:nid>', methods=['PUT'])
def update_noticia(nid):
    data = request.get_json(silent=True) or {}
    errors = {}

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM noticias WHERE id = %s", (nid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    updates = []
    params = []

    if 'titulo' in data:
        titulo = (data['titulo'] or '').strip()
        if not titulo:
            errors['titulo'] = 'Não pode ser vazio'
        elif len(titulo) > 255:
            errors['titulo'] = 'Máximo 255 caracteres'
        else:
            updates.append("titulo = %s")
            params.append(titulo)

    if 'corpo' in data:
        corpo = (data['corpo'] or '').strip()
        if not corpo:
            errors['corpo'] = 'Não pode ser vazio'
        else:
            updates.append("corpo = %s")
            params.append(corpo)

    if errors:
        cur.close()
        conn.close()
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not updates:
        cur.close()
        conn.close()
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        params.append(nid)
        cur.execute(f"UPDATE noticias SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, titulo, corpo, data_hora FROM noticias WHERE id = %s", (nid,))
        updated = cur.fetchone()
        if updated.get('data_hora'):
            updated['data_hora'] = updated['data_hora'].isoformat()
        cur.close()
        conn.close()
        return success_response(updated, "Atualizado com sucesso")
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/noticias/<int:nid>', methods=['DELETE'])
def delete_noticia(nid):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM noticias WHERE id = %s", (nid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        cur.execute("DELETE FROM noticias WHERE id = %s", (nid,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


# ===========================================================================
# CRUD — ONGs
# ===========================================================================

@app.route('/api/ongs', methods=['GET'])
def get_ongs():
    page, limit, offset = parse_pagination(request.args)
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM ongs")
        total = cur.fetchone()['total']
        cur.execute(
            "SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs LIMIT %s OFFSET %s",
            (limit, offset)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ongs/<int:oid>', methods=['GET'])
def get_ong(oid):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs WHERE id = %s",
            (oid,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


def _validate_ong_fields(data, require_all=True):
    """Valida campos de uma ONG. Se require_all=False, valida apenas os presentes."""
    errors = {}

    nome = (data.get('nome_instituicao') or '').strip()
    endereco = (data.get('endereco_fisico') or '').strip() or None
    site = (data.get('site') or '').strip() or None
    pix = (data.get('pix_doacao') or '').strip()

    if require_all and not nome:
        errors['nome_instituicao'] = 'Campo obrigatório'
    elif nome and len(nome) > 150:
        errors['nome_instituicao'] = 'Máximo 150 caracteres'

    if require_all and not pix:
        errors['pix_doacao'] = 'Campo obrigatório'
    elif pix and not validate_pix(pix):
        errors['pix_doacao'] = 'Formato de chave PIX inválido (CPF, CNPJ, e-mail, telefone ou UUID)'

    if require_all:
        if not endereco and not site:
            errors['endereco_fisico'] = 'Ao menos endereço físico ou site deve ser preenchido'
            errors['site'] = 'Ao menos endereço físico ou site deve ser preenchido'

    return errors, nome, endereco, site, pix


@app.route('/api/ongs', methods=['POST'])
def create_ong():
    data = request.get_json(silent=True) or {}
    errors, nome, endereco, site, pix = _validate_ong_fields(data, require_all=True)

    if not errors and not endereco and not site:
        errors['endereco_fisico'] = 'Ao menos endereço físico ou site deve ser preenchido'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO ongs (nome_instituicao, endereco_fisico, site, pix_doacao) VALUES (%s, %s, %s, %s)",
            (nome, endereco, site, pix)
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute(
            "SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs WHERE id = %s",
            (new_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return success_response(row, "Criado com sucesso", 201)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ongs/<int:oid>', methods=['PUT'])
def update_ong(oid):
    data = request.get_json(silent=True) or {}

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs WHERE id = %s",
            (oid,)
        )
        existing = cur.fetchone()
        if not existing:
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    errors = {}
    updates = []
    params = []

    if 'nome_instituicao' in data:
        nome = (data['nome_instituicao'] or '').strip()
        if not nome:
            errors['nome_instituicao'] = 'Não pode ser vazio'
        elif len(nome) > 150:
            errors['nome_instituicao'] = 'Máximo 150 caracteres'
        else:
            updates.append("nome_instituicao = %s")
            params.append(nome)

    if 'pix_doacao' in data:
        pix = (data['pix_doacao'] or '').strip()
        if not pix:
            errors['pix_doacao'] = 'Não pode ser vazio'
        elif not validate_pix(pix):
            errors['pix_doacao'] = 'Formato de chave PIX inválido'
        else:
            updates.append("pix_doacao = %s")
            params.append(pix)

    if 'endereco_fisico' in data:
        updates.append("endereco_fisico = %s")
        params.append((data['endereco_fisico'] or '').strip() or None)

    if 'site' in data:
        updates.append("site = %s")
        params.append((data['site'] or '').strip() or None)

    # Valida constraint após mesclagem
    novo_endereco = data.get('endereco_fisico', existing['endereco_fisico'])
    novo_site = data.get('site', existing['site'])
    if not novo_endereco and not novo_site:
        errors['endereco_fisico'] = 'Ao menos endereço físico ou site deve ser preenchido'

    if errors:
        cur.close()
        conn.close()
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not updates:
        cur.close()
        conn.close()
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        params.append(oid)
        cur.execute(f"UPDATE ongs SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        cur.execute(
            "SELECT id, nome_instituicao, endereco_fisico, site, pix_doacao FROM ongs WHERE id = %s",
            (oid,)
        )
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return success_response(updated, "Atualizado com sucesso")
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ongs/<int:oid>', methods=['DELETE'])
def delete_ong(oid):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM ongs WHERE id = %s", (oid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        cur.execute("DELETE FROM ongs WHERE id = %s", (oid,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


# ===========================================================================
# CRUD — Ajuda
# ===========================================================================

@app.route('/api/ajuda', methods=['GET'])
def get_ajuda_list():
    page, limit, offset = parse_pagination(request.args)
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM ajuda")
        total = cur.fetchone()['total']
        cur.execute(
            "SELECT id, titulo, corpo, pix_doacao FROM ajuda LIMIT %s OFFSET %s",
            (limit, offset)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ajuda/<int:aid>', methods=['GET'])
def get_ajuda(aid):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, titulo, corpo, pix_doacao FROM ajuda WHERE id = %s", (aid,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ajuda', methods=['POST'])
def create_ajuda():
    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()
    pix = (data.get('pix_doacao') or '').strip()

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    elif len(titulo) > 255:
        errors['titulo'] = 'Máximo 255 caracteres'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'
    if not pix:
        errors['pix_doacao'] = 'Campo obrigatório'
    elif not validate_pix(pix):
        errors['pix_doacao'] = 'Formato de chave PIX inválido'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO ajuda (titulo, corpo, pix_doacao) VALUES (%s, %s, %s)",
            (titulo, corpo, pix)
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT id, titulo, corpo, pix_doacao FROM ajuda WHERE id = %s", (new_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return success_response(row, "Criado com sucesso", 201)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ajuda/<int:aid>', methods=['PUT'])
def update_ajuda(aid):
    data = request.get_json(silent=True) or {}

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM ajuda WHERE id = %s", (aid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    errors = {}
    updates = []
    params = []

    if 'titulo' in data:
        titulo = (data['titulo'] or '').strip()
        if not titulo:
            errors['titulo'] = 'Não pode ser vazio'
        elif len(titulo) > 255:
            errors['titulo'] = 'Máximo 255 caracteres'
        else:
            updates.append("titulo = %s")
            params.append(titulo)

    if 'corpo' in data:
        corpo = (data['corpo'] or '').strip()
        if not corpo:
            errors['corpo'] = 'Não pode ser vazio'
        else:
            updates.append("corpo = %s")
            params.append(corpo)

    if 'pix_doacao' in data:
        pix = (data['pix_doacao'] or '').strip()
        if not pix:
            errors['pix_doacao'] = 'Não pode ser vazio'
        elif not validate_pix(pix):
            errors['pix_doacao'] = 'Formato de chave PIX inválido'
        else:
            updates.append("pix_doacao = %s")
            params.append(pix)

    if errors:
        cur.close()
        conn.close()
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not updates:
        cur.close()
        conn.close()
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        params.append(aid)
        cur.execute(f"UPDATE ajuda SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        cur.execute("SELECT id, titulo, corpo, pix_doacao FROM ajuda WHERE id = %s", (aid,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return success_response(updated, "Atualizado com sucesso")
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@app.route('/api/ajuda/<int:aid>', methods=['DELETE'])
def delete_ajuda(aid):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM ajuda WHERE id = %s", (aid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        cur.execute("DELETE FROM ajuda WHERE id = %s", (aid,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)