from flask_restx import Namespace, fields

from .api import BaseMeta


class Meta(BaseMeta):
    api = Namespace('Form', description='')

    response = api.model('Response', {
        'msg': fields.String(default="unknown"),
        'code': fields.Integer(default=0),
        'data': fields.Raw()
    })

    in_offer_form = api.model('InputBecomeResearcher', {
        'candidate_type': fields.String(description='candidate_type', required=True),
        'field': fields.String(description='field', default=""),
        'name': fields.String(description='name', required=True),
        'occupation': fields.String(description='occupation', required=True),
        'work_at': fields.String(description='work_at', required=True),
        'location': fields.String(description='location', required=True),
        'contact': fields.String(description='contact', default=""),
        'email': fields.String(description='email', required=True)
    })
