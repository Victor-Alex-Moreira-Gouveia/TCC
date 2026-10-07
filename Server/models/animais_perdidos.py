from sqlalchemy import String, Text, Date, DateTime, LargeBinary, func, select
from sqlalchemy.orm import Mapped, mapped_column

from config.config import get_db
from models.base import Base


class AnimalPerdido(Base):
    __tablename__ = "animais_perdidos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    especie: Mapped[str] = mapped_column(String(40), nullable=False)
    sexo: Mapped[str] = mapped_column(String(30), nullable=False, default="Não informado")
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    local: Mapped[str] = mapped_column(String(255), nullable=False)
    data_ocorrido: Mapped[Date] = mapped_column(Date, nullable=False)
    contato: Mapped[str] = mapped_column(String(180), nullable=False)

    # A foto fica armazenada no próprio banco, como já acontece com as
    # imagens das notícias do projeto.
    imagem_blob: Mapped[bytes | None] = mapped_column(
        LargeBinary(length=4294967295),
        nullable=True
    )
    imagem_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Perdido"
    )
    autor: Mapped[str] = mapped_column(
        String(150), nullable=False, default="Visitante"
    )
    criado_em: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


def _to_dict(row):
    return {
        "id": row.id,
        "nome": row.nome,
        "especie": row.especie,
        "sexo": row.sexo,
        "descricao": row.descricao,
        "local": row.local,
        "data_ocorrido": row.data_ocorrido.isoformat() if row.data_ocorrido else "",
        "contato": row.contato,
        "tem_imagem": bool(row.imagem_blob),
        "status": row.status,
        "autor": row.autor,
        "criado_em": row.criado_em.isoformat() if row.criado_em else "",
    }


def listar_animais(limit=None):
    db = next(get_db())
    try:
        stmt = select(AnimalPerdido).order_by(AnimalPerdido.criado_em.desc())
        if limit:
            stmt = stmt.limit(limit)
        rows = db.scalars(stmt).all()
        return [_to_dict(row) for row in rows]
    finally:
        db.close()


def buscar_animal(animal_id):
    db = next(get_db())
    try:
        row = db.get(AnimalPerdido, animal_id)
        return _to_dict(row) if row else None
    finally:
        db.close()


def obter_imagem_animal(animal_id):
    db = next(get_db())
    try:
        row = db.get(AnimalPerdido, animal_id)
        if not row or not row.imagem_blob:
            return None
        return row.imagem_blob, (row.imagem_mime or "image/jpeg")
    finally:
        db.close()


def cadastrar_animal(dados, imagem_blob=None, imagem_mime=None):
    db = next(get_db())
    try:
        row = AnimalPerdido(
            **dados,
            imagem_blob=imagem_blob,
            imagem_mime=imagem_mime
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def atualizar_animal(animal_id, dados, imagem_blob=None, imagem_mime=None,
                     alterar_imagem=False, remover_imagem=False):
    db = next(get_db())
    try:
        row = db.get(AnimalPerdido, animal_id)
        if not row:
            return None

        for key, value in dados.items():
            setattr(row, key, value)

        if remover_imagem:
            row.imagem_blob = None
            row.imagem_mime = None
        elif alterar_imagem:
            row.imagem_blob = imagem_blob
            row.imagem_mime = imagem_mime

        db.commit()
        db.refresh(row)
        return _to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def excluir_animal(animal_id):
    db = next(get_db())
    try:
        row = db.get(AnimalPerdido, animal_id)
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True
    finally:
        db.close()
