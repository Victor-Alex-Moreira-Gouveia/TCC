import html
from flask import Blueprint, request, session
from sqlalchemy.exc import SQLAlchemyError

from models.noticias import (
    count_noticias,
    create_comentario,
    create_noticia,
    delete_comentario_db,
    delete_noticia_db,
    get_comentario_by_id,
    get_noticia_by_id,
    list_comentarios,
    list_noticias,
    update_comentario_db,
    update_noticia_db,
    adicionar_curtida,
    remover_curtida,
)
from utils import build_pagination, error_response, parse_pagination, success_response

noticias_bp = Blueprint('noticias', __name__, url_prefix='/api')


def _is_authenticated():
    return session.get('role') in ('admin', 'user')


def _is_admin():
    return session.get('role') == 'admin'


# ---------------------------------------------------------------------------
# Notícias
# ---------------------------------------------------------------------------

@noticias_bp.route('/noticias', methods=['GET'])
def get_noticias():
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    page, limit, offset = parse_pagination(request.args)
    current_user_id = session.get('usuario_id')
    try:
        total = count_noticias()
        rows = list_noticias(limit, offset, current_user_id=current_user_id)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['GET'])
def get_noticia(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    current_user_id = session.get('usuario_id')
    try:
        row = get_noticia_by_id(nid, current_user_id=current_user_id)
        if not row:
            return error_response('Recurso não encontrado', 'NOT_FOUND', status=404)
        return success_response(row)
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias', methods=['POST'])
def create_noticia_route():
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    if not _is_admin():
        return error_response('Apenas administradores podem criar notícias', 'FORBIDDEN', status=403)

    data = request.get_json(silent=True) or {}
    errors = {}

    titulo = (data.get('titulo') or '').strip()
    corpo = (data.get('corpo') or '').strip()
    imagem_url = (data.get('imagem_url') or data.get('imagem') or '').strip() or None

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'

    if errors:
        return error_response('Validação falhou', 'VALIDATION_ERROR', errors, 400)

    try:
        new_id = create_noticia(titulo, corpo, imagem_url=imagem_url)
        row = get_noticia_by_id(new_id, current_user_id=session.get('usuario_id'))
        return success_response(row, 'Notícia cadastrada com sucesso.', 201)
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['PUT'])
def update_noticia_route(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    if not _is_admin():
        return error_response('Apenas administradores podem alterar notícias', 'FORBIDDEN', status=403)

    existing = get_noticia_by_id(nid)
    if not existing:
        return error_response('Recurso não encontrado', 'NOT_FOUND', status=404)

    data = request.get_json(silent=True) or {}
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

    if 'imagem_url' in data or 'imagem' in data:
        raw_img = (data.get('imagem_url') if 'imagem_url' in data else data.get('imagem')) or ''
        img = raw_img.strip()
        update_data['imagem_url'] = img if img else None

    if errors:
        return error_response('Validação falhou', 'VALIDATION_ERROR', errors, 400)

    if not update_data:
        return error_response('Nenhum campo para atualizar', 'NO_FIELDS', status=400)

    try:
        updated = update_noticia_db(nid, update_data)
        return success_response(updated, 'Notícia atualizada com sucesso.')
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>', methods=['DELETE'])
def delete_noticia_route(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    if not _is_admin():
        return error_response('Apenas administradores podem remover notícias', 'FORBIDDEN', status=403)

    try:
        ok = delete_noticia_db(nid)
        if not ok:
            return error_response('Recurso não encontrado', 'NOT_FOUND', status=404)
        return '', 204
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# Comentários
# ---------------------------------------------------------------------------

@noticias_bp.route('/noticias/<int:nid>/comentarios', methods=['GET'])
def get_comentarios_route(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    noticia = get_noticia_by_id(nid)
    if not noticia:
        return error_response('Notícia não encontrada', 'NOT_FOUND', status=404)

    try:
        comments = list_comentarios(nid)
        return success_response(comments)
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>/comentarios', methods=['POST'])
def create_comentario_route(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    noticia = get_noticia_by_id(nid)
    if not noticia:
        return error_response('Notícia não encontrada', 'NOT_FOUND', status=404)

    data = request.get_json(silent=True) or {}
    raw_texto = (data.get('texto') or '').strip()

    if not raw_texto:
        return error_response('O comentário não pode ser vazio', 'VALIDATION_ERROR', {'texto': 'Campo obrigatório'}, 400)

    if len(raw_texto) > 1000:
        return error_response('O comentário excede o tamanho máximo de 1000 caracteres', 'VALIDATION_ERROR', {'texto': 'Máximo 1000 caracteres'}, 400)

    # Escapar XSS
    texto_seguro = html.escape(raw_texto)
    usuario_id = session.get('usuario_id')
    autor_nome = session.get('usuario_nome') or 'Usuário Registrado'

    try:
        novo = create_comentario(nid, str(usuario_id), autor_nome, texto_seguro)
        return success_response(novo, 'Comentário adicionado com sucesso.', 201)
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/comentarios/<int:cid>', methods=['PUT'])
def update_comentario_route(cid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    c = get_comentario_by_id(cid)
    if not c:
        return error_response('Comentário não encontrado', 'NOT_FOUND', status=404)

    current_user_id = str(session.get('usuario_id'))
    if not _is_admin() and str(c['usuario_id']) != current_user_id:
        return error_response('Você só pode editar seus próprios comentários', 'FORBIDDEN', status=403)

    data = request.get_json(silent=True) or {}
    raw_texto = (data.get('texto') or '').strip()

    if not raw_texto:
        return error_response('O comentário não pode ser vazio', 'VALIDATION_ERROR', {'texto': 'Campo obrigatório'}, 400)

    if len(raw_texto) > 1000:
        return error_response('O comentário excede o tamanho máximo de 1000 caracteres', 'VALIDATION_ERROR', {'texto': 'Máximo 1000 caracteres'}, 400)

    texto_seguro = html.escape(raw_texto)

    try:
        updated = update_comentario_db(cid, texto_seguro)
        return success_response(updated, 'Comentário atualizado com sucesso.')
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/comentarios/<int:cid>', methods=['DELETE'])
def delete_comentario_route(cid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    c = get_comentario_by_id(cid)
    if not c:
        return error_response('Comentário não encontrado', 'NOT_FOUND', status=404)

    current_user_id = str(session.get('usuario_id'))
    if not _is_admin() and str(c['usuario_id']) != current_user_id:
        return error_response('Você só pode excluir seus próprios comentários', 'FORBIDDEN', status=403)

    try:
        delete_comentario_db(cid)
        return '', 204
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# Curtidas
# ---------------------------------------------------------------------------

@noticias_bp.route('/noticias/<int:nid>/curtida', methods=['POST'])
def add_curtida_route(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    noticia = get_noticia_by_id(nid, current_user_id=session.get('usuario_id'))
    if not noticia:
        return error_response('Notícia não encontrada', 'NOT_FOUND', status=404)

    try:
        adicionar_curtida(nid, session.get('usuario_id'))
        updated_noticia = get_noticia_by_id(nid, current_user_id=session.get('usuario_id'))
        return success_response(updated_noticia, 'Curtida registrada com sucesso.')
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)


@noticias_bp.route('/noticias/<int:nid>/curtida', methods=['DELETE'])
def remove_curtida_route(nid):
    if not _is_authenticated():
        return error_response('Acesso não autorizado', 'UNAUTHORIZED', status=401)

    noticia = get_noticia_by_id(nid, current_user_id=session.get('usuario_id'))
    if not noticia:
        return error_response('Notícia não encontrada', 'NOT_FOUND', status=404)

    try:
        remover_curtida(nid, session.get('usuario_id'))
        updated_noticia = get_noticia_by_id(nid, current_user_id=session.get('usuario_id'))
        return success_response(updated_noticia, 'Curtida removida com sucesso.')
    except SQLAlchemyError as exc:
        return error_response('Erro interno do servidor', 'DB_ERROR', str(exc), 500)
