from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from config.engine import get_db
from models.ongs import Ong 

def count_ongs():
    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Ong))
    return total

def list_ongs(limit, offset):
    db = next(get_db())
    stmt = select(Ong).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [{"id": r.id, "nome_instituicao": r.nome_instituicao, "endereco_fisico": r.endereco_fisico, "site": r.site, "pix_doacao": r.pix_doacao} for r in rows]

def get_ong_by_id(oid):
    db = next(get_db())
    r = db.get(Ong, oid)
    if r:
        return {"id": r.id, "nome_instituicao": r.nome_instituicao, "endereco_fisico": r.endereco_fisico, "site": r.site, "pix_doacao": r.pix_doacao}
    return None

def create_ong(nome, endereco, site, pix):
    db = next(get_db())
    try:
        nova_ong = Ong(nome_instituicao=nome, endereco_fisico=endereco, site=site, pix_doacao=pix)
        db.add(nova_ong)
        db.commit()
        return nova_ong.id # Retorna o ID gerado[cite: 5]
    except IntegrityError:
        db.rollback()
        raise

def update_ong_db(oid, update_data):
    db = next(get_db())
    try:
        ong = db.get(Ong, oid)
        if not ong:
            return None
        
        for key, value in update_data.items():
            setattr(ong, key, value)
            
        db.commit()
        return {"id": ong.id, "nome_instituicao": ong.nome_instituicao, "endereco_fisico": ong.endereco_fisico, "site": ong.site, "pix_doacao": ong.pix_doacao}
    except IntegrityError:
        db.rollback()
        raise

def delete_ong_db(oid):
    db = next(get_db())
    ong = db.get(Ong, oid)
    if not ong:
        return False
    
    db.delete(ong)
    db.commit()
    return True