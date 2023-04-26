
import json
from functools import wraps
from threading import Thread


from src.extensions import redis_cached


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
