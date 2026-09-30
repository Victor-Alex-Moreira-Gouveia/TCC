from datetime import datetime
from sqlalchemy import DateTime, LargeBinary, String, Text, ForeignKey, UniqueConstraint, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from config.config import get_db
from config.cache import cache
from models.base import Base


class Noticia(Base):
    __tablename__ = 'noticias'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    imagem_blob: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    imagem_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
    )


class ComentarioNoticia(Base):
    __tablename__ = 'comentarios_noticias'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    noticia_id: Mapped[int] = mapped_column(ForeignKey('noticias.id', ondelete='CASCADE'), nullable=False)
    usuario_id: Mapped[str] = mapped_column(String(80), nullable=False)
    autor_nome: Mapped[str] = mapped_column(String(150), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
    )
    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
    )


class CurtidaNoticia(Base):
    __tablename__ = 'curtidas_noticias'
    __table_args__ = (UniqueConstraint('noticia_id', 'usuario_id', name='uq_noticia_usuario'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    noticia_id: Mapped[int] = mapped_column(ForeignKey('noticias.id', ondelete='CASCADE'), nullable=False)
    usuario_id: Mapped[str] = mapped_column(String(80), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
    )


def _invalidate_noticias_cache():
    """Invalida com segurança o cache de notícias (com fallback gracioso em exceção)."""
    cache.flush()


# ---------------------------------------------------------------------------
# Notícias
# ---------------------------------------------------------------------------

def count_noticias():
    cached = cache.get('noticias_count')
    if cached is not None:
        return cached

    db = next(get_db())
    total = db.scalar(select(func.count()).select_from(Noticia)) or 0
    cache.set('noticias_count', total, expire=120)
    return total


def _get_counts_and_user_like(db, noticia_id: int, current_user_id: str = None):
    curtidas_count = db.scalar(
        select(func.count()).select_from(CurtidaNoticia).where(CurtidaNoticia.noticia_id == noticia_id)
    ) or 0
    comentarios_count = db.scalar(
        select(func.count()).select_from(ComentarioNoticia).where(ComentarioNoticia.noticia_id == noticia_id)
    ) or 0

    curtido_pelo_usuario = False
    if current_user_id:
        user_like = db.scalar(
            select(CurtidaNoticia).where(
                CurtidaNoticia.noticia_id == noticia_id,
                CurtidaNoticia.usuario_id == str(current_user_id)
            )
        )
        curtido_pelo_usuario = user_like is not None

    return curtidas_count, comentarios_count, curtido_pelo_usuario


def list_noticias(limit, offset, current_user_id=None):
    cache_key = f'noticias_list_{limit}_{offset}_{current_user_id or "anon"}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    db = next(get_db())
    stmt = select(Noticia).order_by(Noticia.id.desc()).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()

    result = []
    for r in rows:
        curtidas, comentarios, curtido = _get_counts_and_user_like(db, r.id, current_user_id)
        result.append({
            'id': r.id,
            'titulo': r.titulo,
            'corpo': r.corpo,
            'imagem_url': f'/api/noticias/{r.id}/imagem' if r.imagem_blob else None,
            'data_hora': r.data_hora.isoformat() if r.data_hora else None,
            'curtidas_count': curtidas,
            'comentarios_count': comentarios,
            'curtido_pelo_usuario': curtido,
        })

    cache.set(cache_key, result, expire=120)
    return result


def get_noticia_by_id(nid, current_user_id=None):
    cache_key = f'noticia_detail_{nid}_{current_user_id or "anon"}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    db = next(get_db())
    row = db.get(Noticia, nid)
    if row:
        curtidas, comentarios, curtido = _get_counts_and_user_like(db, row.id, current_user_id)
        res = {
            'id': row.id,
            'titulo': row.titulo,
            'corpo': row.corpo,
            'imagem_url': f'/api/noticias/{row.id}/imagem' if row.imagem_blob else None,
            'data_hora': row.data_hora.isoformat() if row.data_hora else None,
            'curtidas_count': curtidas,
            'comentarios_count': comentarios,
            'curtido_pelo_usuario': curtido,
        }
        cache.set(cache_key, res, expire=120)
        return res
    return None


def get_noticia_raw_image(nid):
    db = next(get_db())
    row = db.get(Noticia, nid)
    if row and row.imagem_blob:
        return row.imagem_blob, row.imagem_mime or 'image/jpeg'
    return None, None


def create_noticia(titulo, corpo, imagem_blob=None, imagem_mime=None):
    db = next(get_db())
    try:
        nova = Noticia(titulo=titulo, corpo=corpo, imagem_blob=imagem_blob, imagem_mime=imagem_mime)
        db.add(nova)
        db.commit()
        _invalidate_noticias_cache()
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
        _invalidate_noticias_cache()
        return {
            'id': noticia.id,
            'titulo': noticia.titulo,
            'corpo': noticia.corpo,
            'imagem_url': f'/api/noticias/{noticia.id}/imagem' if noticia.imagem_blob else None,
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
    _invalidate_noticias_cache()
    return True


# ---------------------------------------------------------------------------
# Comentários
# ---------------------------------------------------------------------------

def list_comentarios(noticia_id: int):
    db = next(get_db())
    stmt = select(ComentarioNoticia).where(
        ComentarioNoticia.noticia_id == noticia_id
    ).order_by(ComentarioNoticia.data_criacao.asc())
    rows = db.scalars(stmt).all()
    return [
        {
            'id': c.id,
            'noticia_id': c.noticia_id,
            'usuario_id': c.usuario_id,
            'autor_nome': c.autor_nome,
            'texto': c.texto,
            'data_criacao': c.data_criacao.isoformat() if c.data_criacao else None,
            'data_atualizacao': c.data_atualizacao.isoformat() if c.data_atualizacao else None,
        }
        for c in rows
    ]


def get_comentario_by_id(comentario_id: int):
    db = next(get_db())
    c = db.get(ComentarioNoticia, comentario_id)
    if c:
        return {
            'id': c.id,
            'noticia_id': c.noticia_id,
            'usuario_id': c.usuario_id,
            'autor_nome': c.autor_nome,
            'texto': c.texto,
            'data_criacao': c.data_criacao.isoformat() if c.data_criacao else None,
            'data_atualizacao': c.data_atualizacao.isoformat() if c.data_atualizacao else None,
        }
    return None


def create_comentario(noticia_id: int, usuario_id: str, autor_nome: str, texto: str):
    db = next(get_db())
    novo = ComentarioNoticia(
        noticia_id=noticia_id,
        usuario_id=str(usuario_id),
        autor_nome=autor_nome,
        texto=texto,
    )
    db.add(novo)
    db.commit()
    _invalidate_noticias_cache()
    return get_comentario_by_id(novo.id)


def update_comentario_db(comentario_id: int, texto: str):
    db = next(get_db())
    c = db.get(ComentarioNoticia, comentario_id)
    if not c:
        return None
    c.texto = texto
    c.data_atualizacao = datetime.utcnow()
    db.commit()
    _invalidate_noticias_cache()
    return get_comentario_by_id(c.id)


def delete_comentario_db(comentario_id: int):
    db = next(get_db())
    c = db.get(ComentarioNoticia, comentario_id)
    if not c:
        return False
    db.delete(c)
    db.commit()
    _invalidate_noticias_cache()
    return True


# ---------------------------------------------------------------------------
# Curtidas
# ---------------------------------------------------------------------------

def adicionar_curtida(noticia_id: int, usuario_id: str):
    db = next(get_db())
    user_str = str(usuario_id)
    existing = db.scalar(
        select(CurtidaNoticia).where(
            CurtidaNoticia.noticia_id == noticia_id,
            CurtidaNoticia.usuario_id == user_str
        )
    )
    if existing:
        return True
    try:
        curtida = CurtidaNoticia(noticia_id=noticia_id, usuario_id=user_str)
        db.add(curtida)
        db.commit()
        _invalidate_noticias_cache()
        return True
    except IntegrityError:
        db.rollback()
        return True


def remover_curtida(noticia_id: int, usuario_id: str):
    db = next(get_db())
    user_str = str(usuario_id)
    existing = db.scalar(
        select(CurtidaNoticia).where(
            CurtidaNoticia.noticia_id == noticia_id,
            CurtidaNoticia.usuario_id == user_str
        )
    )
    if not existing:
        return False
    db.delete(existing)
    db.commit()
    _invalidate_noticias_cache()
    return True
