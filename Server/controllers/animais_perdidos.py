from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from flask import Blueprint, request, session, send_file
from io import BytesIO

from models.animais_perdidos import (
    cadastrar_animal,
    listar_animais,
    buscar_animal,
    obter_imagem_animal,
    atualizar_animal,
    excluir_animal,
    marcar_animal_encontrado,
)
from utils import success_response, error_response


animais_perdidos_bp = Blueprint(
    "animais_perdidos",
    __name__,
    url_prefix="/api"
)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def _ler_imagem(upload):
    if not upload or not upload.filename:
        return None, None, None

    if upload.mimetype not in ALLOWED_IMAGE_TYPES:
        return None, None, "Envie uma imagem JPG, PNG, WEBP ou GIF."

    conteudo = upload.read(MAX_IMAGE_SIZE + 1)
    if len(conteudo) > MAX_IMAGE_SIZE:
        return None, None, "A imagem deve ter no máximo 5 MB."

    return conteudo, upload.mimetype, None


def _validar_campos(data):
    valores = {
        "nome": (data.get("nome") or "").strip(),
        "especie": (data.get("especie") or "").strip(),
        "sexo": (data.get("sexo") or "Não informado").strip(),
        "descricao": (data.get("descricao") or "").strip(),
        "local": (data.get("local") or "").strip(),
        "data_ocorrido": (data.get("data_ocorrido") or "").strip(),
        "contato": (data.get("contato") or "").strip(),
        "status": (data.get("status") or "Perdido").strip(),
    }

    erros = {}

    obrigatorios = (
        "nome",
        "especie",
        "descricao",
        "local",
        "data_ocorrido",
        "contato",
    )
    for campo in obrigatorios:
        if not valores[campo]:
            erros[campo] = "Campo obrigatório."

    if valores["nome"] and len(valores["nome"]) > 120:
        erros["nome"] = "Use no máximo 120 caracteres."

    if valores["local"] and len(valores["local"]) > 255:
        erros["local"] = "Use no máximo 255 caracteres."

    if valores["contato"] and len(valores["contato"]) > 180:
        erros["contato"] = "Use no máximo 180 caracteres."

    if valores["status"] not in ("Perdido", "Encontrado"):
        erros["status"] = "Situação inválida."

    if valores["data_ocorrido"]:
        try:
            valores["data_ocorrido"] = date.fromisoformat(
                valores["data_ocorrido"]
            )
        except ValueError:
            erros["data_ocorrido"] = "Informe uma data válida."

    return valores, erros


def _admin_only():
    return session.get("role") == "admin"


@animais_perdidos_bp.route("/animais-perdidos", methods=["GET"])
def get_animais_perdidos():
    try:
        limite = request.args.get("limit", type=int)
        if limite is not None:
            limite = max(1, min(limite, 50))
        current_user_id = (
            session.get("usuario_id")
            if session.get("role") in ("admin", "user") else None
        )
        rows = listar_animais(limite, current_user_id)
        return success_response(rows)
    except SQLAlchemyError as exc:
        return error_response(
            "Não foi possível carregar os animais.",
            "DB_ERROR",
            str(exc),
            500
        )


@animais_perdidos_bp.route("/animais-perdidos", methods=["POST"])
def post_animal_perdido():
    if session.get("role") not in ("admin", "user") or session.get("usuario_id") is None:
        return error_response("Entre na sua conta para publicar um animal.", "UNAUTHORIZED", status=401)

    dados, erros = _validar_campos(request.form)

    imagem_blob, imagem_mime, erro_imagem = _ler_imagem(
        request.files.get("imagem")
    )
    if erro_imagem:
        erros["imagem"] = erro_imagem

    dados["autor"] = str(
        session.get("usuario_nome")
        or session.get("usuario_id")
        or "Visitante"
    )
    dados["usuario_id"] = str(session.get("usuario_id"))

    if erros:
        return error_response(
            "Verifique os campos do cadastro.",
            "VALIDATION_ERROR",
            erros,
            400
        )

    try:
        animal = cadastrar_animal(
            dados,
            imagem_blob=imagem_blob,
            imagem_mime=imagem_mime
        )
        return success_response(
            animal,
            "Animal cadastrado com sucesso!",
            201
        )
    except SQLAlchemyError as exc:
        return error_response(
            "Não foi possível salvar o cadastro.",
            "DB_ERROR",
            str(exc),
            500
        )


