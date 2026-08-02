from flask import Blueprint, request, session
from mysql.connector import DatabaseError
from models.ajuda import (
    count_ajuda, list_ajuda, get_ajuda_by_id,
    create_ajuda_db, update_ajuda_db, delete_ajuda_db
)
from utils import parse_pagination, build_pagination, success_response, error_response, validate_pix

ajuda_bp = Blueprint('ajuda', __name__, url_prefix='/api')


@ajuda_bp.route('/ajuda', methods=['GET'])
def get_ajuda_list():
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_ajuda()
        rows = list_ajuda(limit, offset)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@ajuda_bp.route('/ajuda/<int:aid>', methods=['GET'])
def get_ajuda(aid):
    try:
        row = get_ajuda_by_id(aid)
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@ajuda_bp.route('/ajuda', methods=['POST'])
def create_ajuda():
    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()
    pix = (data.get('pix_doacao') or '').strip()

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    elif len(titulo) > 255:
        errors['titulo'] = 'Máximo 255 caracteres'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'
    if not pix:
        errors['pix_doacao'] = 'Campo obrigatório'
    elif not validate_pix(pix):
        errors['pix_doacao'] = 'Formato de chave PIX inválido'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if session.get('role') == 'guest':
        autor_nome = session.get('usuario_id', 'anon')
    else:
        autor_nome = session.get('usuario_nome', 'Visitante Anônimo')

    try:
        new_id = create_ajuda_db(titulo, corpo, pix, autor_nome)
        row = get_ajuda_by_id(new_id)
        return success_response(row, "Criado com sucesso", 201)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@ajuda_bp.route('/ajuda/<int:aid>', methods=['PUT'])
def update_ajuda(aid):
    data = request.get_json(silent=True) or {}

    try:
        existing = get_ajuda_by_id(aid)
        if not existing:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    errors = {}
    updates = []
    params = []

    if 'titulo' in data:
        titulo = (data['titulo'] or '').strip()
        if not titulo:
            errors['titulo'] = 'Não pode ser vazio'
        elif len(titulo) > 255:
            errors['titulo'] = 'Máximo 255 caracteres'
        else:
            updates.append("titulo = %s")
            params.append(titulo)

    if 'corpo' in data:
        corpo = (data['corpo'] or '').strip()
        if not corpo:
            errors['corpo'] = 'Não pode ser vazio'
        else:
            updates.append("corpo = %s")
            params.append(corpo)

    if 'pix_doacao' in data:
        pix = (data['pix_doacao'] or '').strip()
        if not pix:
            errors['pix_doacao'] = 'Não pode ser vazio'
        elif not validate_pix(pix):
            errors['pix_doacao'] = 'Formato de chave PIX inválido'
        else:
            updates.append("pix_doacao = %s")
            params.append(pix)

    if 'autor' in data:
        autor = (data['autor'] or '').strip()
        if not autor:
            errors['autor'] = 'Não pode ser vazio'
        else:
            updates.append("autor = %s")
            params.append(autor)

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not updates:
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        updated = update_ajuda_db(aid, ', '.join(updates), params)
        return success_response(updated, "Atualizado com sucesso")
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@ajuda_bp.route('/ajuda/<int:aid>', methods=['DELETE'])
def delete_ajuda(aid):
    try:
        ok = delete_ajuda_db(aid)
        if not ok:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return ('', 204)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)
