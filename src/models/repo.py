from src.extensions import mdb

from .base import BaseDAO

mUser = BaseDAO(mdb.db.user)
mProjects = BaseDAO(mdb.db.projects)
mForms = BaseDAO(mdb.db.forms)
