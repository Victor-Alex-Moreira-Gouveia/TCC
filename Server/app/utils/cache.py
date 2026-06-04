from pymemcache.client.base import Client
from app.config import Config

def get_cache_client():
    """Cria cliente de conexão com Memcached"""
    return Client((Config.CACHE_HOST, Config.CACHE_PORT))

def test_cache():
    """Testa conexão com Memcached"""
    try:
        client = get_cache_client()
        client.set('test_key', 'funcionando')
        result = client.get('test_key')
        return result == b'funcionando'
    except Exception:
        return False
