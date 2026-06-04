from flask import Blueprint, jsonify

bp = Blueprint('ongs', __name__, url_prefix='/ongs')

@bp.route('/', methods=['GET'])
def listar_ongs():
    """Lista todas as ONGs"""
    return jsonify({"mensagem": "Listar ONGs"}), 200

@bp.route('/<int:id>', methods=['GET'])
def obter_ong(id):
    """Obtém uma ONG específica"""
    return jsonify({"mensagem": f"Obter ONG {id}"}), 200

@bp.route('/', methods=['POST'])
def criar_ong():
    """Cria uma nova ONG"""
    return jsonify({"mensagem": "Criar ONG"}), 201

@bp.route('/<int:id>', methods=['PUT'])
def atualizar_ong(id):
    """Atualiza uma ONG"""
    return jsonify({"mensagem": f"Atualizar ONG {id}"}), 200

@bp.route('/<int:id>', methods=['DELETE'])
def deletar_ong(id):
    """Deleta uma ONG"""
    return jsonify({"mensagem": f"Deletar ONG {id}"}), 204
