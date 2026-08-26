from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from config.engine import get_db
from models.usuarios import Usuario

def count_users():
    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Usuario))
    return total

def list_users(limit, offset):
    db = next(get_db())
    stmt = select(Usuario).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    # Retorna apenas id, nome_usuario e email, conforme o arquivo original[cite: 6]
    return [{"id": r.id, "nome_usuario": r.nome_usuario, "email": r.email} for r in rows]

def get_usuario_by_id(uid):
    db = next(get_db())
    r = db.get(Usuario, uid)
    if r:
        return {"id": r.id, "nome_usuario": r.nome_usuario, "email": r.email}
    return None

def create_usuario(nome, email, senha_hash):
    db = next(get_db())
    try:
        novo_usuario = Usuario(nome_usuario=nome, email=email, senha=senha_hash)
        db.add(novo_usuario)
        db.commit()
        return novo_usuario.id
    except IntegrityError:
        db.rollback()
        raise

def update_usuario_db(uid, update_data):
    db = next(get_db())
    try:
        usuario = db.get(Usuario, uid)
        if not usuario:
            return None
        
        for key, value in update_data.items():
            setattr(usuario, key, value)
            
        db.commit()
        return {"id": usuario.id, "nome_usuario": usuario.nome_usuario, "email": usuario.email}
    except IntegrityError:
        db.rollback()
        raise

def delete_usuario_db(uid):
    db = next(get_db())
    usuario = db.get(Usuario, uid)
    if not usuario:
        return False
    
    db.delete(usuario)
    db.commit()
    return True