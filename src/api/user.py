from flask import request, current_app

from flask_restx import Resource, marshal
import pydash as py_

import src.constants as Consts
from src.schemas import UserMeta
import src.decorators as Decorators
import src.controllers as Controllers
from src.extensions import redis_cached
from src.resp_code import ResponseMsg
import src.functions as funcs
from src.config import DefaultConfig as Conf
import src.enums as Enums
from src.utils.util_datetime import tzware_timestamp
from src.middlewares.http import enable_cors

api = UserMeta.api


@api.route('/profile')
@api.doc(responses=UserMeta.RESPONSE_CODE)
class Profile(Resource):

    @api.marshal_with(UserMeta.resp_profile)
    @Decorators.req_login
    @enable_cors
    def get(self, user_id):
        """
            User Profile
        """
        resp = Controllers.User.get_profile(user_id)
        return ResponseMsg.SUCCESS.to_json(data=resp), 200

    @api.expect(UserMeta.in_update_profile)
    @Decorators.req_login
    @enable_cors
    def post(self, user_id):
        """
            Update User Profile
        """
        data = marshal(request.get_json(), UserMeta.in_update_profile)
        new_name = py_.get(data, "name")
        new_occupation = py_.get(data, "occupation")
        new_work_at = py_.get(data, "work_at")
        new_location = py_.get(data, "location")
        new_contact = py_.get(data, "contact")
        Controllers.User.update_profile(user_id, name=new_name, occupation=new_occupation,
                                        work_at=new_work_at, location=new_location, contact=new_contact)
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/avatar')
@api.doc(responses=UserMeta.RESPONSE_CODE)
class Avatar(Resource):

    @Decorators.req_login
    @enable_cors
    def post(self, user_id):
        """
            Upload Avatar
        """
        try:
            if 'file' not in request.files:
                return ResponseMsg.INVALID.to_json(), 400
            file = request.files['file']
            Controllers.User.upload_avatar(user_id, file)
        except Exception as e:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data={}), 200
