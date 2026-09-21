import re
import math
from flask import jsonify


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validate_email(email: str):
    return EMAIL_RE.match((email or '').strip()) is not None



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
