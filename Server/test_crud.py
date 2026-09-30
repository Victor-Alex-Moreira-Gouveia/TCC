"""
test_crud.py — Testes automatizados do projeto Vozes que não podem gritar
========================================================================
Técnicas Aplicadas:
- Teste de Integração Bottom-Up (Unitário -> Controller/API -> Sistema)
- Teste de Integração Incremental (Módulo de Auth -> Notícias -> Módulos Sociais -> Cache e Fallback)
- Suporte a Múltiplos Formatos de Imagem (PNG, JPG, JPEG, WEBP, GIF, SVG, BMP, AVIF)
- Validação de Cache Otimizado e Fallback Gracioso sem Interrupção do Serviço
- Melhoria no Tratamento de Erros e Formato Padronizado de Diagnóstico JSON

Execução:
    docker compose exec server pytest -v test_crud.py
"""

import io
import os
import time
import pytest
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8080').rstrip('/')
API = f"{BASE_URL}/api"


def get_admin_session():
    s = requests.Session()
    r = s.post(f"{API}/login", json={"email": "admin@sistema.com", "senha": "admin123"})
    assert r.status_code == 200, f"Login admin falhou: {r.text}"
    return s


def get_user_session():
    ts = str(int(time.time() * 1000))
    email = f"user.{ts}@maustratos.test"
    senha = "SenhaUser@123"

    r_create = requests.post(f"{API}/usuarios", json={
        "nome_usuario": f"User {ts}",
        "email": email,
        "senha": senha
    })
    assert r_create.status_code == 201, f"Cadastro usuário falhou: {r_create.text}"

    s = requests.Session()
    r_login = s.post(f"{API}/login", json={"email": email, "senha": senha})
    assert r_login.status_code == 200, f"Login usuário falhou: {r_login.text}"
    return s, r_create.json()["data"]["id"]


# ===========================================================================
# 1. TESTE BOTTOM-UP: NÍVEL 1 — UNIDADE & AUXILIARES (Cache, Mime, Diagnóstico)
# ===========================================================================

class TestBottomUpUnidade:
    def test_detect_image_mime_multiplos_formatos(self):
        """Bottom-up: Testa função utilitária de detecção dinâmica de MIME types."""
        from utils import detect_image_mime

        # PNG Magic Bytes
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR'
        ok, mime = detect_image_mime('teste.png', 'image/png', png_bytes)
        assert ok is True
        assert mime == 'image/png'

        # JPEG Magic Bytes
        jpg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        ok, mime = detect_image_mime('foto.jpg', 'image/jpeg', jpg_bytes)
        assert ok is True
        assert mime == 'image/jpeg'

        # WEBP Magic Bytes
        webp_bytes = b'RIFF\x00\x00\x00\x00WEBPVP8 '
        ok, mime = detect_image_mime('imagem.webp', 'image/webp', webp_bytes)
        assert ok is True
        assert mime == 'image/webp'

        # GIF Magic Bytes
        gif_bytes = b'GIF89a\x01\x00\x01\x00'
        ok, mime = detect_image_mime('animacao.gif', 'image/gif', gif_bytes)
        assert ok is True
        assert mime == 'image/gif'

        # SVG Text
        svg_bytes = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="5"/></svg>'
        ok, mime = detect_image_mime('vetor.svg', 'image/svg+xml', svg_bytes)
        assert ok is True
        assert mime == 'image/svg+xml'

        # Arquivo Não Imagem (deve falhar na validação)
        txt_bytes = b'Este eh um arquivo de texto simples e nao uma imagem.'
        ok, mime = detect_image_mime('documento.txt', 'text/plain', txt_bytes)
        assert ok is False

    def test_graceful_cache_fallback_sem_excecao(self):
        """Bottom-up: Testa o módulo de cache garantindo resiliência se a conexão falhar."""
        from config.cache import GracefulCache

        # Instancia cache apontando para porta inválida (simulando Memcached offline)
        bad_cache = GracefulCache(host='127.0.0.1', port=59999)
        
        # Leitura, escrita e flush devem retornar None/False sem estourar exceção para o caller
        assert bad_cache.get('qualquer_chave') is None
        assert bad_cache.set('qualquer_chave', {'dados': 1}) is False
        assert bad_cache.delete('qualquer_chave') is False
        assert bad_cache.flush() is False


# ===========================================================================
# 2. TESTE INCREMENTAL: INCREMENTO 1 — AUTH & SEGURANÇA
# ===========================================================================

