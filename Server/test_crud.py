"""
test_crud.py — Testes automatizados do projeto Vozes que não podem gritar
========================================================================
Execução:
    docker compose exec server pytest -v test_crud.py
    # ou
    python -m pytest Server/test_crud.py -v
"""

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
# Health Check
# ===========================================================================

class TestHealth:
    def test_health_endpoint_is_reachable(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code in (200, 500)

    def test_health_returns_json(self):
        r = requests.get(f"{BASE_URL}/health")
        data = r.json()
        assert 'status' in data
        assert 'checks' in data


# ===========================================================================
# Autenticação Obrigatória e Trava de Segurança
# ===========================================================================

class TestAutenticacaoEBloqueios:
    def test_visitante_nao_acessa_api_noticias_sem_login(self):
        r = requests.get(f"{API}/noticias")
        assert r.status_code == 401
        assert r.json()["success"] is False

    def test_visitante_redirecionado_ao_tentar_acessar_pagina_noticias(self):
        r = requests.get(f"{BASE_URL}/noticias", allow_redirects=False)
        assert r.status_code == 302
        assert '/login' in r.headers['Location']

    def test_visitante_acessa_paginas_publicas_sem_login(self):
        r_home = requests.get(f"{BASE_URL}/")
        assert r_home.status_code == 200

        r_pedir = requests.get(f"{BASE_URL}/ajuda/pedir")
        assert r_pedir.status_code == 200

    def test_usuario_comum_nao_cria_noticia(self):
        user_s, _ = get_user_session()
        r = user_s.post(f"{API}/noticias", json={
            "titulo": "Notícia não autorizada",
            "corpo": "Usuário comum não pode criar"
        })
        assert r.status_code == 403
        assert r.json()["code"] == "FORBIDDEN"

    def test_modulo_ongs_removido_retorna_404(self):
        admin_s = get_admin_session()
        r = admin_s.get(f"{API}/ongs")
        assert r.status_code == 404


# ===========================================================================
# CRUD — Usuarios
# ===========================================================================

class TestUsuarios:
    TS = str(int(time.time() * 1000))
    VALID = {
        "nome_usuario": f"Teste User {TS}",
        "email": f"teste.user.{TS}@maustratos.test",
        "senha": "Senha@1234",
    }
    created_id = None

    def test_create_usuario_sucesso(self):
        r = requests.post(f"{API}/usuarios", json=self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        assert "id" in body["data"]
        TestUsuarios.created_id = body["data"]["id"]

    def test_create_usuario_email_duplicado(self):
        r = requests.post(f"{API}/usuarios", json=self.VALID)
        assert r.status_code == 409
        assert r.json()["success"] is False

    def test_create_usuario_sem_campos_obrigatorios(self):
        r = requests.post(f"{API}/usuarios", json={})
        assert r.status_code == 400
        body = r.json()
        assert body["success"] is False

    def test_list_usuarios_autenticado(self):
        admin_s = get_admin_session()
        r = admin_s.get(f"{API}/usuarios")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)

    def test_get_usuario_por_id(self):
        admin_s = get_admin_session()
        assert TestUsuarios.created_id
        r = admin_s.get(f"{API}/usuarios/{TestUsuarios.created_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == TestUsuarios.created_id

    def test_update_usuario_nome(self):
        admin_s = get_admin_session()
        assert TestUsuarios.created_id
        r = admin_s.put(f"{API}/usuarios/{TestUsuarios.created_id}", json={"nome_usuario": "Nome Atualizado"})
        assert r.status_code == 200
        assert r.json()["data"]["nome_usuario"] == "Nome Atualizado"

    def test_delete_usuario(self):
        admin_s = get_admin_session()
        assert TestUsuarios.created_id
        r = admin_s.delete(f"{API}/usuarios/{TestUsuarios.created_id}")
        assert r.status_code == 204


# ===========================================================================
# CRUD — Noticias (Admin) e Noticias Pré-Cadastradas
# ===========================================================================

class TestNoticias:
    TS = str(int(time.time() * 1000))
    VALID = {
        "titulo": f"Notícia de Teste {TS}",
        "corpo": "Conteúdo gerado por teste automatizado.",
        "imagem_url": "/static/img_posts/Imagem1.jpg"
    }
    created_id = None

    def test_create_noticia_sucesso_admin_com_imagem(self):
        admin_s = get_admin_session()
        r = admin_s.post(f"{API}/noticias", json=self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        assert "id" in body["data"]
        assert body["data"]["imagem_url"] == "/static/img_posts/Imagem1.jpg"
        TestNoticias.created_id = body["data"]["id"]

    def test_list_noticias_contem_pre_cadastradas(self):
        user_s, _ = get_user_session()
        r = user_s.get(f"{API}/noticias?limit=50")
        assert r.status_code == 200
        items = r.json()["data"]
        assert len(items) >= 12
        titulos = [n["titulo"] for n in items]
        assert any("Mais de 100 animais" in t for t in titulos)
        assert any("Serial killer" in t for t in titulos)

    def test_update_noticia_admin(self):
        admin_s = get_admin_session()
        assert TestNoticias.created_id
        r = admin_s.put(f"{API}/noticias/{TestNoticias.created_id}", json={"titulo": "Título Notícia Atualizado"})
        assert r.status_code == 200
        assert "Atualizado" in r.json()["data"]["titulo"]


# ===========================================================================
# Comentários e Curtidas em Notícias
# ===========================================================================

class TestComentariosECurtidas:
    def test_curtir_e_descurtir_noticia(self):
        admin_s = get_admin_session()
        r_not = admin_s.post(f"{API}/noticias", json={
            "titulo": "Notícia para Curtida",
            "corpo": "Corpo da notícia para teste de curtida."
        })
        assert r_not.status_code == 201
        nid = r_not.json()["data"]["id"]

        user_s, _ = get_user_session()

        # Dar curtida
        r_like = user_s.post(f"{API}/noticias/{nid}/curtida")
        assert r_like.status_code == 200
        assert r_like.json()["data"]["curtidas_count"] >= 1
        assert r_like.json()["data"]["curtido_pelo_usuario"] is True

        # Descurtir
        r_unlike = user_s.delete(f"{API}/noticias/{nid}/curtida")
        assert r_unlike.status_code == 200
        assert r_unlike.json()["data"]["curtido_pelo_usuario"] is False

    def test_criar_e_moderar_comentario(self):
        admin_s = get_admin_session()
        r_not = admin_s.post(f"{API}/noticias", json={
            "titulo": "Notícia para Comentário",
            "corpo": "Corpo da notícia para teste de comentário."
        })
        assert r_not.status_code == 201
        nid = r_not.json()["data"]["id"]

        user_s, _ = get_user_session()

        # Adicionar comentário com XSS potencial
        r_com = user_s.post(f"{API}/noticias/{nid}/comentarios", json={
            "texto": "<script>alert('xss')</script>Comentário Válido"
        })
        assert r_com.status_code == 201
        cid = r_com.json()["data"]["id"]
        assert "&lt;script&gt;" in r_com.json()["data"]["texto"]

        # Editar próprio comentário
        r_upd = user_s.put(f"{API}/comentarios/{cid}", json={"texto": "Comentário Editado com Sucesso"})
        assert r_upd.status_code == 200
        assert r_upd.json()["data"]["texto"] == "Comentário Editado com Sucesso"

        # Admin exclui comentário
        r_del = admin_s.delete(f"{API}/comentarios/{cid}")
        assert r_del.status_code == 204


# ===========================================================================
# CRUD — Ajuda (Denúncia com Orientação Imediata, Sem PIX)
# ===========================================================================

class TestAjuda:
    TS = str(int(time.time() * 1000))
    VALID = {
        "titulo": f"Denúncia Urgente {TS}",
        "corpo": "Cão atropelado necessitando de socorro imediato.",
        "tipo_denuncia": "Animal doméstico",
        "nivel_urgencia": "Atropelamento"
    }
    created_id = None

    def test_create_ajuda_retorna_orientacao_imediata(self):
        user_s, _ = get_user_session()
        r = user_s.post(f"{API}/ajuda", json=self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        assert "orientacao_imediata" in body["data"]
        assert "resgate" in body["data"]["orientacao_imediata"].lower() or "zoonoses" in body["data"]["orientacao_imediata"].lower()
        TestAjuda.created_id = body["data"]["id"]

    def test_create_ajuda_sem_pix_doacao(self):
        user_s, _ = get_user_session()
        assert TestAjuda.created_id
        r = user_s.get(f"{API}/ajuda/{TestAjuda.created_id}")
        assert r.status_code == 200
        assert "pix_doacao" not in r.json()["data"]

    def test_delete_ajuda(self):
        admin_s = get_admin_session()
        assert TestAjuda.created_id
        r = admin_s.delete(f"{API}/ajuda/{TestAjuda.created_id}")
        assert r.status_code == 204


# ===========================================================================
# Testes de Paginação
# ===========================================================================

class TestPaginacao:
    def test_paginacao_limit(self):
        admin_s = get_admin_session()
        r = admin_s.get(f"{API}/noticias?limit=2&page=1")
        assert r.status_code == 200
        body = r.json()
        assert body["pagination"]["limit"] == 2
        assert len(body["data"]) <= 2
