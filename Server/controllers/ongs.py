from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError
from models.ongs import (
    count_ongs, list_ongs, get_ong_by_id,
    create_ong, update_ong_db, delete_ong_db
)
from utils import parse_pagination, build_pagination, success_response, error_response, validate_pix

ongs_bp = Blueprint('ongs', __name__, url_prefix='/api')

def _validate_ong_fields(data, require_all=True):
    errors = {}

    nome = (data.get('nome_instituicao') or '').strip()
    endereco = (data.get('endereco_fisico') or '').strip() or None
    site = (data.get('site') or '').strip() or None
    pix = (data.get('pix_doacao') or '').strip()

    if require_all and not nome:
        errors['nome_instituicao'] = 'Campo obrigatório'
    elif nome and len(nome) > 150:
        errors['nome_instituicao'] = 'Máximo 150 caracteres'

    if require_all and not pix:
        errors['pix_doacao'] = 'Campo obrigatório'
    elif pix and not validate_pix(pix):
        errors['pix_doacao'] = 'Formato de chave PIX inválido (CPF, CNPJ, e-mail, telefone ou UUID)'

    if require_all:
        if not endereco and not site:
            errors['endereco_fisico'] = 'Ao menos endereço físico ou site deve ser preenchido'
            errors['site'] = 'Ao menos endereço físico ou site deve ser preenchido'

    return errors, nome, endereco, site, pix

@ongs_bp.route('/ongs', methods=['GET'])
def get_ongs():
    page, limit, offset = parse_pagination(request.args)
    try:
        total = count_ongs()
        rows = list_ongs(limit, offset)
        return success_response(rows, pagination=build_pagination(total, page, limit))
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ongs_bp.route('/ongs/<int:oid>', methods=['GET'])
def get_ong(oid):
    try:
        row = get_ong_by_id(oid)
        if not row:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return success_response(row)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ongs_bp.route('/ongs', methods=['POST'])
def create_ong_route():
    data = request.get_json(silent=True) or {}
    errors, nome, endereco, site, pix = _validate_ong_fields(data, require_all=True)

    if not errors and not endereco and not site:
        errors['endereco_fisico'] = 'Ao menos endereço físico ou site deve ser preenchido'

    if errors:
        return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

    try:
        new_id = create_ong(nome, endereco, site, pix)
        row = get_ong_by_id(new_id)
        return success_response(row, "Criado com sucesso", 201)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

@ongs_bp.route('/ongs/<int:oid>', methods=['PUT'])
def update_ong_route(oid):
    try:
        data = request.get_json(silent=True) or {}
        try:
            existing = get_ong_by_id(oid)
            if not existing:
                return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        except SQLAlchemyError as e:
            return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)

        errors = {}
        update_data = {}

        if 'nome_instituicao' in data:
            nome = (data['nome_instituicao'] or '').strip()
            if not nome:
                errors['nome_instituicao'] = 'Não pode ser vazio'
            elif len(nome) > 150:
                errors['nome_instituicao'] = 'Máximo 150 caracteres'
            else:
                update_data['nome_instituicao'] = nome

        if 'pix_doacao' in data:
            pix = (data['pix_doacao'] or '').strip()
            if not pix:
                errors['pix_doacao'] = 'Não pode ser vazio'
            elif not validate_pix(pix):
                errors['pix_doacao'] = 'Formato de chave PIX inválido'
            else:
                update_data['pix_doacao'] = pix

        if 'endereco_fisico' in data:
            update_data['endereco_fisico'] = (data['endereco_fisico'] or '').strip() or None

        if 'site' in data:
            update_data['site'] = (data['site'] or '').strip() or None

        novo_endereco = data.get('endereco_fisico', existing.get('endereco_fisico'))
        novo_site = data.get('site', existing.get('site'))
        
        if not novo_endereco and not novo_site:
            errors['endereco_fisico'] = 'Ao menos endereço físico ou site deve ser preenchido'

        if errors:
            return error_response("Validação falhou", "VALIDATION_ERROR", errors, 400)

        if not update_data:
            return error_response("Nenhum campo para atualizar", "NO_FIELDS", status=400)

        try:
            updated = update_ong_db(oid, update_data)
            return success_response(updated, "Atualizado com sucesso")
        except SQLAlchemyError as e:
            return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)
    except Exception as e:
        import traceback
        return error_response("Erro interno do servidor", "EXCEPTION", traceback.format_exc(), 500)

@ongs_bp.route('/ongs/<int:oid>', methods=['DELETE'])
def delete_ong_route(oid):
    try:
        ok = delete_ong_db(oid)
        if not ok:
            return error_response("Recurso não encontrado", "NOT_FOUND", status=404)
        return ('', 204)
    except SQLAlchemyError as e:
        return error_response("Erro interno do servidor", "DB_ERROR", str(e), 500)