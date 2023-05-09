import re
import hashlib
import src.constants as Consts


import hashlib
import json
import random
import string

import datetime as dt
import pytz
from datetime import datetime, date


def ora_hash(string: str) -> str:
    print(string)
    return hashlib.pbkdf2_hmac("sha256", str(string).encode('utf-8'), Consts.HASH_SALT.encode('utf-8'), 100000).hex()


def safe_string(string: str) -> str:
    string = string.strip()
    string = string.lower()
    return string


def safe_name(string: str) -> str:
    string = string.strip()
    string = string[:20]
    return string


def is_valid_phone_number(phone_number):
    pattern = re.compile(r'^\+?\d{0,2}[- ]?\d{3}[- ]?\d{3}[- ]?\d{4}$')
    # The pattern matches phone numbers in the following formats:
    # +1-555-555-5555, +44 1234567890, 555-555-5555, 5555555555, etc.

    return bool(re.match(pattern, phone_number))


def json_decode_hook(obj):
    if '__datetime__' in obj:
        return datetime.strptime(obj['as_str'], "%Y%m%dT%H:%M:%S.%f")
    if b'__datetime__' in obj:
        return datetime.strptime(obj[b'as_str'], "%Y%m%dT%H:%M:%S.%f")
    return obj


def json_encode_hook(obj):
    if isinstance(obj, datetime):
        obj = {
            '__datetime__': True,
            'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")
        }
    if isinstance(obj, date):
        dt = datetime.combine(obj.today(), datetime.min.time())
        obj = {
            '__datetime__': True,
            'as_str': dt.strftime("%Y%m%dT%H:%M:%S.%f")
        }
    return obj


def json_encode_response(obj):
    if isinstance(obj, datetime):
        return obj.timestamp()
    if isinstance(obj, date):
        return datetime.combine(obj.today(), datetime.min.time()).timestamp()
    return obj


def sha1(data):
    json_data = json.dumps(data, default=json_encode_hook)
    return hashlib.sha1(json_data.encode('utf-8')).hexdigest()


def md5(str2hash):
    result = hashlib.md5(str2hash.encode())
    return result.hexdigest()


def tzware_datetime():
    """
    Return a timezone aware datetime.

    :return: Datetime
    """
    return dt.datetime.now(pytz.utc)


def random_ascii_number(N=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def is_hex(string):
    return all(c in '0123456789abcdefABCDEF' for c in string) and len(string) % 2 == 0
