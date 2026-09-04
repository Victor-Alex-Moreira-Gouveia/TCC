from datetime import datetime

from sqlalchemy import DateTime, String, Text, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from config.config import get_db
from models.base import Base


class Noticia(Base):
    __tablename__ = 'noticias'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
    )


def count_noticias():
    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Noticia))
    return total


def list_noticias(limit, offset):
    db = next(get_db())
    stmt = select(Noticia).order_by(Noticia.id.asc()).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [
        {
            'id': r.id,
            'titulo': r.titulo,
            'corpo': r.corpo,
            'data_hora': r.data_hora.isoformat() if r.data_hora else None,
        }
        for r in rows
    ]


def get_noticia_by_id(nid):
    db = next(get_db())
    row = db.get(Noticia, nid)
    if row:
        return {
            'id': row.id,
            'titulo': row.titulo,
            'corpo': row.corpo,
            'data_hora': row.data_hora.isoformat() if row.data_hora else None,
        }
    return None


def create_noticia(titulo, corpo):
    db = next(get_db())
    try:
        nova = Noticia(titulo=titulo, corpo=corpo)
        db.add(nova)
        db.commit()
        return nova.id
    except IntegrityError:
        db.rollback()
        raise


def update_noticia_db(nid, update_data):
    db = next(get_db())
    try:
        noticia = db.get(Noticia, nid)
        if not noticia:
            return None
        for key, value in update_data.items():
            setattr(noticia, key, value)
        db.commit()
        return {
            'id': noticia.id,
            'titulo': noticia.titulo,
            'corpo': noticia.corpo,
            'data_hora': noticia.data_hora.isoformat() if noticia.data_hora else None,
        }
    except IntegrityError:
        db.rollback()
        raise


def delete_noticia_db(nid):
    db = next(get_db())
    noticia = db.get(Noticia, nid)
    if not noticia:
        return False
    db.delete(noticia)
    db.commit()
    return True
