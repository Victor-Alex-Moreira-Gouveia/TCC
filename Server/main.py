import os
import re
import math
import time
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import mysql.connector
from mysql.connector import IntegrityError, DatabaseError
from pymemcache.client.base import Client
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = "admin1234@"

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

# Gerador de usuário temporário automático para visitantes anônimos
@app.before_request
def garantir_usuario_temporario():
    # Se a pessoa não está logada (nem como admin, nem como comum)
    if 'usuario_id' not in session:
        numero_aleatorio = random.randint(10000, 99999)
        session['usuario_id'] = f"anon#{numero_aleatorio}"
        session['usuario_nome'] = "Visitante Anônimo"
        session['role'] = "guest" # Convidado/Anônimo

# ---------------------------------------------------------------------------
# Helpers de banco de dados e resposta
# ---------------------------------------------------------------------------

def get_db():
    """Retorna uma nova conexão com o MariaDB."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db_schema():
    """Garante a estrutura correta do banco de dados (coluna autor em ajuda)."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SHOW COLUMNS FROM ajuda LIKE 'autor'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE ajuda ADD COLUMN autor VARCHAR(150) NOT NULL DEFAULT 'anon'")
            conn.commit()
            print("Migração automática: Coluna 'autor' inserida na tabela 'ajuda'.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Alerta de migração (inicialização rápida): {e}")

# Executa migração de startup
init_db_schema()


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
# Páginas do Sistema (Renderização de templates com travas de segurança)
# ---------------------------------------------------------------------------

# Página Inicial (Qualquer um pode acessar, até o anônimo/guest)
@app.route('/test')
def test_index():
    return render_template('Tcc/index.html')

# Painel de Usuários - APENAS ADMIN
@app.route('/test/usuarios')
def test_usuarios():
    if session.get('role') != 'admin':
        return redirect('/test/login')
    return render_template('Tcc/Usuario/usuarios.html')

# Painel de Notícias - APENAS ADMIN
@app.route('/test/noticias')
def test_noticias():
    if session.get('role') != 'admin':
        return redirect('/test/login')
    return render_template('Tcc/Noticias/noticias.html')

# Painel de ONGs - APENAS ADMIN
@app.route('/test/ongs')
def test_ongs():
    if session.get('role') != 'admin':
        return redirect('/test/login')
    return render_template('Tcc/ONGs/ongs.html')

# Painel de Ajuda - APENAS ADMIN
@app.route('/test/ajuda')
def test_ajuda():
    if session.get('role') != 'admin':
        return redirect('/test/login')
    return render_template('Tcc/Ajuda/ajuda.html')

# Solicitação Pública de Ajuda (Qualquer um pode acessar)
@app.route('/test/ajuda/pedir', methods=['GET'])
def public_pedir_ajuda():
    return render_template('Tcc/Ajuda/pedir_ajuda.html')

# Página Estática de Leis (Qualquer um pode acessar)
@app.route('/test/leis', methods=['GET'])
def pagina_leis():
    return render_template('Tcc/Leis/leis.html')

# Tela de Login (Leva para o template que você criou na pasta Tcc/Login)
@app.route('/test/login', methods=['GET'])
def tela_login():
    # Se o usuário já estiver logado e tentar entrar no login, joga direto pro index
    if session.get('role') in ('admin', 'user'):
        return redirect('/test')
    return render_template('Tcc/Login/login.html')

# Tela de Cadastro
@app.route('/test/cadastro', methods=['GET'])
def tela_cadastro():
    # Se o usuário já estiver logado e tentar cadastrar, joga direto pro index
    if session.get('role') in ('admin', 'user'):
        return redirect('/test')
    return render_template('Tcc/Login/cadastro.html')

# Rota para deslogar do sistema
@app.route('/test/logout')
def logout():
    session.clear()
    return redirect('/test/login')

# ===========================================================================
# Login Usuários
# ===========================================================================

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({"status": "erro", "mensagem": "Preencha todos os campos."}), 400

    # Verificação simples e direta para o Admin
    if email == "admin@sistema.com" and senha == "admin123":
        session['usuario_id'] = "admin"
        session['usuario_nome'] = "Administrador"
        session['role'] = "admin"
        return jsonify({"status": "sucesso", "redirect": "/test"}), 200

    # Busca do usuário comum no banco de dados
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nome_usuario, email, senha FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['usuario_id'] = user['id']
            session['usuario_nome'] = user['nome_usuario']
            session['role'] = "user"
            return jsonify({"status": "sucesso", "redirect": "/test"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro interno do servidor: {str(e)}"}), 500
    
    return jsonify({"status": "erro", "mensagem": "E-mail ou senha incorretos."}), 401

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

    # -------------------------------------------------------------------------
    # MODIFICAÇÃO: Captura o autor da sessão (Admin ou Usuário Temporário)
    # -------------------------------------------------------------------------
    # Se por algum motivo a sessão falhar, define o padrão como "Visitante Anônimo"
    autor_nome = session.get('usuario_nome', 'Visitante Anônimo')
    
    # Formata o corpo da notícia injetando uma assinatura elegante ao final do texto
    corpo_com_autor = f"{corpo}\n\n— Publicado por: {autor_nome}"
    # -------------------------------------------------------------------------

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        
        # Agora inserimos o 'corpo_com_autor' no lugar do corpo puro original
        cur.execute(
            "INSERT INTO noticias (titulo, corpo) VALUES (%s, %s)", 
            (titulo, corpo_com_autor)
        )
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
            "SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda LIMIT %s OFFSET %s",
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
        cur.execute("SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda WHERE id = %s", (aid,))
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

    # Lógica de definição do autor com base na sessão
    if session.get('role') == 'guest':
        autor_nome = session.get('usuario_id', 'anon')
    else:
        autor_nome = session.get('usuario_nome', 'Visitante Anônimo')

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO ajuda (titulo, corpo, pix_doacao, autor) VALUES (%s, %s, %s, %s)",
            (titulo, corpo, pix, autor_nome)
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda WHERE id = %s", (new_id,))
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

    if 'autor' in data:
        autor = (data['autor'] or '').strip()
        if not autor:
            errors['autor'] = 'Não pode ser vazio'
        else:
            updates.append("autor = %s")
            params.append(autor)

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
        cur.execute("SELECT id, titulo, corpo, pix_doacao, autor FROM ajuda WHERE id = %s", (aid,))
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