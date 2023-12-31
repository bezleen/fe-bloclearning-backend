from flask import request, current_app

from flask_restx import Resource, marshal
import pydash as py_

import src.constants as Consts
from src.schemas import FormMeta
import src.decorators as Decorators
import src.controllers as Controllers
from src.extensions import redis_cached
from src.resp_code import ResponseMsg
import src.functions as funcs
from src.config import DefaultConfig as Conf
import src.enums as Enums
from src.utils.util_datetime import tzware_timestamp
from src.middlewares.http import enable_cors

api = FormMeta.api


@api.route('/offer/<form_type>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class Offer(Resource):

    @api.expect(FormMeta.in_offer_form)
    @Decorators.req_login
    @enable_cors
    def post(self, form_type, user_id):
        """
            Submit a form to become Third Party
        """
        data = marshal(request.get_json(), FormMeta.in_offer_form)
        form_obj = Controllers.Form.submit_form(user_id, form_type, data)
        if not form_obj:
            return ResponseMsg.INVALID.to_json(data={}), 400
        return ResponseMsg.SUCCESS.to_json(data=form_obj), 200


@api.route('/upload-id-card/<side>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class UploadIdCard(Resource):

    @Decorators.req_login
    @enable_cors
    def post(self, side, user_id):
        """
            Upload Front and Back of the IdCard
        """
        form_id = py_.get(request.args, "form_id")
        try:
            if 'file' not in request.files or side not in Enums.CardIdSide.list():
                return ResponseMsg.INVALID.to_json(), 400
            file = request.files["file"]
            Controllers.Form.upload_card_id_img(user_id, form_id, file, side)
        except Exception as e:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/upload-attached-file/<form_id>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class UploadAttachedFile(Resource):

    @Decorators.req_login
    @enable_cors
    def post(self, form_id, user_id):
        """
            Upload Attached File
        """
        try:
            if 'file' not in request.files:
                return ResponseMsg.INVALID.to_json(), 400
            file = request.files["file"]
            Controllers.Form.upload_attached_file(user_id, form_id, file)
        except Exception as e:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/publish/<form_id>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class Publish(Resource):

    @Decorators.req_login
    @enable_cors
    def post(self, form_id, user_id):
        """
            Publish A Form
        """
        Controllers.Form.publish_form(user_id, form_id)
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class Fetch(Resource):

    @Decorators.req_admin
    @enable_cors
    def get(self):
        """
            Admin Fetch Forms
        """
        page = py_.get(request.args, "page", 1)
        page_size = py_.get(request.args, "page_size", 10)
        forms = Controllers.Form.fetch_forms(page, page_size)
        print(forms)
        return ResponseMsg.SUCCESS.to_json(data={"forms": forms}), 200


@api.route('/<form_id>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class GetById(Resource):

    @Decorators.req_admin
    @enable_cors
    def get(self, form_id):
        """
            Admin Get Form Detail
        """
        form = Controllers.Form.get_form_by_id(form_id)
        return ResponseMsg.SUCCESS.to_json(data=form), 200


@api.route('/approve/<form_id>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class Approve(Resource):

    @Decorators.req_admin
    @enable_cors
    def get(self, form_id):
        """
            Admin Approve Form
        """
        Controllers.Form.approve_form(form_id)
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/reject/<form_id>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class Reject(Resource):

    @Decorators.req_admin
    @enable_cors
    def get(self, form_id):
        """
            Admin Reject Form
        """
        Controllers.Form.reject_form(form_id)
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/me')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class MyFroms(Resource):

    @Decorators.req_login
    @enable_cors
    def get(self, user_id):
        """
            Fetch my forms
        """
        page = py_.get(request.args, "page", 1)
        page_size = py_.get(request.args, "page_size", 10)
        forms = Controllers.Form.fetch_my_forms(user_id, page, page_size)
        return ResponseMsg.SUCCESS.to_json(data={"forms": forms}), 200


@api.route('/me/<form_id>')
@api.doc(responses=FormMeta.RESPONSE_CODE)
class MyFromById(Resource):

    @Decorators.req_login
    @enable_cors
    def get(self, form_id, user_id):
        """
            Get my form by id
        """
        form = Controllers.Form.get_my_form_by_id(user_id, form_id)
        return ResponseMsg.SUCCESS.to_json(data=form), 200
