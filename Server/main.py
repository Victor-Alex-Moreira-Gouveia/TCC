import logging
import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from pymemcache.client.base import Client
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from config.config import CACHE_ENABLED, MEMCACHED_HOST, MEMCACHED_PORT, ROOT_EMAIL, ROOT_PASSWORD, ROOT_USER, detect_db_engine, get_db, init_db_schema, test_mariadb
from config.cache import cache
from models.usuarios import Usuario
from models.animais_perdidos import AnimalPerdido
from utils import error_response

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s em %(module)s: %(message)s'
)
logger = logging.getLogger('app_main')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'admin1234@')

# Limite para upload de fotos dos animais.
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# O model AnimalPerdido é importado antes desta chamada para que
# Base.metadata.create_all() conheça a nova tabela.
init_db_schema()


@app.before_request
def verificar_autenticacao():
    path = request.path

    if path.startswith('/static') or path == '/health':
        return None

    # Sessões de admin criadas por versões anteriores usavam o ID virtual
    # "admin". Migra para o usuário administrativo real para manter as FKs
    # de curtidas, comentários e publicações de animais válidas.
    if session.get('role') == 'admin' and str(session.get('usuario_id')) == 'admin':
        try:
            admin = _get_or_create_admin_user()
            session['usuario_id'] = admin['id']
            session['usuario_nome'] = admin['nome_usuario']
        except Exception as exc:
            logger.error('Não foi possível atualizar a sessão administrativa: %s', exc, exc_info=True)

    is_noticias_route = path == '/noticias' or path.startswith('/api/noticias')

    if is_noticias_route:
        if session.get('role') not in ('admin', 'user'):
            if path.startswith('/api/'):
                return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)
            return redirect(url_for('tela_login'))

    return None


def _get_or_create_admin_user():
    """Retorna o registro administrativo persistente usado pelas FKs sociais."""
    db = next(get_db())
    try:
        admin = db.scalar(select(Usuario).where(Usuario.email == ROOT_EMAIL))
        if admin is None:
            admin = Usuario(
                nome_usuario=ROOT_USER,
                email=ROOT_EMAIL,
                senha=generate_password_hash(ROOT_PASSWORD),
            )
            db.add(admin)
            try:
                db.commit()
            except IntegrityError:
                # Evita falha se duas sessões de admin forem abertas juntas.
                db.rollback()
                admin = db.scalar(select(Usuario).where(Usuario.email == ROOT_EMAIL))
                if admin is None:
                    raise
            else:
                db.refresh(admin)
        return {'id': admin.id, 'nome_usuario': admin.nome_usuario}
    finally:
        db.close()


@app.errorhandler(400)
def handle_bad_request(e):
    msg = str(e.description) if hasattr(e, 'description') else 'Requisição inválida'
    if request.path.startswith('/api/'):
        return error_response(msg, 'BAD_REQUEST', status=400)
    return render_template('Tcc/index.html'), 400


@app.errorhandler(404)
def handle_not_found(e):
    if request.path.startswith('/api/'):
        return error_response('Recurso ou rota não encontrada', 'NOT_FOUND', status=404)
    return render_template('Tcc/index.html'), 404


@app.errorhandler(405)
def handle_method_not_allowed(e):
    if request.path.startswith('/api/'):
        return error_response('Método HTTP não permitido para esta rota', 'METHOD_NOT_ALLOWED', status=405)
    return render_template('Tcc/index.html'), 405


@app.errorhandler(413)
def handle_payload_too_large(e):
    if request.path.startswith('/api/'):
        return error_response('O arquivo enviado excede o limite máximo permitido (5 MB).', 'PAYLOAD_TOO_LARGE', status=413)
    return render_template('Tcc/index.html'), 413


@app.errorhandler(500)
def handle_internal_server_error(e):
    logger.error(f"Erro interno de servidor não capturado na rota {request.path}: {e}", exc_info=True)
    if request.path.startswith('/api/'):
        return error_response(
            'Erro interno no servidor. O problema foi registrado para análise.',
            'INTERNAL_SERVER_ERROR',
            details=str(e) if app.debug else None,
            status=500
        )
    return render_template('Tcc/index.html'), 500


def test_memcached():
    if not CACHE_ENABLED:
        return False, 'Memcached desativado pela configuração'
    try:
        client = Client((MEMCACHED_HOST, MEMCACHED_PORT), connect_timeout=1, timeout=1)
        client.set('healthcheck_key', 'ok', expire=10)
        result = client.get('healthcheck_key')
        if result == b'ok':
            return True, 'Conexão com Memcached: OK'
        return False, 'Memcached: Resposta inesperada'
    except Exception as exc:
        return False, f'Memcached indisponível (Modo Fallback Ativo): {str(exc)}'


@app.route('/health')
def health_check():
    db_status, db_msg = test_mariadb()
    engine, engine_info = detect_db_engine()
    cache_status, cache_msg = test_memcached()

    status_code = 200 if db_status else 500
    checks = {
        'database': {
            'status': db_msg,
            'engine': engine,
            'version_or_info': engine_info,
        },
        'memcached': {
            'status': cache_msg,
            'enabled': CACHE_ENABLED,
            'cache_active': cache_status,
            'fallback_mode': not cache_status,
        },
    }
    return jsonify({
        'status': 'online' if db_status else 'unstable',
        'checks': checks,
    }), status_code


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


# ---------------------------------------------------------------------------
# Animais perdidos e encontrados
# ---------------------------------------------------------------------------

@app.route('/animais-perdidos')
def pagina_animais_perdidos():
    return render_template('Tcc/Animais/animais_perdidos.html')


@app.route('/animais-perdidos/publicacoes')
def publicacoes_animais_perdidos():
    return render_template('Tcc/Animais/publicacoes_animais.html')


@app.route('/animais-perdidos/admin')
def admin_animais_perdidos():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('Tcc/Animais/animais_admin.html')


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


@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip()
    senha = (dados.get('senha') or '').strip()

    if not email or not senha:
        return jsonify({'status': 'erro', 'mensagem': 'Preencha todos os campos.'}), 400

    if email == ROOT_EMAIL and senha == ROOT_PASSWORD:
        try:
            admin = _get_or_create_admin_user()
            session['usuario_id'] = admin['id']
            session['usuario_nome'] = admin['nome_usuario']
            session['role'] = 'admin'
            return jsonify({'status': 'sucesso', 'redirect': '/'}), 200
        except Exception as exc:
            logger.error('Erro ao preparar o usuário administrativo: %s', exc, exc_info=True)
            return jsonify({'status': 'erro', 'mensagem': 'Não foi possível iniciar a sessão administrativa.'}), 500

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
        logger.error(f"Erro no login: {exc}", exc_info=True)
        return jsonify({'status': 'erro', 'mensagem': f'Erro interno do servidor: {str(exc)}'}), 500

    return jsonify({'status': 'erro', 'mensagem': 'E-mail ou senha incorretos.'}), 401


from controllers.usuarios import usuarios_bp
from controllers.noticias import noticias_bp
from controllers.ajuda import ajuda_bp
from controllers.animais_perdidos import animais_perdidos_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(noticias_bp)
app.register_blueprint(ajuda_bp)
app.register_blueprint(animais_perdidos_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
