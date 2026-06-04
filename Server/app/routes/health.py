from flask import Blueprint, jsonify
from app.models.database import get_db_connection, close_db_connection
from app.utils.cache import test_cache

bp = Blueprint('health', __name__, url_prefix='/health')

def test_mariadb():
    """Testa conexão com MariaDB"""
    try:
        conn = get_db_connection()
        if conn.is_connected():
            close_db_connection(conn)
            return True, "Conexão com MariaDB: OK"
    except Exception as e:
        return False, f"Erro MariaDB: {str(e)}"

def test_memcached():
    """Testa conexão com Memcached"""
    try:
        if test_cache():
            return True, "Conexão com Memcached: OK"
        return False, "Memcached: Falha na integridade dos dados"
    except Exception as e:
        return False, f"Erro Memcached: {str(e)}"

@bp.route('/', methods=['GET'])
def health_check():
    """Endpoint de health check da API"""
    db_status, db_msg = test_mariadb()
    cache_status, cache_msg = test_memcached()
    
    status_code = 200 if db_status and cache_status else 500
    
    return jsonify({
        "status": "online" if status_code == 200 else "unstable",
        "checks": {
            "mariadb": db_msg,
            "memcached": cache_msg
        }
    }), status_code
