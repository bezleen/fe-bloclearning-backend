
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
class Mails(Resource):
    """
        Get all projects
    """
    @api.marshal_with(ProjectsMeta.response)
    # @Decorators.req_login
    @enable_cors
    def get(self, user_id):
        all_projects = Controllers.Projects.get_all_projects()
        return ResponseMsg.SUCCESS.to_json(data={"projects": all_projects})


@ api.route('/<project_id>')
@ api.doc(responses=ProjectsMeta.RESPONSE_CODE)
class Mail(Resource):
    """
        Get project by id
    """
    @api.marshal_with(ProjectsMeta.response)
    # @Decorators.req_login
    @enable_cors
    def get(self, project_id, user_id):
        project = Controllers.Projects.get_project_by_id(project_id)
        return ResponseMsg.SUCCESS.to_json(data={"project": project})
