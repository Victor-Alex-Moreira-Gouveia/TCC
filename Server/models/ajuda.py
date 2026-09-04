from sqlalchemy import String, Text, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from config.config import get_db
from models.base import Base


class Ajuda(Base):
    __tablename__ = 'ajuda'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    pix_doacao: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_denuncia: Mapped[str] = mapped_column(String(80), nullable=False, default='Animal doméstico')
    nivel_urgencia: Mapped[str] = mapped_column(String(80), nullable=False, default='Não informado')
    autor: Mapped[str] = mapped_column(String(150), nullable=False, default='anon')


def count_ajuda():
    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Ajuda))
    return total


def list_ajuda(limit, offset):
    db = next(get_db())
    stmt = select(Ajuda).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [
        {
            'id': r.id,
            'titulo': r.titulo,
            'corpo': r.corpo,
            'pix_doacao': r.pix_doacao,
            'tipo_denuncia': r.tipo_denuncia,
            'nivel_urgencia': r.nivel_urgencia,
            'autor': r.autor,
        }
        for r in rows
    ]


def get_ajuda_by_id(aid):
    db = next(get_db())
    row = db.get(Ajuda, aid)
    if row:
        return {
            'id': row.id,
            'titulo': row.titulo,
            'corpo': row.corpo,
            'pix_doacao': row.pix_doacao,
            'tipo_denuncia': row.tipo_denuncia,
            'nivel_urgencia': row.nivel_urgencia,
            'autor': row.autor,
        }
    return None


def create_ajuda_db(titulo, corpo, pix, autor, tipo_denuncia='Animal doméstico', nivel_urgencia='Não informado'):
    db = next(get_db())
    try:
        nova_ajuda = Ajuda(
            titulo=titulo,
            corpo=corpo,
            pix_doacao=pix,
            autor=autor,
            tipo_denuncia=tipo_denuncia,
            nivel_urgencia=nivel_urgencia,
        )
        db.add(nova_ajuda)
        db.commit()
        return nova_ajuda.id
    except IntegrityError:
        db.rollback()
        raise


def update_ajuda_db(aid, update_data):
    db = next(get_db())
    try:
        ajuda = db.get(Ajuda, aid)
        if not ajuda:
            return None

        for key, value in update_data.items():
            setattr(ajuda, key, value)

        db.commit()
        return {
            'id': ajuda.id,
            'titulo': ajuda.titulo,
            'corpo': ajuda.corpo,
            'pix_doacao': ajuda.pix_doacao,
            'tipo_denuncia': ajuda.tipo_denuncia,
            'nivel_urgencia': ajuda.nivel_urgencia,
            'autor': ajuda.autor,
        }
    except IntegrityError:
        db.rollback()
        raise


def delete_ajuda_db(aid):
    db = next(get_db())
    ajuda = db.get(Ajuda, aid)
    if not ajuda:
        return False

    db.delete(ajuda)
    db.commit()
    return True