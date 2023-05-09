from src.schemas.api import ApiMeta

from .index import bp as rest_index
from .auth import api as AuthApi
from .projects import api as ProjectsApi
from .user import api as UserApi
from .form import api as FormApi

v1_bp = ApiMeta.blueprint
api = ApiMeta.api


# routing api for app
api.add_namespace(AuthApi, path='/auth')
api.add_namespace(ProjectsApi, path='/projects')
api.add_namespace(UserApi, path='/user')
api.add_namespace(FormApi, path='/form')


DEFAULT_BLUEPRINTS = [
    v1_bp,
    rest_index
]
