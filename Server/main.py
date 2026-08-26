import os
import re
import math
import time
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from sqlalchemy import select
from models.usuarios import Usuario # Assumindo que o seu modelo Usuario está aqui
from pymemcache.client.base import Client
from werkzeug.security import generate_password_hash, check_password_hash
import random
from config.config import *

# Load app config from centralized module (reads .env)
from config.config import DB_CONFIG, MEMCACHED_HOST, MEMCACHED_PORT, get_db, init_db_schema, test_mariadb, detect_db_engine

app = Flask(__name__)
# prefer secret from environment
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'admin1234@')

# Ensure DB schema migrations at startup (keeps original behavior)
init_db_schema()

# Gerador de usuário temporário automático para visitantes anônimos
@app.before_request
def garantir_usuario_temporario():
    # Se a pessoa não está logada (nem como admin, nem como comum)
    if 'usuario_id' not in session:
        numero_aleatorio = random.randint(10000, 99999)
        session['usuario_id'] = f"anon#{numero_aleatorio}"
        session['usuario_nome'] = "Visitante Anônimo"
        session['role'] = "guest" # Convidado/Anônimo



from utils import success_response, error_response, parse_pagination, build_pagination, validate_email, validate_pix


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

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
    # Keep backward-compatible DB check (config.test_mariadb) and also detect engine/version
    db_status, db_msg = test_mariadb()
    engine, engine_info = detect_db_engine()
    cache_status, cache_msg = test_memcached()

    status_code = 200 if db_status and cache_status else 500
    checks = {
        "database": {
            "status": db_msg,
            "engine": engine,
            "version_or_info": engine_info
        },
        "memcached": cache_msg
    }
    return jsonify({
        "status": "online" if status_code == 200 else "unstable",
        "checks": checks
    }), status_code


# ---------------------------------------------------------------------------
# Páginas do Sistema (Renderização de templates com travas de segurança)
# ---------------------------------------------------------------------------

# Página Inicial (Qualquer um pode acessar, até o anônimo/guest)
@app.route('/')
def test_index():
    return render_template('Tcc/index.html')

# Painel de Usuários - APENAS ADMIN
@app.route('/usuarios')
def test_usuarios():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('Tcc/Usuario/usuarios.html')

# Painel de Notícias - APENAS ADMIN
@app.route('/noticias')
def test_noticias():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('Tcc/Noticias/noticias.html')

# Painel de ONGs - APENAS ADMIN
@app.route('/ongs')
def test_ongs():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('Tcc/ONGs/ongs.html')

# Painel de Ajuda - APENAS ADMIN
@app.route('/ajuda')
def test_ajuda():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('Tcc/Ajuda/ajuda.html')

# Solicitação Pública de Ajuda (Qualquer um pode acessar)
@app.route('/ajuda/pedir', methods=['GET'])
def public_pedir_ajuda():
    return render_template('Tcc/Ajuda/pedir_ajuda.html')

# Página Estática de Leis (Qualquer um pode acessar)
@app.route('/leis', methods=['GET'])
def pagina_leis():
    return render_template('Tcc/Leis/leis.html')

# Tela de Login (Leva para o template que você criou na pasta Tcc/Login)
@app.route('/login', methods=['GET'])
def tela_login():
    # Se o usuário já estiver logado e tentar entrar no login, joga direto pro index
    if session.get('role') in ('admin', 'user'):
        return redirect('/')
    return render_template('Tcc/Login/login.html')

# Tela de Cadastro
@app.route('/cadastro', methods=['GET'])
def tela_cadastro():
    # Se o usuário já estiver logado e tentar cadastrar, joga direto pro index
    if session.get('role') in ('admin', 'user'):
        return redirect('/')
    return render_template('Tcc/Login/cadastro.html')

# Rota para deslogar do sistema
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

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
        return jsonify({"status": "sucesso", "redirect": "/"}), 200

    # Busca do usuário comum no banco de dados usando SQLAlchemy
    try:
        # Obter a sessão do banco
        db = next(get_db())
        
        # Consulta usando o ORM
        stmt = select(Usuario).where(Usuario.email == email)
        user = db.scalar(stmt)

        # Verifica se o usuário existe e se a senha bate[cite: 10]
        if user and check_password_hash(user.senha, senha):
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome_usuario
            session['role'] = "user"
            return jsonify({"status": "sucesso", "redirect": "/"}), 200
            
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro interno do servidor: {str(e)}"}), 500
    
    return jsonify({"status": "erro", "mensagem": "E-mail ou senha incorretos."}), 401
# ===========================================================================
# CRUD — Usuarios
# ===========================================================================

# migrated to controllers.usuarios blueprint
from controllers.usuarios import usuarios_bp
app.register_blueprint(usuarios_bp)


# ===========================================================================
# CRUD — Noticias
# migrated to controllers.noticias
# from controllers.noticias import noticias_bp
# app.register_blueprint(noticias_bp)

# ===========================================================================
# CRUD — ONGs
# migrated to controllers.ongs
from controllers.ongs import ongs_bp
app.register_blueprint(ongs_bp)


# ===========================================================================
# CRUD — Ajuda
# migrated to controllers.ajuda
from controllers.ajuda import ajuda_bp
app.register_blueprint(ajuda_bp)


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)