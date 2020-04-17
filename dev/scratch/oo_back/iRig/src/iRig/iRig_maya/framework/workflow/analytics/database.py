from sqlalchemy.orm import scoped_session, sessionmaker
from table_objects import *


def initialize_session(database_path):
    engine = sqlalchemy.create_engine("sqlite:///%s" % database_path)
    engine.echo = False
    Base.metadata.bind = engine
    Base.metadata.create_all()
    session = scoped_session(sessionmaker())
    session.configure(bind=engine)
    return session


def query_executions(session, project=None, entity=None, workflow=None, action=None, user=None):
    query = session.query(Execution).join(Action.workflow)
    if action:
        query.filter(Action.name == action)
    if workflow:
        query.filter(Workflow.name == workflow)
    query.join(Workflow.entity)
    if entity:
        query.filter(Entity.name == entity)
    query.join(Entity.project)
    if project:
        query.filter(Project.name == project)
    query.join(Execution.user)
    if user:
        query.filter(User.name == user)
    return query


def initialize_user(session, user_name):
    existing_user = session.query(User).filter(User.name == user_name).first()
    if existing_user:
        return existing_user
    new_user = User(name=user_name)
    session.add(new_user)
    session.commit()
    return new_user


def initialize_project(session, project_name):
    existing_project = session.query(Project)\
        .filter(Project.name == project_name).first()

    if existing_project:
        return existing_project
    new_project = Project(name=project_name)
    session.add(new_project)
    session.commit()
    return new_project


def initialize_entity(session, project, entity_name):
    existing_entity = session.query(Entity)\
        .filter(Entity.name == entity_name)\
        .join(Entity.project)\
        .filter(Project.id == project.id).first()

    if existing_entity:
        return existing_entity
    new_project = Entity(
        name=entity_name,
        project=project
    )
    session.add(new_project)
    session.commit()
    return new_project


def get_workflow(session, id):
    return session.query(Workflow)\
        .filter(Workflow.id == id).first()


def create_workflow(session, **kwargs):
    new_workflow = Workflow(
        **kwargs
    )
    session.add(new_workflow)
    session.commit()
    return new_workflow


def initialize_workflow(session, entity, workflow_name):
    existing_workflow = session.query(Workflow)\
        .filter(Workflow.name == workflow_name)\
        .join(Workflow.entity).filter(Entity.id == entity.id).first()
    if existing_workflow:
        return existing_workflow
    return create_workflow(
        session,
        entity=entity,
        name=workflow_name
    )


def get_action(session, id):
    return session.query(Action)\
        .filter(Action.id == id).first()


def create_action(session, **kwargs):
    new_action = Action(
        **kwargs
    )
    session.add(new_action)
    session.commit()
    return new_action


def create_execution(session, **kwargs):
    new_execution = Execution(
        **kwargs
    )
    session.add(new_execution)
    session.commit()
    return new_execution