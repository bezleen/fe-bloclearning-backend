
import pydash as py_
from flask import request, current_app, redirect, abort
from flask_restx import Resource, marshal

import src.decorators as Decorators
import src.controllers as Controllers
import json

from src.schemas import ProjectsMeta


from src.resp_code import ResponseMsg
from src.middlewares.http import enable_cors


api = ProjectsMeta.api


@api.route('')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Fetch(Resource):
    """
        Get all projects
    """
    @api.marshal_with(ProjectsMeta.response)
    # @Decorators.req_login
    @enable_cors
    def get(self):
        page = py_.get(request.args, "page", 1)
        page_size = py_.get(request.args, "page_size", 10)
        all_projects = Controllers.Projects.get_all_projects(page, page_size)
        return ResponseMsg.SUCCESS.to_json(data={"projects": all_projects})


@api.route('/<project_id>')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class GetById(Resource):
    """
        Get project by id
    """
    @api.marshal_with(ProjectsMeta.response)
    # @Decorators.req_login
    @enable_cors
    def get(self, project_id):
        project = Controllers.Projects.get_project_by_id(project_id)
        return ResponseMsg.SUCCESS.to_json(data={"project": project})


@api.route('/initialize')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Initialize(Resource):

    @api.expect(ProjectsMeta.in_initialize)
    @api.marshal_with(ProjectsMeta.response)
    @Decorators.req_login
    @enable_cors
    def post(self, user_id):
        """
            Initialize a project
        """
        data = marshal(request.get_json(), ProjectsMeta.in_initialize)
        result = Controllers.Projects.init_project(user_id, data)
        if not result:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data=result)


@api.route('/upload_thumbnail/<project_id>')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Thumbnail(Resource):

    @api.marshal_with(ProjectsMeta.response)
    @Decorators.req_login
    @enable_cors
    def post(self, project_id, user_id):
        """
            Upload Thumbnail Of Project
        """
        try:
            if 'file' not in request.files:
                return ResponseMsg.INVALID.to_json(), 400
            file = request.files["file"]
            Controllers.Projects.upload_thumbnail(user_id, project_id, file)
        except Exception as e:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/publish/<project_id>')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Publish(Resource):

    @api.marshal_with(ProjectsMeta.response)
    @Decorators.req_login
    @enable_cors
    def post(self, project_id, user_id):
        """
            Publish A Project 
        """
        Controllers.Projects.user_publish_project(project_id, user_id)
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/approve/<project_id>')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Approve(Resource):

    @Decorators.req_admin
    @enable_cors
    def post(self, project_id):
        """
            Admin Approve A Project 
        """
        result = Controllers.Projects.user_publish_project(project_id)
        if not result:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data={}), 200


@api.route('/reject/<project_id>')
@api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Reject(Resource):

    @Decorators.req_admin
    @enable_cors
    def post(self, project_id):
        """
            Admin Reject A Project 
        """
        result = Controllers.Projects.admin_reject_project(project_id)
        if not result:
            return ResponseMsg.INVALID.to_json(), 400
        return ResponseMsg.SUCCESS.to_json(data={}), 200
