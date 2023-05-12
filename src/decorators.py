
import json
from functools import wraps
from threading import Thread
import pydash as py_
from flask import request, current_app, abort


from src.resp_code import ResponseMsg
import src.controllers as Controllers
from src.extensions import redis_cached
import src.enums as Enums


def async_function(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


def cache_filter(timeout=86400, key_prefix='common', key_fields=[]):
    """
    Decorator for caching functions by filter
    Returns the cached value, or the function if the cache is disabled
    """
    if timeout is None:
        timeout = 86400

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # print(args, kwargs)
            # user_id, limit, offset {}
            key = f'{key_prefix}'
            for key_field in key_fields:
                key_field_data = kwargs.get(key_field)
                if key_field_data:
                    key += f':{key_field_data}'
            output = redis_cached.get(key)
            if output:
                print('HIT', key)
                return json.loads(output)
            output = f(*args, **kwargs)
            # print('MISS', key, output)
            # Set data to redis
            redis_cached.setex(
                key, timeout,
                json.dumps(output)
            )

            return output

        return wrapper

    return decorator


def req_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        access_token = py_.get(request.headers, 'X-Authorization')
        if not access_token:
            return ResponseMsg.UNAUTHORIZED.to_json(), 401

        token_info = Controllers.Auth.decode_jwt(access_token)
        user_id = py_.get(token_info, "_id")
        user_role = py_.get(token_info, "role")

        if not user_id:
            return ResponseMsg.UNAUTHORIZED.to_json(), 401

        # check conflict
        is_conflict = Controllers.User.check_conflict_token(
            user_id, access_token)
        if is_conflict:
            return ResponseMsg.LOGIN_CONFLICT.to_json(), 409

        # prevent admin
        role_decoded = Controllers.Auth.decode_user_role(
            user_role, output_type="list")
        if Enums.UserRole.ADMIN.value in role_decoded:
            return ResponseMsg.UNAUTHORIZED.to_json(), 401

        return f(user_id=user_id, *args, **kwargs)
    return wrapper


def req_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        access_token = py_.get(request.headers, 'X-Authorization')
        if not access_token:
            return ResponseMsg.UNAUTHORIZED.to_json(), 401

        token_info = Controllers.Auth.decode_jwt(access_token)
        user_role = py_.get(token_info, "role")

        if user_role != Enums.UserRole.ADMIN.value:
            return ResponseMsg.UNAUTHORIZED.to_json(), 401

        return f(*args, **kwargs)
    return wrapper
