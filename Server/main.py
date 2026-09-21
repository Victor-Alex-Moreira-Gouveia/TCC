import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from pymemcache.client.base import Client
from sqlalchemy import select
from werkzeug.security import check_password_hash

from config.config import MEMCACHED_HOST, MEMCACHED_PORT, detect_db_engine, get_db, init_db_schema, test_mariadb
from models.usuarios import Usuario

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'admin1234@')

# Garante a sincronização do schema e migrações no arranque
init_db_schema()


@app.before_request
def verificar_autenticacao():
    path = request.path

    # Assets estáticos e endpoint de saúde são abertos
    if path.startswith('/static') or path == '/health':
        return None

    # Apenas a área de notícias (página e API) exige que o usuário esteja logado.
    # O restante do sistema é de livre acesso ao público / usuários anônimos.
    is_noticias_route = path == '/noticias' or path.startswith('/api/noticias')

    if is_noticias_route:
        if session.get('role') not in ('admin', 'user'):
            if path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Acesso não autorizado', 'code': 'UNAUTHORIZED'}), 401
            return redirect(url_for('tela_login'))

    return None


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_memcached():
    try:
        client = Client((MEMCACHED_HOST, MEMCACHED_PORT))
        client.set('test_key', 'funcionando')
        result = client.get('test_key')
        if result == b'funcionando':
            return True, 'Conexão com Memcached: OK'
        return False, 'Memcached: Falha na integridade dos dados'
    except Exception as exc:
        return False, f'Erro Memcached: {str(exc)}'


@app.route('/health')
def health_check():
    db_status, db_msg = test_mariadb()
    engine, engine_info = detect_db_engine()
    cache_status, cache_msg = test_memcached()

    status_code = 200 if db_status and cache_status else 500
    checks = {
        'database': {
            'status': db_msg,
            'engine': engine,
            'version_or_info': engine_info,
        },
        'memcached': cache_msg,
    }
    return jsonify({
        'status': 'online' if status_code == 200 else 'unstable',
        'checks': checks,
    }), status_code


# ---------------------------------------------------------------------------
# Páginas do Sistema (Renderização de templates com travas de segurança)
# ---------------------------------------------------------------------------

@app.route('/')
def test_index():
    return render_template('Tcc/index.html')


@app.route('/usuarios')
def test_usuarios():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('Tcc/Usuario/usuarios.html')


@app.route('/noticias')
def test_noticias():
    return render_template('Tcc/noticias/noticias.html')


@app.route('/ajuda')
def test_ajuda():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('Tcc/Ajuda/ajuda.html')


@app.route('/ajuda/pedir', methods=['GET'])
def public_pedir_ajuda():
    return render_template('Tcc/Ajuda/pedir_ajuda.html')


@app.route('/leis', methods=['GET'])
def pagina_leis():
    return render_template('Tcc/Leis/leis.html')


@app.route('/login', methods=['GET'])
def tela_login():
    if session.get('role') in ('admin', 'user'):
        return redirect('/')
    return render_template('Tcc/Login/login.html')


@app.route('/cadastro', methods=['GET'])
def tela_cadastro():
    if session.get('role') in ('admin', 'user'):
        return redirect('/')
    return render_template('Tcc/Login/cadastro.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ===========================================================================
# Login Usuários
# ===========================================================================

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip()
    senha = (dados.get('senha') or '').strip()

    if not email or not senha:
        return jsonify({'status': 'erro', 'mensagem': 'Preencha todos os campos.'}), 400

    # Verificação estática para o Admin de sistema
    if email == 'admin@sistema.com' and senha == 'admin123':
        session['usuario_id'] = 'admin'
        session['usuario_nome'] = 'Administrador'
        session['role'] = 'admin'
        return jsonify({'status': 'sucesso', 'redirect': '/'}), 200

    # Busca no banco pelo modelo Usuario
    try:
        db = next(get_db())
        stmt = select(Usuario).where(Usuario.email == email)
        user = db.scalar(stmt)

        if user and check_password_hash(user.senha, senha):
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome_usuario
            session['role'] = 'user'
            return jsonify({'status': 'sucesso', 'redirect': '/'}), 200

    except Exception as exc:
        return jsonify({'status': 'erro', 'mensagem': f'Erro interno do servidor: {str(exc)}'}), 500

    return jsonify({'status': 'erro', 'mensagem': 'E-mail ou senha incorretos.'}), 401


# ===========================================================================
# Blueprints
# ===========================================================================

from controllers.usuarios import usuarios_bp
from controllers.noticias import noticias_bp
from controllers.ajuda import ajuda_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(noticias_bp)
app.register_blueprint(ajuda_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
