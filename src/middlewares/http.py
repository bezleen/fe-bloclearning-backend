import os
import json
from flask import (request, jsonify, make_response)

from http import HTTPStatus
from functools import wraps
import pydash as py_
import src.functions as funcs


def make_cross_resp(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        return funcs.make_cross_domain_response(resp)

    return wrapper


def require_field(req_type, fields):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if req_type == 'payload':
                req = request.get_json()

            if not req \
                or any(field for field in fields
                       if field not in req or not py_.get(req, field)):
                return {
                    "code": HTTPStatus.BAD_REQUEST,
                    "msg": f"Check your request - require fields: {','.join(fields)}!"
                }
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_payload_field(fields):
    return require_field('payload', fields)
