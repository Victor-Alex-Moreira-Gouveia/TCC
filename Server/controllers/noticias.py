from flask import Blueprint, request, session
from mysql.connector import DatabaseError
from models.noticias import (
    count_noticias, list_noticias, get_noticia_by_id,
    create_noticia, update_noticia_db, delete_noticia_db
)
from utils import parse_pagination, build_pagination, success_response, error_response

noticias_bp = Blueprint('noticias', __name__, url_prefix='/api')


@noticias_bp.route('/noticias', methods=['GET'])
def get_noticias():
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_noticias()
        rows = list_noticias(limit, offset)
        # serialize datetime if present
        for r in rows:
            if r.get('data_hora'):
                try:
                    r['data_hora'] = r['data_hora'].isoformat()
                except Exception:
                    pass
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['GET'])
def get_noticia(nid):
    try:
        row = get_noticia_by_id(nid)
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        if row.get('data_hora'):
            try:
                row['data_hora'] = row['data_hora'].isoformat()
            except Exception:
                pass
        return success_response(row)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@noticias_bp.route('/noticias', methods=['POST'])
def create_noticia_route():
    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    elif len(titulo) > 255:
        errors['titulo'] = 'Máximo 255 caracteres'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    autor_nome = session.get('usuario_nome', 'Visitante Anônimo')
    corpo_com_autor = f"{corpo}\n\n— Publicado por: {autor_nome}"

    try:
        new_id = create_noticia(titulo, corpo_com_autor)
        row = get_noticia_by_id(new_id)
        if row.get('data_hora'):
            try:
                row['data_hora'] = row['data_hora'].isoformat()
            except Exception:
                pass
        return success_response(row, "Criado com sucesso", 201)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['PUT'])
def update_noticia_route(nid):
    data = request.get_json(silent=True) or {}
    try:
        existing = get_noticia_by_id(nid)
        if not existing:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

    updates = []
    params = []
    errors = {}

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

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    if not updates:
        return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

    try:
        updated = update_noticia_db(nid, ', '.join(updates), params)
        if updated.get('data_hora'):
            try:
                updated['data_hora'] = updated['data_hora'].isoformat()
            except Exception:
                pass
        return success_response(updated, "Atualizado com sucesso")
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['DELETE'])
def delete_noticia_route(nid):
    try:
        ok = delete_noticia_db(nid)
        if not ok:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return ('', 204)
    except DatabaseError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)
