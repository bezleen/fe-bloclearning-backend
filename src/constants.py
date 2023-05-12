import os
import src.enums as Enums
from dotenv import load_dotenv

load_dotenv()

# FORMAT
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
HASH_SALT = os.getenv("HASH_SALT")
ACCESS_TOKEN_TTL = 3600
REFRESH_TOKEN_TTL = 86400 * 2
UPLOAD_FOLDER = os.path.join(os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))), 'src/static')
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
PREFIX_KEY = "orasci"

KEY_USER_TOKEN = f"{PREFIX_KEY}:user:session:"

DEFAULT_ROLE_OBJ = {
    Enums.UserRole.DAO_MEMBER.value: 1,
    Enums.UserRole.RESEARCHER.value: 0,
    Enums.UserRole.REVIEWER.value: 0,
    Enums.UserRole.THIRD_PARTY.value: 0,
}

FORM_TO_ROLE = {
    Enums.FormType.OFFER_RESEARCHER.value: Enums.UserRole.RESEARCHER.value,
    Enums.FormType.OFFER_REVIEWER.value: Enums.UserRole.REVIEWER.value,
    Enums.FormType.OFFER_THIRD_PARTY.value: Enums.UserRole.THIRD_PARTY.value
}
