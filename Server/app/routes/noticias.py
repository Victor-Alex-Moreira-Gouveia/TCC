from flask import Blueprint, jsonify

bp = Blueprint('noticias', __name__, url_prefix='/noticias')

@bp.route('/', methods=['GET'])
def listar_noticias():
    """Lista todas as notícias"""
    return jsonify({"mensagem": "Listar notícias"}), 200

@bp.route('/<int:id>', methods=['GET'])
def obter_noticia(id):
    """Obtém uma notícia específica"""
    return jsonify({"mensagem": f"Obter notícia {id}"}), 200

@bp.route('/', methods=['POST'])
def criar_noticia():
    """Cria uma nova notícia"""
    return jsonify({"mensagem": "Criar notícia"}), 201

@bp.route('/<int:id>', methods=['PUT'])
def atualizar_noticia(id):
    """Atualiza uma notícia"""
    return jsonify({"mensagem": f"Atualizar notícia {id}"}), 200

@bp.route('/<int:id>', methods=['DELETE'])
def deletar_noticia(id):
    """Deleta uma notícia"""
    return jsonify({"mensagem": f"Deletar notícia {id}"}), 204
