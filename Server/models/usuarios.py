from sqlalchemy import String, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from config.config import get_db
from models.base import Base


class Usuario(Base):
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome_usuario: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)


def count_users():
    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Usuario))
    return total


def list_users(limit, offset):
    db = next(get_db())
    stmt = select(Usuario).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [{'id': r.id, 'nome_usuario': r.nome_usuario, 'email': r.email} for r in rows]


def get_usuario_by_id(uid):
    db = next(get_db())
    row = db.get(Usuario, uid)
    if row:
        return {'id': row.id, 'nome_usuario': row.nome_usuario, 'email': row.email}
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
        return {'id': usuario.id, 'nome_usuario': usuario.nome_usuario, 'email': usuario.email}
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