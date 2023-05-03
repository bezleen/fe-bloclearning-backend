import os

from dotenv import load_dotenv

load_dotenv()

# FORMAT
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
HASH_SALT = os.getenv("HASH_SALT")
ACCESS_TOKEN_TTL = 3600
REFRESH_TOKEN_TTL = 86400 * 2
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'src/static')
