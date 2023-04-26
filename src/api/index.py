from http import HTTPStatus
from flask import Blueprint, request

import pydash as py_
import src.constants as Consts
import src.config as Conf
import src.middlewares.http as Http
import src.models.repo as Repo


bp = Blueprint('index', __name__, url_prefix='/common')


@bp.route('debug')
@Http.make_cross_resp
def debug():
    1 / 0
    return ''


@bp.route('health_check')
@Http.make_cross_resp
def health_check():

    rq_hdrs = request.headers
    geo_ip = py_.get(rq_hdrs, 'x-geoip-country-code')

    data = {
        "geo_ip": geo_ip,
    }

    return {
        "code": HTTPStatus.OK,
        "msg": "success",
        "data": data
    }
