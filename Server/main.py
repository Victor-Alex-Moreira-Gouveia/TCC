import os
import time
from flask import Flask, jsonify
import mysql.connector
from pymemcache.client.base import Client

app = Flask(__name__)

# Configurações vindas do ambiente (Docker Compose)
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'mariadb'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', '19032007'),
    'database': os.getenv('DATABASE_NAME', 'MausTratosDB')
}

MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', 'memcached')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))

def test_mariadb():
    try:
        # Tenta conectar ao MariaDB
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            conn.close()
            return True, "Conexão com MariaDB: OK"
    except Exception as e:
        return False, f"Erro MariaDB: {str(e)}"

def test_memcached():
    try:
        # Tenta definir e buscar uma chave no Memcached
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
        "checks": {
            "mariadb": db_msg,
            "memcached": cache_msg
        }
    }), status_code

if __name__ == '__main__':
    # Em produção o Gunicorn chama 'app', mas para testes locais:
    app.run(host='0.0.0.0', port=8080)