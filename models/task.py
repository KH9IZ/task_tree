# -*- coding: UTF-8 -*-
"""Task model for interaction with database"""

from models import db
from models.user import User


class Task(db.Model):
    """Task model for interaction with database"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, comment="Unique identifier of task")
    title = db.Column(db.String(64), nullable=False, comment="Name of task")
    description = db.Column(db.Text(1024), nullable=True, comment="Detailed information about task")
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True,
                          comment="Task for which current task is subtask")
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    owner = db.relationship('User', backref=db.backref('tasks', lazy='dynamic'), lazy=True)
    parent = db.relationship('Task', remote_side=id, lazy=True, backref='subtasks')

    def __init__(self, title: str = None, description: str = None, parent=None, owner: User = None, **kwargs):
        """Task model for interaction with database
        :param title: Title of Task
        :param description: Detailed description of Task
        :param parent: Parent task, it means Task for which this Task is subtask
        :param owner: User who own this Task
        :param kwargs: Alternative params: parent_id, owner_id. Extra param: id
        :param parent_id: ID of parent (alternative for parent)
        :param owner_id: ID of owner (alternative for owner)
        :param id: ID of Task
        """
        self.title = title
        self.description = description
        if kwargs.get('parent_id'):
            self.parent_id = kwargs['parent_id']
        else:
            self.parent = parent

        if kwargs.get('owner_id'):
            self.owner_id = kwargs['owner_id']
        else:
            self.owner = owner

        if kwargs.get('id'):
            self.id = kwargs['id']