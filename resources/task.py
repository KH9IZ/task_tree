# -*- coding UTF-8 -*-
"""Submodule with Task API implementation"""

# External imports
from flask_restful import Resource, marshal_with, fields, reqparse, abort

# Internal imports
from security import auth
from resources import api
from models.task import Task
from models import db

task_fields: dict = {
    'id': fields.Integer,  # TODO remove
    'title': fields.String,
    'description': fields.String,
    'parent_uri': fields.String(
        attribute=lambda task: api.url_for(TaskAPI, task_id=task.parent_id, _external=True) if task.parent_id else None
    ),
    'subtasks_uris': fields.List(
        fields.String,
        attribute=lambda task: [api.url_for(TaskAPI, task_id=subtask.id, _external=True) for subtask in task.subtasks]
    )
    # TODO: add url to get all subtasks
    # This code wrote by genius 😎
}

# Configure parser of arguments for Task
task_parser = reqparse.RequestParser()
task_parser.add_argument('title', type=str, help="The title cant be empty and should be string")
task_parser.add_argument('description', type=str, help="Type of Description is 'text'")


@api.resource('/tasks', endpoint='tasks')
class TaskListAPI(Resource):
    """Resource representing list of tasks and additionally creating new tree"""
    decorators = [auth.login_required]

    @marshal_with(task_fields)
    def get(self) -> list:  # TODO: limit count of returning tasks
        """Return list of user's tasks"""
        tasks = Task.query.filter_by(owner=auth.current_user()).all()
        return tasks

    @marshal_with(task_fields)
    def post(self) -> Task:
        """Create new **root** task"""
        args = task_parser.parse_args()
        if args['title'] is None:
            abort(400, message="Title required.")
        new_task = Task(args['title'], args['description'], owner=auth.current_user())
        db.session.add(new_task)
        db.session.commit()
        return new_task


@api.resource('/task/<int:task_id>', endpoint='task')
class TaskAPI(Resource):
    """Resource representing Task instance"""
    decorators = [auth.login_required]

    @marshal_with(task_fields)
    def get(self, task_id: int) -> Task:
        """Return one task
        :param task_id: ID of task to return
        """
        task = Task.query.filter_by(id=task_id, owner=auth.current_user()).first_or_404()
        return task

    @marshal_with(task_fields)
    def post(self, task_id: int) -> Task:
        """Create new subtask
        :param task_id: parent_id of new task
        """
        args: dict = task_parser.parse_args()
        if args['title'] is None:
            abort(400, message="Title required.")
        new_task = Task(args['title'], args['description'], parent_id=task_id, owner=auth.current_user())
        db.session.add(new_task)
        db.session.commit()
        return new_task

    @marshal_with(task_fields)
    def put(self, task_id: int) -> Task:
        """Edit all fields of task
        :param task_id: task which to edit
        """
        task = Task.query.filter_by(id=task_id, owner=auth.current_user()).first_or_404()
        args = task_parser.parse_args()
        if args['title'] is None:
            abort(400, message="Title required.")
        task.title = args['title']
        task.description = args['description']
        db.session.commit()
        return task

    @marshal_with(task_fields)
    def patch(self, task_id: int) -> Task:
        """Edit fields of task selectively
        :param task_id: task to edit
        """
        task = Task.query.filter_by(id=task_id, owner=auth.current_user()).first_or_404()
        args = task_parser.parse_args()
        if args['title']:
            task.title = args['title']
        if args['description']:
            task.description = args['description']
        db.session.commit()
        return task

    @marshal_with(task_fields)
    def delete(self, task_id: int) -> Task:
        """Delete task
        :param task_id: task to delete
        """
        task = Task.query.filter_by(id=task_id, owner=auth.current_user()).first_or_404()
        db.session.delete(task)
        db.session.commit()
        return task
