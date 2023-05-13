
from flask import (request, jsonify, make_response)


from http import HTTPStatus
from functools import wraps
import pydash as py_
import src.functions as funcs
from flask_restx.utils import unpack


def make_cross_resp(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        return make_cross_domain_response(resp)

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


def make_cross_domain_response(data, response_code=200, extra_data=[]):
    etag = funcs.sha1(data)
    # print(etag)
    # print(request.if_none_match)
    if request.if_none_match and etag in request.if_none_match:
        response = make_response(jsonify({}), 304)
    else:
        response = make_response(jsonify(data), response_code)
        response.set_etag(etag)
    # set headers for response CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'AUTHORIZATION, If-none-match'
    response.headers['Access-Control-Max-Age'] = '1728000'
    response.headers['Access-Control-Expose-Headers'] = 'ETag, X-TOKEN'

    if extra_data:
        for d in extra_data:
            if 'name' in d and 'value' in d:
                response.headers[d['name']] = d['value']
    return response


def require_payload_field(fields):
    return require_field('payload', fields)


def enable_cors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        data, code, headers = unpack(func(*args, **kwargs))

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = '*'
        headers['Access-Control-Allow-Headers'] = '*'
        headers['Access-Control-Max-Age'] = '1728000'
        headers['Access-Control-Expose-Headers'] = 'ETag, X-TOKEN'

        return data, code, headers

    return wrapper
