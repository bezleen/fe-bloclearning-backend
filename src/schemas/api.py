import os
from sys import prefix
from flask import Blueprint
from flask_restx import Api, Model

from dotenv import load_dotenv
load_dotenv()


class BaseMeta:
    AUTHEN_BY_TOKEN = 'authorization'
    # AUTHEN_BY_CODE = 'apikey'

    AUTHORIZATIONS = {
        AUTHEN_BY_TOKEN: {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-Authorization'
        },
        # AUTHEN_BY_CODE: {
        #     'type': 'apiKey',
        #     'in': 'header',
        #     'name': 'sc'
        # }
    }

    RESPONSE_CODE = {
        200: 'Success',
        201: 'Created',
        400: 'Bad request',
        500: 'Server error'
    }


class ApiMeta(BaseMeta):
    blueprint = Blueprint('api v1', __name__, url_prefix='/v1/api')
    doc_path = False
    if int(os.getenv("DEVELOP", 0)):
        doc_path = "/docs/65jRoTK4j4w6ihkW"

    api = Api(
        blueprint,
        title='API SERVICES',
        version='1.0',
        description='api docs',
        security=[BaseMeta.AUTHEN_BY_TOKEN],
        authorizations=BaseMeta.AUTHORIZATIONS,
        doc=doc_path
    )
