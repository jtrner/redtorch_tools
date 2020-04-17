import uuid
import json
import datetime
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship, backref
Base = declarative_base()


def initialize_object(self, *args, **kwargs):
    if not kwargs and args and isinstance(args[0], dict):
        kwargs = args[0]
    for key in kwargs:
        setattr(self, key, kwargs[key])
    if not self.id:
        self.id = str(uuid.uuid4())


class TextPickleType(TypeDecorator):

    impl = Text(256)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value


def process_result_value(self, value, dialect):
    if value is not None:
        value = json.loads(value)
    return value


class Project(Base):

    __tablename__ = 'project'

    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)
    data = Column(TextPickleType())
    created = Column(DateTime, default=datetime.datetime.now)
    entities = sqlalchemy.orm.relationship(
        'Entity',
        backref=sqlalchemy.orm.backref(
            "project",
            remote_side='Project.id'
        )
    )

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__()
        initialize_object(self, *args, **kwargs)

    def __repr__(self):
        return "Project(id=%s, name=%s)" % (
                    self.id,
                    self.name
                )


class Entity(Base):

    __tablename__ = 'entity'

    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)
    data = Column(TextPickleType())
    created = Column(DateTime, default=datetime.datetime.now())
    project_id = Column(
        Integer,
        ForeignKey('project.id')
    )

    workflows = relationship(
        'Workflow',
        backref=backref(
            "entity",
            remote_side='Entity.id'
        )
    )

    def __init__(self, *args, **kwargs):
        super(Entity, self).__init__()
        initialize_object(self, *args, **kwargs)

    def __repr__(self):
        return "Entity(id=%s, name=%s)" % (
                    self.id,
                    self.name
                )


class Workflow(Base):

    __tablename__ = 'workflow'

    id = Column(
        String(100),
        primary_key=True
    )
    data = Column(TextPickleType())
    name = Column(
        String(100),
        nullable=False
    )
    created = Column(DateTime, default=datetime.datetime.now())
    entity_id = Column(
        Integer,
        ForeignKey('entity.id')
    )

    actions = relationship(
        'Action',
        backref=backref(
            "workflow",
            remote_side='Workflow.id'
        )
    )

    def __init__(self, *args, **kwargs):
        super(Workflow, self).__init__()
        initialize_object(self, *args, **kwargs)

    def __repr__(self):
        return "Workflow(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )


class Action(Base):

    __tablename__ = 'action'

    id = Column(String(100), primary_key=True)
    data = Column(TextPickleType())
    name = Column(String(100), nullable=False)
    code = Column(String(1000), nullable=True)
    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    created = Column(DateTime, default=datetime.datetime.now())

    executions = relationship(
        'Execution',
        backref=backref(
            "action",
            remote_side='Action.id'
        )
    )

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__()
        initialize_object(self, *args, **kwargs)

    def __repr__(self):
        return "Action(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )


class Execution(Base):

    __tablename__ = 'execution'

    id = Column(String(100), primary_key=True)
    data = Column(TextPickleType())
    duration = Column(String(100), nullable=True)
    action_id = Column(Integer, ForeignKey('action.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    code = Column(String(1000), nullable=True)
    name = Column(
        String(100),
        nullable=False
    )
    traceback = Column(String(1000), nullable=True)
    executed = Column(DateTime, default=datetime.datetime.now())
    success = Column(Boolean())

    def __init__(self, *args, **kwargs):
        super(Execution, self).__init__()
        initialize_object(self, *args, **kwargs)

    def __repr__(self):
        return "Execution(id=%r)" % (
                    self.id
                )

class User(Base):

    __tablename__ = 'user'

    id = Column(
        String(100),
        primary_key=True
    )
    data = Column(TextPickleType())
    name = Column(
        String(100),
        nullable=False
    )
    created = Column(DateTime, default=datetime.datetime.now())

    executions = relationship(
        'Execution',
        backref=backref(
            "user",
            remote_side='User.id'
        )
    )

    def __init__(self, *args, **kwargs):
        super(User, self).__init__()
        initialize_object(self, *args, **kwargs)

    def __repr__(self):
        return "User(id=%r, name=%r)" % (
                    self.id,
                    str(self.name)
                )