class TestIncrementalAuthESeguranca:
    def test_health_check_resiliencia(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code in (200, 500)
        data = r.json()
        assert 'status' in data
        assert 'checks' in data

    def test_visitante_bloqueado_na_api_noticias(self):
        r = requests.get(f"{API}/noticias")
        assert r.status_code == 401
        assert r.json()["success"] is False
        assert r.json()["code"] == "UNAUTHORIZED"

    def test_redirecionamento_pagina_restrita(self):
        r = requests.get(f"{BASE_URL}/noticias", allow_redirects=False)
        assert r.status_code == 302
        assert '/login' in r.headers['Location']

    def test_usuario_comum_bloqueado_de_criar_noticia(self):
        user_s, _ = get_user_session()
        r = user_s.post(f"{API}/noticias", data={
            "titulo": "Tentativa não autorizada",
            "corpo": "Sem permissão de admin"
        })
        assert r.status_code == 403
        assert r.json()["code"] == "FORBIDDEN"


# ===========================================================================
# 3. TESTE INCREMENTAL: INCREMENTO 2 — MULTI-FORMATO DE IMAGEM & NOTÍCIAS
# ===========================================================================

class TestMultiFormatosDeImagemENoticias:
    TS = str(int(time.time() * 1000))
    created_id = None

    def test_upload_imagem_png(self):
        admin_s = get_admin_session()
        png_bytes = bytes([
            0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a,0x00,0x00,0x00,0x0d,
            0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,
            0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,0xde,0x00,0x00,0x00,
            0x0c,0x49,0x44,0x41,0x54,0x08,0xd7,0x63,0xf8,0xff,0xff,0x3f,
            0x00,0x05,0xfe,0x02,0xfe,0xdc,0xcc,0x59,0xe7,0x00,0x00,0x00,
            0x00,0x49,0x45,0x4e,0x44,0xae,0x42,0x60,0x82
        ])
        r = admin_s.post(
            f"{API}/noticias",
            data={'titulo': f'Notícia PNG {self.TS}', 'corpo': 'Teste com imagem PNG.'},
            files={'imagem': ('imagem.png', io.BytesIO(png_bytes), 'image/png')}
        )
        assert r.status_code == 201, r.text
        nid = r.json()['data']['id']
        TestMultiFormatosDeImagemENoticias.created_id = nid

        # Valida endpoint e MIME Type
        r_img = admin_s.get(f"{BASE_URL}/api/noticias/{nid}/imagem")
        assert r_img.status_code == 200
        assert 'image/png' in r_img.headers.get('Content-Type', '')

    def test_upload_imagem_jpeg(self):
        admin_s = get_admin_session()
        jpg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
        r = admin_s.post(
            f"{API}/noticias",
            data={'titulo': f'Notícia JPEG {self.TS}', 'corpo': 'Teste com imagem JPEG.'},
            files={'imagem': ('foto.jpg', io.BytesIO(jpg_bytes), 'image/jpeg')}
        )
        assert r.status_code == 201, r.text
        nid = r.json()['data']['id']

        r_img = admin_s.get(f"{BASE_URL}/api/noticias/{nid}/imagem")
        assert r_img.status_code == 200
        assert 'image/jpeg' in r_img.headers.get('Content-Type', '')

        # Cleanup
        admin_s.delete(f"{API}/noticias/{nid}")

    def test_upload_imagem_webp(self):
        admin_s = get_admin_session()
        webp_bytes = b'RIFF\x18\x00\x00\x00WEBPVP8 \x0c\x00\x00\x000\x01\x00\x9d\x01\x2a\x01\x00\x01\x00\x02\x000\x25\xa4\x00'
        r = admin_s.post(
            f"{API}/noticias",
            data={'titulo': f'Notícia WEBP {self.TS}', 'corpo': 'Teste com imagem WEBP.'},
            files={'imagem': ('imagem.webp', io.BytesIO(webp_bytes), 'image/webp')}
        )
        assert r.status_code == 201, r.text
        nid = r.json()['data']['id']

        r_img = admin_s.get(f"{BASE_URL}/api/noticias/{nid}/imagem")
        assert r_img.status_code == 200
        assert 'image/webp' in r_img.headers.get('Content-Type', '')

        # Cleanup
        admin_s.delete(f"{API}/noticias/{nid}")

    def test_upload_imagem_svg(self):
        admin_s = get_admin_session()
        svg_bytes = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10" fill="red"/></svg>'
        r = admin_s.post(
            f"{API}/noticias",
            data={'titulo': f'Notícia SVG {self.TS}', 'corpo': 'Teste com arquivo SVG.'},
            files={'imagem': ('icone.svg', io.BytesIO(svg_bytes), 'image/svg+xml')}
        )
        assert r.status_code == 201, r.text
        nid = r.json()['data']['id']

        r_img = admin_s.get(f"{BASE_URL}/api/noticias/{nid}/imagem")
        assert r_img.status_code == 200
        assert 'image/svg+xml' in r_img.headers.get('Content-Type', '')

        # Cleanup
        admin_s.delete(f"{API}/noticias/{nid}")

    def test_rejeicao_de_arquivo_nao_imagem(self):
        admin_s = get_admin_session()
        file_bytes = b"echo 'hacked' > /tmp/malicious.sh"
        r = admin_s.post(
            f"{API}/noticias",
            data={'titulo': 'Script Malicioso', 'corpo': 'Tentativa de upload de script.'},
            files={'imagem': ('script.sh', io.BytesIO(file_bytes), 'text/plain')}
        )
        assert r.status_code == 400
        body = r.json()
        assert body['success'] is False
        assert body['code'] == 'INVALID_IMAGE_FORMAT'

    def test_list_noticias_pre_cadastradas(self):
        user_s, _ = get_user_session()
        r = user_s.get(f"{API}/noticias?limit=50")
        assert r.status_code == 200
        items = r.json()['data']
        assert len(items) >= 12
        # Verifica se todas as notícias possuem imagem associada
        com_imagem = [n for n in items if n.get('imagem_url')]
        assert len(com_imagem) >= 12


# ===========================================================================
# 4. TESTE INCREMENTAL: INCREMENTO 3 — INTERATIVIDADE SOCIAL (Comentários & Curtidas)
# ===========================================================================

class TestInteratividadeSocial:
    def test_curtidas_e_comentarios_com_seguranca(self):
        admin_s = get_admin_session()
        user_s, _ = get_user_session()

        # Cria notícia
        r_not = admin_s.post(f"{API}/noticias", data={
            'titulo': 'Notícia Social Teste',
            'corpo': 'Corpo da notícia para testes sociais.'
        })
        assert r_not.status_code == 201
        nid = r_not.json()['data']['id']

        # Curtir
        r_curt = user_s.post(f"{API}/noticias/{nid}/curtida")
        assert r_curt.status_code == 200
        assert r_curt.json()['data']['curtidas_count'] >= 1

        # Comentar com higienização de XSS
        r_com = user_s.post(f"{API}/noticias/{nid}/comentarios", json={
            'texto': "<script>alert('hack')</script>Comentário seguro."
        })
        assert r_com.status_code == 201
        assert '&lt;script&gt;' in r_com.json()['data']['texto']

        # Cleanup
        admin_s.delete(f"{API}/noticias/{nid}")


# ===========================================================================
# 5. TESTE INCREMENTAL: INCREMENTO 4 — CACHE & FALLBACK GRACIOSO
# ===========================================================================

class TestCacheEOtimizacao:
    def test_list_noticias_com_cache(self):
        user_s, _ = get_user_session()
        # Primeira requisição (popula cache)
        r1 = user_s.get(f"{API}/noticias?limit=5")
        assert r1.status_code == 200
        
        # Segunda requisição (servida via Memcached ou DB fallback transparente)
        r2 = user_s.get(f"{API}/noticias?limit=5")
        assert r2.status_code == 200
        assert r1.json()['data'] == r2.json()['data']

    def test_invalida_cache_ao_criar_nova_noticia(self):
        admin_s = get_admin_session()
        user_s, _ = get_user_session()

        # Chama listagem para aquecer cache
        user_s.get(f"{API}/noticias?limit=10")

        # Cria nova notícia
        r_new = admin_s.post(f"{API}/noticias", data={
            'titulo': 'Notícia Invalidação Cache',
            'corpo': 'Testando expiração do cache.'
        })
        assert r_new.status_code == 201
        nid = r_new.json()['data']['id']

        # Busca atualizada deve refletir novo item
        r_list = user_s.get(f"{API}/noticias?limit=50")
        titulos = [n['titulo'] for n in r_list.json()['data']]
        assert 'Notícia Invalidação Cache' in titulos

        # Cleanup
        admin_s.delete(f"{API}/noticias/{nid}")


# ===========================================================================
# 6. TESTE DE ERROS & DIAGNÓSTICO HTTP
# ===========================================================================

class TestTratamentoErrosEDiagnostico:
    def test_404_api_retorna_json_padronizado(self):
        r = requests.get(f"{API}/rota_que_nao_existe")
        assert r.status_code == 404
        body = r.json()
        assert body['success'] is False
        assert body['code'] == 'NOT_FOUND'

    def test_405_metodo_nao_permitido(self):
        admin_s = get_admin_session()
        r = admin_s.post(f"{API}/noticias/1/imagem")
        assert r.status_code == 405
        body = r.json()
        assert body['success'] is False
        assert body['code'] == 'METHOD_NOT_ALLOWED'
