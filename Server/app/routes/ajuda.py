from flask import Blueprint, jsonify

bp = Blueprint('ajuda', __name__, url_prefix='/ajuda')

@bp.route('/', methods=['GET'])
def listar_ajudas():
    """Lista todas as ajudas"""
    return jsonify({"mensagem": "Listar ajudas"}), 200

@bp.route('/<int:id>', methods=['GET'])
def obter_ajuda(id):
    """Obtém uma ajuda específica"""
    return jsonify({"mensagem": f"Obter ajuda {id}"}), 200

@bp.route('/', methods=['POST'])
def criar_ajuda():
    """Cria uma nova ajuda"""
    return jsonify({"mensagem": "Criar ajuda"}), 201

@bp.route('/<int:id>', methods=['PUT'])
def atualizar_ajuda(id):
    """Atualiza uma ajuda"""
    return jsonify({"mensagem": f"Atualizar ajuda {id}"}), 200

@bp.route('/<int:id>', methods=['DELETE'])
def deletar_ajuda(id):
    """Deleta uma ajuda"""
    return jsonify({"mensagem": f"Deletar ajuda {id}"}), 204
