import re
import hashlib
import src.constants as Consts


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
