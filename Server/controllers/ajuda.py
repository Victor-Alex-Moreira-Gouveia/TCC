from flask import Blueprint, request, session
from sqlalchemy.exc import SQLAlchemyError
from models.ajuda import (
    count_ajuda, list_ajuda, get_ajuda_by_id,
    create_ajuda_db, update_ajuda_db, delete_ajuda_db
)
from services.orientacoes import obter_orientacao_imediata
from utils import parse_pagination, build_pagination, success_response, error_response

ajuda_bp = Blueprint('ajuda', __name__, url_prefix='/api')

@ajuda_bp.route('/ajuda', methods=['GET'])
def get_ajuda_list():
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_ajuda()
        rows = list_ajuda(limit, offset)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ajuda_bp.route('/ajuda/<int:aid>', methods=['GET'])
def get_ajuda(aid):
    try:
        row = get_ajuda_by_id(aid)
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ajuda_bp.route('/ajuda', methods=['POST'])
def create_ajuda():
    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()
    tipo_denuncia = (data.get('tipo_denuncia') or '').strip() or 'Animal doméstico'
    nivel_urgencia = (data.get('nivel_urgencia') or '').strip() or 'Não informado'

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    elif len(titulo) > 255:
        errors['titulo'] = 'Máximo 255 caracteres'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    autor_nome = session.get('usuario_nome') or session.get('usuario_id') or 'Visitante'

    try:
        new_id = create_ajuda_db(titulo, corpo, autor_nome, tipo_denuncia, nivel_urgencia)
        row = get_ajuda_by_id(new_id)
        orientacao = obter_orientacao_imediata(nivel_urgencia, tipo_denuncia)
        if row:
            row['orientacao_imediata'] = orientacao
        return success_response(row, "Denúncia registrada com sucesso.", 201)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ajuda_bp.route('/ajuda/<int:aid>', methods=['PUT'])
def update_ajuda(aid):
    data = request.get_json(silent=True) or {}

    try:
        existing = get_ajuda_by_id(aid)
        if not existing:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    errors = {}
    update_data = {}

    if 'titulo' in data:
        titulo = (data['titulo'] or '').strip()
        if not titulo:
            errors['titulo'] = 'Não pode ser vazio'
        elif len(titulo) > 255:
            errors['titulo'] = 'Máximo 255 caracteres'
        else:
            update_data['titulo'] = titulo

    if 'corpo' in data:
        corpo = (data['corpo'] or '').strip()
        if not corpo:
            errors['corpo'] = 'Não pode ser vazio'
        else:
            update_data['corpo'] = corpo

    if 'autor' in data:
        autor = (data['autor'] or '').strip()
        if not autor:
            errors['autor'] = 'Não pode ser vazio'
        else:
            update_data['autor'] = autor

    if 'tipo_denuncia' in data:
        tipo = (data['tipo_denuncia'] or '').strip()
        if not tipo:
            errors['tipo_denuncia'] = 'Não pode ser vazio'
        else:
            update_data['tipo_denuncia'] = tipo

    if 'nivel_urgencia' in data:
        nivel = (data['nivel_urgencia'] or '').strip()
        if not nivel:
            errors['nivel_urgencia'] = 'Não pode ser vazio'
        else:
            update_data['nivel_urgencia'] = nivel

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not update_data:
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        updated = update_ajuda_db(aid, update_data)
        return success_response(updated, "Atualizado com sucesso")
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ajuda_bp.route('/ajuda/<int:aid>', methods=['DELETE'])
def delete_ajuda(aid):
    try:
        ok = delete_ajuda_db(aid)
        if not ok:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return ('', 204)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)