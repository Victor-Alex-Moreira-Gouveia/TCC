from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from config.engine import get_db
# Importe o modelo Ajuda de onde ele foi definido
from models.ajuda import Ajuda 

def count_ajuda():
    # Pegamos a sessão do generator criado no engine.py
    db = next(get_db()) 
    total = db.scalar(select(func.count()).select_from(Ajuda))
    return total

def list_ajuda(limit, offset):
    db = next(get_db())
    stmt = select(Ajuda).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    # Retorna como dicionário para manter a compatibilidade com o controlador antigo[cite: 4]
    return [{"id": r.id, "titulo": r.titulo, "corpo": r.corpo, "pix_doacao": r.pix_doacao, "autor": r.autor} for r in rows]

def get_ajuda_by_id(aid):
    db = next(get_db())
    r = db.get(Ajuda, aid)
    if r:
        return {"id": r.id, "titulo": r.titulo, "corpo": r.corpo, "pix_doacao": r.pix_doacao, "autor": r.autor}
    return None

def create_ajuda_db(titulo, corpo, pix, autor):
    db = next(get_db())
    try:
        nova_ajuda = Ajuda(titulo=titulo, corpo=corpo, pix_doacao=pix, autor=autor)
        db.add(nova_ajuda)
        db.commit()
        return nova_ajuda.id # Retorna o ID recém-criado[cite: 4]
    except IntegrityError:
        db.rollback()
        raise

def update_ajuda_db(aid, update_data):
    # update_data deve ser um dicionário ex: {"titulo": "Novo", "corpo": "..."}[cite: 4]
    db = next(get_db())
    try:
        ajuda = db.get(Ajuda, aid)
        if not ajuda:
            return None
        
        for key, value in update_data.items():
            setattr(ajuda, key, value)
            
        db.commit()
        return {"id": ajuda.id, "titulo": ajuda.titulo, "corpo": ajuda.corpo, "pix_doacao": ajuda.pix_doacao, "autor": ajuda.autor}
    except IntegrityError:
        db.rollback()
        raise

def delete_ajuda_db(aid):
    db = next(get_db())
    ajuda = db.get(Ajuda, aid)
    if not ajuda:
        return False # Retorna False se não encontrar[cite: 4]
    
    db.delete(ajuda)
    db.commit()
    return True