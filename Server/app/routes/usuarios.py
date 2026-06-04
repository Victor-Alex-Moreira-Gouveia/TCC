from flask import Blueprint, jsonify

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/', methods=['GET'])
def listar_usuarios():
    """Lista todos os usuários"""
    return jsonify({"mensagem": "Listar usuários"}), 200

@bp.route('/<int:id>', methods=['GET'])
def obter_usuario(id):
    """Obtém um usuário específico"""
    return jsonify({"mensagem": f"Obter usuário {id}"}), 200

@bp.route('/', methods=['POST'])
def criar_usuario():
    """Cria um novo usuário"""
    return jsonify({"mensagem": "Criar usuário"}), 201

@bp.route('/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    """Atualiza um usuário"""
    return jsonify({"mensagem": f"Atualizar usuário {id}"}), 200

@bp.route('/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    """Deleta um usuário"""
    return jsonify({"mensagem": f"Deletar usuário {id}"}), 204
