import json
import logging
from pymemcache.client.base import Client
from config.config import MEMCACHED_HOST, MEMCACHED_PORT

logger = logging.getLogger('app_cache')


class GracefulCache:
    """
    Sistema de Cache otimizado com suporte a Fallback Gracioso.
    Caso a instância do Memcached esteja ausente ou indisponível,
    o sistema continua operando normalmente realizando as consultas no banco de dados relacional.
    """
    def __init__(self, host=MEMCACHED_HOST, port=MEMCACHED_PORT):
        self.host = host
        self.port = port
        self._client = None

    def get_client(self):
        try:
            if self._client is None:
                self._client = Client(
                    (self.host, self.port),
                    connect_timeout=1,
                    timeout=1,
                    ignore_exc=True,
                )
            return self._client
        except Exception as exc:
            logger.warning(f"[Cache Warning] Falha ao conectar ao Memcached ({self.host}:{self.port}): {exc}")
            return None

    def is_available(self) -> bool:
        try:
            client = self.get_client()
            if not client:
                return False
            client.set('healthcheck_ping', 'pong', expire=10)
            val = client.get('healthcheck_ping')
            return val == b'pong'
        except Exception as exc:
            logger.warning(f"[Cache Warning] Memcached indisponível no healthcheck: {exc}")
            return False

    def get(self, key: str):
        try:
            client = self.get_client()
            if not client:
                return None
            data = client.get(key)
            if data:
                return json.loads(data.decode('utf-8'))
        except Exception as exc:
            logger.warning(f"[Cache Warning] Falha na leitura da chave '{key}': {exc}")
        return None

    def set(self, key: str, value: any, expire: int = 120):
        try:
            client = self.get_client()
            if not client:
                return False
            serialized = json.dumps(value).encode('utf-8')
            return client.set(key, serialized, expire=expire)
        except Exception as exc:
            logger.warning(f"[Cache Warning] Falha ao gravar chave '{key}': {exc}")
            return False

    def delete(self, key: str):
        try:
            client = self.get_client()
            if not client:
                return False
            return client.delete(key)
        except Exception as exc:
            logger.warning(f"[Cache Warning] Falha ao deletar chave '{key}': {exc}")
            return False

    def flush(self):
        try:
            client = self.get_client()
            if not client:
                return False
            return client.flush_all()
        except Exception as exc:
            logger.warning(f"[Cache Warning] Falha ao efetuar flush do cache: {exc}")
            return False


# Instância global reutilizável
cache = GracefulCache()
