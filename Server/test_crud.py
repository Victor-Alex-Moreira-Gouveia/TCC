"""
test_crud.py — Testes automatizados do CRUD do projeto MausTratos
=================================================================
Execução:
    pytest test_crud.py -v
    # ou
    python -m pytest test_crud.py -v

Pré-requisitos:
    pip install pytest requests

A aplicação deve estar rodando em BASE_URL (padrão: http://localhost:8080).
Configure via variável de ambiente:
    BASE_URL=http://localhost:8080 pytest test_crud.py -v
"""

import os
import time
import pytest
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8080').rstrip('/')
API = f"{BASE_URL}/api"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post(endpoint, payload):
    return requests.post(f"{API}/{endpoint}", json=payload)

def get(endpoint):
    return requests.get(f"{API}/{endpoint}")

def put(endpoint, payload):
    return requests.put(f"{API}/{endpoint}", json=payload)

def delete(endpoint):
    return requests.delete(f"{API}/{endpoint}")


# ===========================================================================
# Health Check
# ===========================================================================

class TestHealth:
    def test_health_endpoint_is_reachable(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code in (200, 500), "Endpoint /health deve responder"

    def test_health_returns_json(self):
        r = requests.get(f"{BASE_URL}/health")
        data = r.json()
        assert 'status' in data
        assert 'checks' in data


# ===========================================================================
# CRUD — Usuarios
# ===========================================================================

class TestUsuarios:
    """Suite completa de testes para /api/usuarios"""

    TS = str(int(time.time()))
    VALID = {
        "nome_usuario": f"Teste User {TS}",
        "email": f"teste.user.{TS}@maustratos.test",
        "senha": "Senha@1234",
    }
    created_id = None

    # --- CREATE ---

    def test_create_usuario_sucesso(self):
        r = post("usuarios", self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        assert "id" in body["data"]
        TestUsuarios.created_id = body["data"]["id"]

    def test_create_usuario_email_duplicado(self):
        r = post("usuarios", self.VALID)
        assert r.status_code == 409
        assert r.json()["success"] is False

    def test_create_usuario_sem_campos_obrigatorios(self):
        r = post("usuarios", {})
        assert r.status_code == 400
        body = r.json()
        assert body["success"] is False
        assert "nome_usuario" in body.get("details", {})
        assert "email" in body.get("details", {})
        assert "senha" in body.get("details", {})

    def test_create_usuario_email_invalido(self):
        r = post("usuarios", {**self.VALID, "email": "nao-eh-email", "email": "invalido"})
        # garante email diferente para não conflitar
        r = post("usuarios", {
            "nome_usuario": "Teste",
            "email": "email-invalido-sem-arroba",
            "senha": "Senha@1234"
        })
        assert r.status_code == 400
        assert "email" in r.json().get("details", {})

    def test_create_usuario_senha_curta(self):
        r = post("usuarios", {
            "nome_usuario": "Teste",
            "email": f"outro.{self.TS}@maustratos.test",
            "senha": "123"
        })
        assert r.status_code == 400
        assert "senha" in r.json().get("details", {})

    # --- READ ---

    def test_list_usuarios_retorna_lista(self):
        r = get("usuarios")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert "pagination" in body

    def test_get_usuario_por_id(self):
        assert TestUsuarios.created_id, "Crie um usuário primeiro"
        r = get(f"usuarios/{TestUsuarios.created_id}")
        assert r.status_code == 200
        body = r.json()
        assert body["data"]["id"] == TestUsuarios.created_id

    def test_get_usuario_inexistente(self):
        r = get("usuarios/999999")
        assert r.status_code == 404
        assert r.json()["success"] is False

    # --- UPDATE ---

    def test_update_usuario_nome(self):
        assert TestUsuarios.created_id
        r = put(f"usuarios/{TestUsuarios.created_id}", {"nome_usuario": "Nome Atualizado"})
        assert r.status_code == 200
        assert r.json()["data"]["nome_usuario"] == "Nome Atualizado"

    def test_update_usuario_inexistente(self):
        r = put("usuarios/999999", {"nome_usuario": "X"})
        assert r.status_code == 404

    def test_update_usuario_sem_campos(self):
        assert TestUsuarios.created_id
        r = put(f"usuarios/{TestUsuarios.created_id}", {})
        assert r.status_code == 400

    # --- DELETE ---

    def test_delete_usuario(self):
        assert TestUsuarios.created_id
        r = delete(f"usuarios/{TestUsuarios.created_id}")
        assert r.status_code == 204

    def test_delete_usuario_inexistente(self):
        r = delete("usuarios/999999")
        assert r.status_code == 404

    def test_get_usuario_apos_delete(self):
        assert TestUsuarios.created_id
        r = get(f"usuarios/{TestUsuarios.created_id}")
        assert r.status_code == 404


# ===========================================================================
# CRUD — Noticias
# ===========================================================================

class TestNoticias:
    TS = str(int(time.time()))
    VALID = {
        "titulo": f"Notícia de Teste {TS}",
        "corpo": "Conteúdo gerado por teste automatizado.",
    }
    created_id = None

    def test_create_noticia_sucesso(self):
        r = post("noticias", self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        assert "id" in body["data"]
        TestNoticias.created_id = body["data"]["id"]

    def test_create_noticia_sem_campos(self):
        r = post("noticias", {})
        assert r.status_code == 400
        details = r.json().get("details", {})
        assert "titulo" in details
        assert "corpo" in details

    def test_list_noticias(self):
        r = get("noticias")
        assert r.status_code == 200
        assert isinstance(r.json()["data"], list)

    def test_get_noticia_por_id(self):
        assert TestNoticias.created_id
        r = get(f"noticias/{TestNoticias.created_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == TestNoticias.created_id

    def test_get_noticia_inexistente(self):
        r = get("noticias/999999")
        assert r.status_code == 404

    def test_update_noticia(self):
        assert TestNoticias.created_id
        r = put(f"noticias/{TestNoticias.created_id}", {"titulo": "Título Atualizado"})
        assert r.status_code == 200
        assert "Atualizado" in r.json()["data"]["titulo"]

    def test_update_noticia_inexistente(self):
        r = put("noticias/999999", {"titulo": "X"})
        assert r.status_code == 404

    def test_delete_noticia(self):
        assert TestNoticias.created_id
        r = delete(f"noticias/{TestNoticias.created_id}")
        assert r.status_code == 204

    def test_get_noticia_apos_delete(self):
        assert TestNoticias.created_id
        r = get(f"noticias/{TestNoticias.created_id}")
        assert r.status_code == 404


# ===========================================================================
# CRUD — ONGs
# ===========================================================================

class TestOngs:
    TS = str(int(time.time()))
    VALID = {
        "nome_instituicao": f"ONG Teste {TS}",
        "endereco_fisico": "Rua dos Testes, 0 - SP",
        "pix_doacao": f"ong.teste.{TS}@pix.test",
    }
    created_id = None

    def test_create_ong_sucesso(self):
        r = post("ongs", self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        TestOngs.created_id = body["data"]["id"]

    def test_create_ong_sem_endereco_nem_site(self):
        r = post("ongs", {
            "nome_instituicao": "Sem Contato",
            "pix_doacao": "contato@test.com"
        })
        assert r.status_code == 400
        details = r.json().get("details", {})
        assert "endereco_fisico" in details or "site" in details

    def test_create_ong_pix_invalido(self):
        r = post("ongs", {
            "nome_instituicao": "ONG Inválida",
            "site": "https://ong.com.br",
            "pix_doacao": "nao eh pix valido aqui!!!",
        })
        assert r.status_code == 400

    def test_create_ong_apenas_com_site(self):
        r = post("ongs", {
            "nome_instituicao": f"ONG Site {self.TS}",
            "site": "https://ong-site-only.org.br",
            "pix_doacao": f"sosite.{self.TS}@pix.test",
        })
        assert r.status_code == 201, r.text
        # Limpar
        oid = r.json()["data"]["id"]
        delete(f"ongs/{oid}")

    def test_list_ongs(self):
        r = get("ongs")
        assert r.status_code == 200
        assert isinstance(r.json()["data"], list)

    def test_get_ong_por_id(self):
        assert TestOngs.created_id
        r = get(f"ongs/{TestOngs.created_id}")
        assert r.status_code == 200

    def test_get_ong_inexistente(self):
        r = get("ongs/999999")
        assert r.status_code == 404

    def test_update_ong_nome(self):
        assert TestOngs.created_id
        r = put(f"ongs/{TestOngs.created_id}", {"nome_instituicao": "ONG Atualizada"})
        assert r.status_code == 200
        assert "Atualizada" in r.json()["data"]["nome_instituicao"]

    def test_update_ong_remove_endereco_sem_site_falha(self):
        """Não deve permitir remover endereço se não há site."""
        assert TestOngs.created_id
        r = put(f"ongs/{TestOngs.created_id}", {"endereco_fisico": None})
        # O existing não tem site, então deve retornar 400
        assert r.status_code == 400

    def test_delete_ong(self):
        assert TestOngs.created_id
        r = delete(f"ongs/{TestOngs.created_id}")
        assert r.status_code == 204

    def test_delete_ong_inexistente(self):
        r = delete("ongs/999999")
        assert r.status_code == 404


# ===========================================================================
# CRUD — Ajuda
# ===========================================================================

class TestAjuda:
    TS = str(int(time.time()))
    VALID = {
        "titulo": f"Como denunciar? {TS}",
        "corpo": "Para denunciar, acesse o portal e preencha o formulário.",
        "pix_doacao": f"ajuda.{TS}@pix.test",
    }
    created_id = None

    def test_create_ajuda_sucesso(self):
        r = post("ajuda", self.VALID)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        TestAjuda.created_id = body["data"]["id"]

    def test_create_ajuda_sem_campos(self):
        r = post("ajuda", {})
        assert r.status_code == 400
        details = r.json().get("details", {})
        assert "titulo" in details
        assert "corpo" in details
        assert "pix_doacao" in details

    def test_create_ajuda_pix_invalido(self):
        r = post("ajuda", {**self.VALID, "pix_doacao": "pix invalido !!!"})
        assert r.status_code == 400

    def test_list_ajuda(self):
        r = get("ajuda")
        assert r.status_code == 200
        assert isinstance(r.json()["data"], list)

    def test_get_ajuda_por_id(self):
        assert TestAjuda.created_id
        r = get(f"ajuda/{TestAjuda.created_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == TestAjuda.created_id

    def test_get_ajuda_inexistente(self):
        r = get("ajuda/999999")
        assert r.status_code == 404

    def test_update_ajuda(self):
        assert TestAjuda.created_id
        r = put(f"ajuda/{TestAjuda.created_id}", {"titulo": "Título Ajuda Atualizado"})
        assert r.status_code == 200
        assert "Atualizado" in r.json()["data"]["titulo"]

    def test_update_ajuda_inexistente(self):
        r = put("ajuda/999999", {"titulo": "X"})
        assert r.status_code == 404

    def test_delete_ajuda(self):
        assert TestAjuda.created_id
        r = delete(f"ajuda/{TestAjuda.created_id}")
        assert r.status_code == 204

    def test_get_ajuda_apos_delete(self):
        assert TestAjuda.created_id
        r = get(f"ajuda/{TestAjuda.created_id}")
        assert r.status_code == 404


# ===========================================================================
# Testes de paginação
# ===========================================================================

class TestPaginacao:
    def test_paginacao_limit(self):
        r = requests.get(f"{API}/noticias?limit=2&page=1")
        assert r.status_code == 200
        body = r.json()
        assert body["pagination"]["limit"] == 2
        assert len(body["data"]) <= 2

    def test_paginacao_page_invalida_usa_default(self):
        r = requests.get(f"{API}/noticias?page=abc&limit=xyz")
        assert r.status_code == 200  # não deve estourar 500
