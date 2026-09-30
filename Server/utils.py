import re
import math
import mimetypes
from flask import jsonify


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

ALLOWED_IMAGE_MIMES = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif',
    'image/svg+xml', 'image/bmp', 'image/tiff', 'image/x-icon', 'image/avif',
    'image/heic', 'image/heif'
}


def validate_email(email: str):
    return EMAIL_RE.match((email or '').strip()) is not None


def detect_image_mime(filename: str, mimetype: str, blob: bytes) -> tuple[bool, str]:
    """
    Valida e detecta dinamicamente o MIME type para múltiplos formatos de imagem (PNG, JPG, JPEG, WEBP, GIF, SVG, BMP, AVIF, TIFF).
    Retorna (is_valid: bool, mime_type: str).
    """
    if not blob:
        return False, ''

    filename_lower = (filename or '').lower()
    mime = (mimetype or '').lower().strip()
    if mime == 'image/jpg':
        mime = 'image/jpeg'

    # Se o browser enviou octet-stream ou nada, tenta adivinhar pela extensão
    if not mime or mime == 'application/octet-stream':
        guessed, _ = mimetypes.guess_type(filename_lower)
        if guessed:
            mime = guessed.lower()

    # Inspeção de Magic Bytes para verificação precisa de integridade
    header = blob[:32]
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = 'image/png'
    elif header.startswith(b'\xff\xd8\xff'):
        mime = 'image/jpeg'
    elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        mime = 'image/gif'
    elif header.startswith(b'RIFF') and b'WEBP' in header[8:16]:
        mime = 'image/webp'
    elif header.startswith(b'BM'):
        mime = 'image/bmp'
    elif header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):
        mime = 'image/tiff'
    elif b'<svg' in header.lower() or filename_lower.endswith('.svg'):
        mime = 'image/svg+xml'
    elif b'ftypavif' in header or b'ftypheic' in header:
        mime = 'image/avif'

    is_valid = (mime in ALLOWED_IMAGE_MIMES) or mime.startswith('image/')
    return is_valid, mime or 'image/jpeg'


def parse_pagination(args):
    try:
        page = max(1, int(args.get('page', 1)))
        limit = max(1, min(100, int(args.get('limit', 10))))
    except (ValueError, TypeError):
        page, limit = 1, 10
    offset = (page - 1) * limit
    return page, limit, offset


def build_pagination(total, page, limit):
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if limit else 1
    }


def success_response(data, message="Operação realizada com sucesso", status=200, pagination=None):
    body = {"success": True, "data": data, "message": message}
    if pagination:
        body["pagination"] = pagination
    return jsonify(body), status


def error_response(message, code="ERROR", details=None, status=400):
    body = {"success": False, "error": message, "code": code}
    if details is not None:
        body["details"] = details
    return jsonify(body), status
