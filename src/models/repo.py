from src.extensions import mdb

from .base import BaseDAO

mUser = BaseDAO(mdb.db.user)
