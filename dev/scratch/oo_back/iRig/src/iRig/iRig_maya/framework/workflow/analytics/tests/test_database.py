import os
import json
import workflow.analytics.database as db


def test_build():

    session = db.initialize_session('C:/Temp/foo.db')
    user = db.initialize_user(
        session,
        os.environ['USERNAME']
    )

    with open('%s/movies.json' % os.path.dirname(__file__.replace('\\', '/')), mode='r') as f:
        for movie_data in json.loads(f.read()):
            project = db.initialize_project(
                session,
                movie_data['title']
            )
            for i in range(10):
                entity = db.initialize_entity(
                    session,
                    project,
                    'Digidouble_%s' % i
                )
                for workflow_name in ['build_rig', 'build_model']:

                    workflow = db.initialize_workflow(session, entity, workflow_name)

                    action = db.Action(
                        workflow=workflow,
                        name='do a thing',
                        code='import sys\nprint sys.path'
                    )

                    execution = db.Execution(
                        workflow=workflow,
                        action=action,
                        user=user,
                        code='import sys\nprint sys.path',
                        success=True
                    )

            session.add(project)
            session.commit()


if __name__ == '__main__':
    test_build()