@animais_perdidos_bp.route(
    "/animais-perdidos/<int:animal_id>/status",
    methods=["PATCH"]
)
def patch_status_animal_perdido(animal_id):
    if session.get("role") not in ("admin", "user") or session.get("usuario_id") is None:
        return error_response("Entre na sua conta para alterar a publicação.", "UNAUTHORIZED", status=401)

    dados = request.get_json(silent=True) or {}
    if dados.get("status") != "Encontrado":
        return error_response(
            "A ação disponível é marcar o animal como encontrado.",
            "VALIDATION_ERROR",
            status=400
        )

    try:
        outcome, animal = marcar_animal_encontrado(
            animal_id, session.get("usuario_id")
        )
        if outcome == "updated":
            animal["pode_marcar_encontrado"] = False
            return success_response(animal, "Publicação atualizada para encontrado.")
        if outcome == "not_found":
            return error_response("Animal não encontrado.", "NOT_FOUND", status=404)
        if outcome == "forbidden":
            return error_response(
                "Somente quem criou esta publicação pode marcá-la como encontrada.",
                "FORBIDDEN",
                status=403
            )
        return error_response(
            "Esta publicação já está marcada como encontrada.",
            "ALREADY_FOUND",
            status=409
        )
    except SQLAlchemyError as exc:
        return error_response(
            "Não foi possível atualizar a publicação.",
            "DB_ERROR",
            str(exc),
            500
        )




@animais_perdidos_bp.route(
    "/animais-perdidos/<int:animal_id>/imagem",
    methods=["GET"]
)
def imagem_animal(animal_id):
    try:
        imagem = obter_imagem_animal(animal_id)
        if not imagem:
            return error_response(
                "Imagem não encontrada.",
                "NOT_FOUND",
                status=404
            )

        blob, mime = imagem
        return send_file(
            BytesIO(blob),
            mimetype=mime,
            max_age=3600
        )
    except SQLAlchemyError as exc:
        return error_response(
            "Não foi possível carregar a imagem.",
            "DB_ERROR",
            str(exc),
            500
        )


@animais_perdidos_bp.route(
    "/animais-perdidos/<int:animal_id>",
    methods=["PUT"]
)
def put_animal_perdido(animal_id):
    if not _admin_only():
        return error_response(
            "Acesso não autorizado.",
            "UNAUTHORIZED",
            status=401
        )

    existente = buscar_animal(animal_id)
    if not existente:
        return error_response(
            "Animal não encontrado.",
            "NOT_FOUND",
            status=404
        )

    dados, erros = _validar_campos(request.form)

    imagem_blob = imagem_mime = None
    alterar_imagem = False
    remover_imagem = request.form.get("remover_imagem") == "1"

    upload = request.files.get("imagem")
    if upload and upload.filename:
        imagem_blob, imagem_mime, erro_imagem = _ler_imagem(upload)
        alterar_imagem = not bool(erro_imagem)
        if erro_imagem:
            erros["imagem"] = erro_imagem

    if erros:
        return error_response(
            "Verifique os campos da edição.",
            "VALIDATION_ERROR",
            erros,
            400
        )

    dados["autor"] = existente["autor"]

    try:
        atualizado = atualizar_animal(
            animal_id,
            dados,
            imagem_blob=imagem_blob,
            imagem_mime=imagem_mime,
            alterar_imagem=alterar_imagem,
            remover_imagem=remover_imagem
        )
        return success_response(
            atualizado,
            "Cadastro atualizado com sucesso."
        )
    except SQLAlchemyError as exc:
        return error_response(
            "Não foi possível atualizar o cadastro.",
            "DB_ERROR",
            str(exc),
            500
        )


@animais_perdidos_bp.route(
    "/animais-perdidos/<int:animal_id>",
    methods=["DELETE"]
)
def delete_animal_perdido(animal_id):
    if not _admin_only():
        return error_response(
            "Acesso não autorizado.",
            "UNAUTHORIZED",
            status=401
        )

    try:
        if not excluir_animal(animal_id):
            return error_response(
                "Animal não encontrado.",
                "NOT_FOUND",
                status=404
            )
        return "", 204
    except SQLAlchemyError as exc:
        return error_response(
            "Não foi possível excluir o cadastro.",
            "DB_ERROR",
            str(exc),
            500
        )
