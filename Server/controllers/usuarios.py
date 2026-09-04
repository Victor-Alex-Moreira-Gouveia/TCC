from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.usuarios import count_users, list_users, get_usuario_by_id, create_usuario, update_usuario_db, delete_usuario_db
import re
import math

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api')

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def validate_email(email: str):
    return EMAIL_RE.match(email.strip()) is not None

def parse_pagination(args):
    try:
        page = max(1, int(args.get('page', 1)))
        limit = max(1, min(100, int(args.get('limit', 10))))
    except (ValueError, TypeError):
        page, limit = 1, 10
    offset = (page - 1) * limit
    return page, limit, offset

def build_pagination(total, page, limit):
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if limit else 1
    }

def success_response(data, message="Operação realizada com sucesso", status=200, pagination=None):
    body = {"success": True, "data": data, "message": message}
    if pagination:
        body["pagination"] = pagination
    return jsonify(body), status

def error_response(message, code="ERROR", details=None, status=400):
    body = {"success": False, "error": message, "code": code}
    if details:
        body["details"] = details
    return jsonify(body), status

@usuarios_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_users()
        rows = list_users(limit, offset)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@usuarios_bp.route('/usuarios/<int:uid>', methods=['GET'])
def get_usuario(uid):
    try:
        row = get_usuario_by_id(uid)
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@usuarios_bp.route('/usuarios', methods=['POST'])
def create_usuario_route():
    data = request.get_json(silent=True) or {}
    errors = {}

    nome = (data.get('nome_usuario') or '').strip()
    email = (data.get('email') or '').strip()
    senha = (data.get('senha') or '').strip()

    if not nome:
        errors['nome_usuario'] = 'Campo obrigatório'
    if not email:
        errors['email'] = 'Campo obrigatório'
    elif not validate_email(email):
        errors['email'] = 'Formato de e-mail inválido'
    if not senha:
        errors['senha'] = 'Campo obrigatório'
    elif len(senha) < 8:
        errors['senha'] = 'A senha deve ter no mínimo 8 caracteres'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    senha_hash = generate_password_hash(senha)

    try:
        new_id = create_usuario(nome, email, senha_hash)
        return success_response({"id": new_id, "nome_usuario": nome, "email": email}, "Criado com sucesso", 201)
    except IntegrityError:
        return error_response("Email já registrado no sistema", "EMAIL_CONFLICT", status=409)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@usuarios_bp.route('/usuarios/<int:uid>', methods=['PUT'])
def update_usuario_route(uid):
    data = request.get_json(silent=True) or {}

    existing = get_usuario_by_id(uid)
    if not existing:
        return error_response("Recurso não encontrado", "NOT_FOUND", status=404)

    update_data = {}
    errors = {}

    if 'nome_usuario' in data:
        nome = (data['nome_usuario'] or '').strip()
        if not nome:
            errors['nome_usuario'] = 'Não pode ser vazio'
        else:
            update_data['nome_usuario'] = nome

    if 'email' in data:
        email = (data['email'] or '').strip()
        if not email:
            errors['email'] = 'Não pode ser vazio'
        elif not validate_email(email):
            errors['email'] = 'Formato de e-mail inválido'
        else:
            update_data['email'] = email

    if 'senha' in data:
        senha = (data['senha'] or '').strip()
        if len(senha) < 8:
            errors['senha'] = 'A senha deve ter no mínimo 8 caracteres'
        else:
            update_data['senha'] = generate_password_hash(senha)

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not update_data:
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        updated = update_usuario_db(uid, update_data)
        return success_response(updated, "Atualizado com sucesso")
    except IntegrityError:
        return error_response("Email já registrado no sistema", "EMAIL_CONFLICT", status=409)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@usuarios_bp.route('/usuarios/<int:uid>', methods=['DELETE'])
def delete_usuario_route(uid):
    try:
        ok = delete_usuario_db(uid)
        if not ok:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return ('', 204)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)