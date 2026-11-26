from flask import Blueprint, request, session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from models.ajuda import (
    count_ajuda, list_ajuda, get_ajuda_by_id,
    create_ajuda_db, get_ajuda_by_idempotency_key, update_ajuda_db, delete_ajuda_db
)
from services.orientacoes import obter_orientacao_imediata, obter_canal_recomendado
from utils import parse_pagination, build_pagination, success_response, error_response

ajuda_bp = Blueprint('ajuda', __name__, url_prefix='/api')

SITUACOES_OCORRENCIA = {
    'violencia_em_andamento', 'risco_imediato', 'animal_ferido',
    'relato_passado', 'resgate'
}
TIPOS_ANIMAL = {'Animal doméstico', 'Animal Silvestre', 'Resgate e acolhimento'}
NIVEIS_URGENCIA = {
    'Ferimento grave', 'Engasgo', 'Convulsão', 'Doença contagiosa',
    'Envenenamento', 'Atropelamento',
    'Queimaduras ou exposição a produtos químicos', 'Não informado'
}


def _admin_required():
    return session.get('role') == 'admin'

@ajuda_bp.route('/ajuda', methods=['GET'])
def get_ajuda_list():
    if not _admin_required():
        return error_response("Acesso não autorizado.", "UNAUTHORIZED", status=403)
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_ajuda()
        rows = list_ajuda(limit, offset)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ajuda_bp.route('/ajuda/<int:aid>', methods=['GET'])
def get_ajuda(aid):
    if not _admin_required():
        return error_response("Acesso não autorizado.", "UNAUTHORIZED", status=403)
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
    situacao_ocorrencia = (data.get('situacao_ocorrencia') or '').strip() or 'relato_passado'
    idempotency_key = (data.get('idempotency_key') or '').strip()

    if not titulo:
        errors['titulo'] = 'Campo obrigatório'
    elif len(titulo) > 255:
        errors['titulo'] = 'Máximo 255 caracteres'
    if not corpo:
        errors['corpo'] = 'Campo obrigatório'
    if tipo_denuncia not in TIPOS_ANIMAL:
        errors['tipo_denuncia'] = 'Selecione um tipo de animal válido.'
    if nivel_urgencia not in NIVEIS_URGENCIA:
        errors['nivel_urgencia'] = 'Selecione uma condição válida.'
    if situacao_ocorrencia not in SITUACOES_OCORRENCIA:
        errors['situacao_ocorrencia'] = 'Selecione uma situação válida.'
    if idempotency_key:
        try:
            UUID(idempotency_key)
        except (ValueError, TypeError, AttributeError):
            errors['idempotency_key'] = 'Identificador de envio inválido'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    autor_nome = session.get('usuario_nome') or session.get('usuario_id') or 'Visitante'

    try:
        row, created = create_ajuda_db(
            titulo, corpo, autor_nome, tipo_denuncia, nivel_urgencia,
            situacao_ocorrencia, idempotency_key or None
        )
        if idempotency_key and not created and (
            row['titulo'] != titulo or row['corpo'] != corpo
            or row['autor'] != autor_nome or row['tipo_denuncia'] != tipo_denuncia
            or row['nivel_urgencia'] != nivel_urgencia
            or row['situacao_ocorrencia'] != situacao_ocorrencia
        ):
            return error_response(
                'Este envio já foi registrado com outros dados. Confira a confirmação antes de iniciar uma nova denúncia.',
                'IDEMPOTENCY_CONFLICT', status=409
            )
        orientacao = obter_orientacao_imediata(nivel_urgencia, tipo_denuncia)
        row['orientacao_imediata'] = orientacao
        row['canal_recomendado'] = obter_canal_recomendado(tipo_denuncia, situacao_ocorrencia)
        return success_response(
            row, "Denúncia registrada com sucesso.", 201 if created else 200
        )
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)


@ajuda_bp.route('/ajuda/confirmar/<string:idempotency_key>', methods=['GET'])
def confirmar_ajuda(idempotency_key):
    try:
        UUID(idempotency_key)
    except (ValueError, TypeError, AttributeError):
        return error_response('Identificador de envio inválido.', 'VALIDATION_ERROR', status=400)

    try:
        row = get_ajuda_by_idempotency_key(idempotency_key)
        if not row:
            return error_response('Ainda não há registro confirmado para este envio.', 'NOT_FOUND', status=404)
        # This endpoint only reconciles persistence; it does not expose complaint content.
        return success_response({
            'id': row['id'],
            'canal_recomendado': obter_canal_recomendado(
                row['tipo_denuncia'], row['situacao_ocorrencia']
            ),
        }, 'Denúncia registrada com sucesso.')
    except SQLAlchemyError as e:
        return error_response('Não foi possível confirmar o registro.', 'DB_ERROR', str(e), 500)

@ajuda_bp.route('/ajuda/<int:aid>', methods=['PUT'])
def update_ajuda(aid):
    if not _admin_required():
        return error_response("Acesso não autorizado.", "UNAUTHORIZED", status=403)
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
        if tipo not in TIPOS_ANIMAL:
            errors['tipo_denuncia'] = 'Selecione um tipo de animal válido.'
        else:
            update_data['tipo_denuncia'] = tipo

    if 'nivel_urgencia' in data:
        nivel = (data['nivel_urgencia'] or '').strip()
        if nivel not in NIVEIS_URGENCIA:
            errors['nivel_urgencia'] = 'Selecione uma condição válida.'
        else:
            update_data['nivel_urgencia'] = nivel

    if 'situacao_ocorrencia' in data:
        situacao = (data['situacao_ocorrencia'] or '').strip()
        if situacao not in SITUACOES_OCORRENCIA:
            errors['situacao_ocorrencia'] = 'Selecione uma situação válida.'
        else:
            update_data['situacao_ocorrencia'] = situacao

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
    if not _admin_required():
        return error_response("Acesso não autorizado.", "UNAUTHORIZED", status=403)
    try:
        ok = delete_ajuda_db(aid)
        if not ok:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return ('', 204)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)
