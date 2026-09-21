from sqlalchemy import String, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from config.config import get_db
from models.base import Base


class Ong(Base):
    __tablename__ = 'ongs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome_instituicao: Mapped[str] = mapped_column(String(150), nullable=False)
    endereco_fisico: Mapped[str | None] = mapped_column(String(255), nullable=True)
    site: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pix_doacao: Mapped[str] = mapped_column(String(100), nullable=False)


def count_ongs():
    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Ong))
    return total


def list_ongs(limit, offset):
    db = next(get_db())
    stmt = select(Ong).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [
        {
            'id': r.id,
            'nome_instituicao': r.nome_instituicao,
            'endereco_fisico': r.endereco_fisico,
            'site': r.site,
            'pix_doacao': r.pix_doacao,
        }
        for r in rows
    ]


def get_ong_by_id(oid):
    db = next(get_db())
    row = db.get(Ong, oid)
    if row:
        return {
            'id': row.id,
            'nome_instituicao': row.nome_instituicao,
            'endereco_fisico': row.endereco_fisico,
            'site': row.site,
            'pix_doacao': row.pix_doacao,
        }
    return None


def create_ong(nome, endereco, site, pix):
    db = next(get_db())
    try:
        nova_ong = Ong(nome_instituicao=nome, endereco_fisico=endereco, site=site, pix_doacao=pix)
        db.add(nova_ong)
        db.commit()
        return nova_ong.id
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
        return {
            'id': ong.id,
            'nome_instituicao': ong.nome_instituicao,
            'endereco_fisico': ong.endereco_fisico,
            'site': ong.site,
            'pix_doacao': ong.pix_doacao,
        }
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