import hashlib
import src.constants as Consts


def ora_hash(string: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", str(string).encode('utf-8'), Consts.HASH_SALT.encode('utf-8'), 100000).hex()


def safe_string(string: str) -> str:
    string = string.strip()
    string = string.lower()
    return string
