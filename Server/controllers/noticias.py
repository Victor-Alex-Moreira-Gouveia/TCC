from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from models.noticias import (
    count_noticias,
    create_noticia,
    delete_noticia_db,
    get_noticia_by_id,
    list_noticias,
    update_noticia_db,
)
from utils import build_pagination, error_response, parse_pagination, success_response

noticias_bp = Blueprint('noticias', __name__, url_prefix='/api')


@noticias_bp.route('/noticias', methods=['GET'])
def get_noticias():
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_noticias()
        rows = list_noticias(limit, offset)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['GET'])
def get_noticia(nid):
    try:
        row = get_noticia_by_id(nid)
        if not row:
            return error_response('Recurso não encontrado', 'NOT_FOUND', status=404)
        return success_response(row)
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias', methods=['POST'])
def create_noticia_route():
    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'

    if errors:
        return error_response('Validação falhou', 'VALIDATION_ERROR', errors, 400)

    try:
        new_id = create_noticia(titulo, corpo)
        row = get_noticia_by_id(new_id)
        return success_response(row, 'Criado com sucesso', 201)
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['PUT'])
def update_noticia_route(nid):
    data = request.get_json(silent=True) or {}
    existing = get_noticia_by_id(nid)
    if not existing:
        return error_response('Recurso não encontrado', 'NOT_FOUND', status=404)

    errors = {}
    update_data = {}

    if 'titulo' in data:
        titulo = (data['titulo'] or '').strip()
        if not titulo:
            errors['titulo'] = 'Não pode ser vazio'
        else:
            update_data['titulo'] = titulo

    if 'corpo' in data:
        corpo = (data['corpo'] or '').strip()
        if not corpo:
            errors['corpo'] = 'Não pode ser vazio'
        else:
            update_data['corpo'] = corpo

    if errors:
        return error_response('Validação falhou', 'VALIDATION_ERROR', errors, 400)

    if not update_data:
        return error_response('Nenhum campo para atualizar', 'NO_FIELDS', status=400)

    try:
        updated = update_noticia_db(nid, update_data)
        return success_response(updated, 'Atualizado com sucesso')
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['DELETE'])
def delete_noticia_route(nid):
    try:
        ok = delete_noticia_db(nid)
        if not ok:
            return error_response('Recurso não encontrado', 'NOT_FOUND', status=404)
        return '', 204
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)
