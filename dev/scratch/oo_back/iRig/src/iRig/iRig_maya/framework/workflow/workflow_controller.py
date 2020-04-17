import uuid
import json
import os
import gc
import PySignal
import shutil
import traceback
import time
# This should be done differently
try:
    import maya.cmds as mc
except:
    pass
from rig_factory.controllers.object_controller import ObjectController
from workflow.workflow_objects.action import Action
import workflow.analytics.database as db
import rig_factory.objects as obs
try:
    import file_tools as ft
except ImportError:
    ft = None
import re


class WorkflowController(ObjectController):

    selection_changed_signal = PySignal.ClassSignal()
    critical_signal = PySignal.ClassSignal()
    warning_signal = PySignal.ClassSignal()
    message_signal = PySignal.ClassSignal()
    busy_signal = PySignal.ClassSignal()
    current_entity_changed_signal = PySignal.ClassSignal()
    project_changed_signal = PySignal.ClassSignal()
    entity_changed_signal = PySignal.ClassSignal()
    user_changed_signal = PySignal.ClassSignal()
    select_item_signal = PySignal.ClassSignal()

    def __init__(self):
        super(WorkflowController, self).__init__()
        self.current_action = None
        self.rig_controller = None
        self.project = None
        self.entity = None
        self.user = None
        self.current_entity = None
        self.entity_variables = dict()
        self.active_entities = dict()
        self.name = None
        self.uuid = str(uuid.uuid4())
        self.database_object = None
        self.development = False
        self.pipe_base = None
        self.asset_type = None
        self.session = None
        if os.path.exists('G:/Rigging/Paxton/analytics.db'):
            self.session = db.initialize_session('G:/Rigging/Paxton/analytics.db')
        else:
            self.session = db.initialize_session('%s/analytics.db' % os.path.expanduser('~'))

        self.user = db.initialize_user(
            self.session,
            os.environ.get(
                'USERNAME',
                'default_user'
            )
        )
        self.pipe_base = os.environ.get(
            'PIPE_BASE',
            ''
        )
        if not os.path.exists(self.pipe_base):
            self.pipe_base = 'D:/Pipeline/{user}/dev/git_repo/pipeline_monolith'.format(user=self.user)

        self.asset_type = os.environ.get(
            'TT_ASSTYPE',
            'Character'
        )
        self.step = os.environ.get(
            'TT_STEPCODE',
            'rig'
        )
        self.entity_type = os.environ.get(
            'TT_ENTTYPE',
            'Asset'
        )
        self.project = db.initialize_project(
            self.session,
            os.environ.get(
                'TT_PROJCODE',
                'LMM'
            )
        )
        self.entity = db.initialize_entity(
            self.session,
            self.project,
            os.environ.get(
                'TT_ENTNAME',
                'Ariel'
            )
        )

        self.current_entity = self.entity
        self.ez_path = None
        self.update_ez_path()

    def update_ez_path(self):
        if ft:
            self.ez_path = ft.EzAs(
                project='global_icon_show',
                TT_ENTTYPE=self.entity_type,
                TT_PROJCODE=self.project.name,
                TT_ENTNAME=self.current_entity.name,
                SERVER_BASE='Y:',
                TT_ASSTYPE=self.asset_type,
                TT_STEPCODE=self.step,
                TT_PACKAGE='Maya',
                TT_USER=self.user.name,
                PIPE_BASE=self.pipe_base
            )

    def set_user(self, user_name):
        if not isinstance(user_name, basestring):
            raise Exception('User name must be type : string')
        self.user = db.initialize_user(
            self.session,
            user_name
        )
        self.user_changed_signal.emit(self.user)
        self.update_ez_path()

    def set_project(self, project_name):
        if not isinstance(project_name, basestring):
            raise Exception('Project name must be type : string')
        self.project = db.initialize_project(
            self.session,
            project_name
        )
        self.project_changed_signal.emit(self.project)
        self.update_ez_path()

    def set_entity(self, entity_name):
        """
        This can leverage self.existing_entities for a speed boost
        """
        if not isinstance(entity_name, basestring):
            raise Exception('Entity name must be type : string')
        self.entity = db.initialize_entity(
            self.session,
            self.project,
            entity_name
        )
        self.set_current_entity(self.entity.name)
        self.entity_changed_signal.emit(self.entity)
        self.update_ez_path()

    def set_current_entity(self, entity_name):
        if not isinstance(entity_name, basestring):
            raise Exception('Entity must be type : string')
        if not self.project:
            raise Exception('You cannot set entity until the project has been set')
        self.current_entity = None
        if entity_name:
            self.current_entity = db.initialize_entity(
                self.session,
                self.project,
                entity_name
            )
            self.active_entities[entity_name] = self.current_entity
        self.current_entity_changed_signal.emit(self.current_entity)
        self.update_ez_path()

    def pull_from_database(self):
        self.database_object = db.get_workflow(
            self.session,
            self.uuid
        )
        if not self.database_object:
            self.database_object = db.create_workflow(
                self.session,
                id=self.uuid,
                name=self.name,
                entity=self.entity
            )

    def push_to_database(self):
        if not self.database_object:
            self.pull_from_database()
        self.database_object.name = self.name
        self.database_object.id = self.uuid
        self.session.commit()

    def reset(self, *args):
        if self.entity:
            self.set_current_entity(self.entity.name)
        self.set_root(None)
        self.current_action = None
        self.entity_variables = dict()
        self.load_entity_variables()
        self.database_object = None
        gc.collect()

    def get_next_action(self):
        if self.root:
            actions = self.root.get_descendants()
            current_index = actions.index(self.current_action) + 1 if self.current_action else 0
            if current_index < len(actions):
                return actions[current_index]

    def next(self):
        next_action = self.get_next_action()
        if next_action:
            self.select_item_signal.emit(next_action)
        else:
            self.message_signal.emit('Workflow complete.')
            raise StopIteration('Workflow complete.')
        self.execute_action(
            next_action
        )
        last_action = self.current_action
        self.current_action = next_action
        if last_action:
            self.item_changed_signal.emit(last_action)
        if self.current_action.cache_scene:
            self.save_cache(self.current_action)
        self.item_changed_signal.emit(self.current_action)
        if self.rig_controller:
            self.rig_controller.scene.refresh()
        return self.current_action

    def __iter__(self):
        return self

    def close(self):
        """Raise GeneratorExit inside generator.
        """
        try:
            self.throw(GeneratorExit)
        except (GeneratorExit, StopIteration):
            pass
        else:
            raise RuntimeError("generator ignored GeneratorExit")

    def throw(self, type=None, value=None, traceback=None):
        raise StopIteration

    def execute_action(self, action):
        self.busy_signal.emit(True)
        self.load_entity_variables()
        namespace = dict()
        namespace.update(self.entity_variables)
        namespace['controller'] = self
        namespace.update(obs.classes)
        code_lines = list()
        code_lines.append("def execute_code(controller):")
        if action.code:
            for line in action.code.split('\n'):
                code_lines.append("    %s" % line)
        else:
            code_lines.append("    pass")
        code_block = '\n'.join(code_lines)
        start = time.time()

        try:
            exec (code_block, namespace)
            my_function = namespace['execute_code']
            return_value = my_function(self.rig_controller)
            action.critical = False
            action.success = True
            self.item_changed_signal.emit(action)
            self.busy_signal.emit(False)
            self.item_changed_signal.emit(action)
            db.create_execution(
                self.session,
                action=action.database_object,
                user=self.user,
                name=action.name,
                code=action.code,
                success=True,
                duration=str(time.time()-start)
            )
            return return_value

        except StopIteration, e:
            # Catch "StopIteration" raised by action code
            action.critical = True
            action.success = False
            self.item_changed_signal.emit(action)
            self.busy_signal.emit(False)
            print traceback.format_exc()
            db.create_execution(
                self.session,
                action=action.database_object,
                user=self.user,
                code=action.code,
                name=action.name,
                success=False,
                duration=str(time.time() - start),
                traceback=traceback.format_exc()
            )
            raise Exception('Iteration stopped by action.')

        except Exception, e:
            # Catch all other exceptions in the action code
            #if self.current_action:q
            #    self.select_item_signal.emit(self.current_action)
            action.critical = True
            action.success = False
            self.item_changed_signal.emit(action)
            self.critical_signal.emit('Workflow Action Error. See script editor for details.')
            self.busy_signal.emit(False)
            print traceback.format_exc()
            db.create_execution(
                self.session,
                action=action.database_object,
                user=self.user,
                code=action.code,
                name=action.name,
                success=False,
                traceback=traceback.format_exc(),
                duration=str(time.time() - start)


            )
            raise e

    def save_cache(self, action):
        cache_path = self.get_cache_path(action)
        with open(self.get_cache_json_path(action), mode='w') as f:
            f.write(json.dumps(self.serialize()))
        mc.file(rn=cache_path)
        mc.file(s=True)
        print 'saved cache to : %s' % cache_path

    def load_cache(self, action):
        cache_path = self.get_cache_path(action)
        mc.file(cache_path, o=True, f=True)
        blueprint = self.get_blueprint()
        self.root_changed_signal.emit(None)
        self.build_blueprint(blueprint)
        self.load_entity_variables()
        with open(self.get_cache_json_path(action), mode='r') as f:
            data = json.loads(f.read())
            self.current_action = self.objects[data['current_action']]

    def create_name(self, *args, **kwargs):
        return kwargs['name']

    def critical(self, message):
        print 'Critical: %s' % message
        self.critical_signal.emit(message)
        next_action = self.get_next_action()
        if next_action:
            next_action.critical = True
            self.item_changed_signal.emit(next_action)
        raise StopIteration

    def warning(self, message):
        print 'Warning: %s' % message
        self.warning_signal.emit(message)
        next_action = self.get_next_action()
        if next_action:
            next_action.critical = True
            self.item_changed_signal.emit(next_action)
        raise StopIteration

    def message(self, message):
        print 'Message: %s' % message
        self.message_signal.emit(message)
        next_action = self.get_next_action()
        if next_action:
            next_action.critical = True
            self.item_changed_signal.emit(next_action)

    def get_blueprint(self):
        if not self.root:
            raise Exception('No root found')
        return dict(
            name=self.name,
            uuid=self.uuid,
            actions=self.get_action_blueprint(self.root)
        )

    def get_action_blueprint(self, root):
        blueprint = dict(
            name=root.name,
            code=root.code,
            break_point=root.break_point,
            cache_scene=root.cache_scene,
            documentation=root.documentation,
            uuid=root.uuid
        )
        child_blueprints = []
        for part in root.children:
            child_blueprints.append(self.get_action_blueprint(part))
        blueprint['children'] = child_blueprints
        return blueprint

    def build_blueprint(self, data):
        self.reset()
        self.name = data['name']
        self.uuid = data.get('uuid', str(uuid.uuid4()))
        self.push_to_database()
        root = self.build_action_blueprint(data['actions'])
        self.set_root(root)
        return root

    def build_action_blueprint(self, data):
        child_data = data.pop('children', [])
        action = self.create_object(
            Action,
            **data
        )
        if not action.controller:
            raise Exception('No Controler')
        for x in child_data:
            x['parent'] = action
            self.build_action_blueprint(x)
        return action

    def serialize(self):
        return dict(
            item_data=super(WorkflowController, self).serialize(),
            current_action=self.current_action.uuid if self.current_action else None
        )

    def deserialize(self, data):
        self.reset()
        super(WorkflowController, self).deserialize(data['item_data'])
        self.current_action = self.objects[data['current_action']]
        self.item_changed_signal.emit(self.current_action)

    def export_workflow(self, json_path):
        if not self.root:
            raise Exception('No root found')
        if os.path.exists(json_path):
            self.backup_file(json_path)

        with open(json_path, mode='w') as f:
            f.write(json.dumps(
                self.get_blueprint(),
                sort_keys=True,
                indent=4,
                separators=(',', ': '))
            )

    def import_workflow(self, json_path):
        self.reset()
        with open(json_path, mode='r') as f:
            root = self.build_blueprint(json.loads(f.read()))
            self.set_root(root)

    def set_parent(self, child, parent):
        if not isinstance(parent, Action):
            raise Exception('Cannot parent to type "%s"' % type(parent))
        if child.parent == parent or child.parent:
            self.unparent(child)
        self.start_parent_signal.emit(child, parent)
        child.parent = parent
        parent.children.append(child)
        self.end_parent_signal.emit(child, parent)

    def insert_child(self, index, parent, child):
        if child.parent == parent or child.parent:
            self.unparent(child)
        self.start_parent_signal.emit(child, parent, child_index=index)
        child.parent = parent
        parent.children.insert(index, child)
        self.end_parent_signal.emit(child, parent)

    def get_skin_path(self, geometry_name):
        return '%s/%s.json' % (self.get_skin_directory(), geometry_name)

    def get_skin_directory(self):
        skin_directory = '%s/skin_clusters' % self.get_data_directory()
        if not os.path.exists(skin_directory):
            os.makedirs(skin_directory)
        return skin_directory

    def get_data_path(self, name, extension):
        data_directory = self.get_data_directory()
        return '%s/%s.%s' % (data_directory, name, extension)

    def get_project_directory(self):
        if self.ez_path:
            directory = str(self.ez_path.base)
            if not os.path.exists(str(directory)) or directory is None:
                raise OSError('Project directory does not exist. Got {dir}'.format(dir=directory))
        else:
            directory = '%s/local_projects/%s' % (
                os.path.expanduser('~'),
                self.project.name
            )
            if not os.path.exists(str(directory)) or directory is None:
                try_make_dirs(directory)
        return directory

    def get_current_entity_directory(self):
        if self.ez_path:
            directory = str(self.ez_path.entity)
            if not os.path.exists(str(directory)) or directory is None:
                raise OSError('Entity directory does not exist. Got {dir}'.format(dir=directory))
        else:
            directory = '%s/%s' % (
                self.get_project_directory(),
                self.current_entity.name
            )
            if not os.path.exists(str(directory)) or directory is None:
                try_make_dirs(directory)
        return directory

    def get_alembic_directory(self):
        if self.ez_path:
            directory = str(self.ez_path.products / 'abc')
        else:
            directory = '%s/abc' % self.get_current_entity_directory()

        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception, e:
                print e.message
        return directory

    def get_scene_cache_directory(self):
        if self.ez_path:
            directory = str(self.ez_path.elems / 'scene_cache')
        else:
            directory = '%s/scene_cache' % self.get_current_entity_directory()

        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception, e:
                print e.message
        return directory

    def get_data_directory(self):
        if self.ez_path:
            #------DELETE ONE DAY --------
            # This is so we don't break existing EAV workflows.. Eventually it should deleted
            old_path = str(self.ez_path.entity / 'elems' / 'Pipeline' / 'rig_data')
            if os.path.exists(old_path):
                return old_path
            #------DELETE ONE DAY --------

            data_path = str(self.ez_path.elems / 'rig_data')
        else:
            data_path = '%s/rig_data' % self.get_current_entity_directory()
        if not os.path.exists(data_path):
            try:
                os.makedirs(data_path)
            except Exception, e:
                print e.message
        return data_path

    def get_cache_path(self, action):
        cache_directory = '%s/workflow_caches' % (
            self.get_scene_cache_directory()
        )
        if not os.path.exists(cache_directory):
            try:
                os.makedirs(cache_directory)
            except Exception, e:
                print e.message
        return '%s/%s.mb' % (cache_directory, action.uuid)

    def get_cache_json_path(self, action):
        return self.get_cache_path(action).replace('.mb', '.json')

    def save_json_file(self, name, data):
        directory = self.get_data_directory()
        data_path = '%s/%s.json' % (directory, name)
        data_directory = os.path.dirname(data_path)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        if os.path.exists(data_path):
            self.backup_file(data_path)
        write_data(data_path, data)
        print 'Saved to : %s' % data_path

    def load_json_file(self, name):
        data_path = self.get_data_path(name, 'json')
        print 'loading from : %s' % data_path
        if os.path.exists(data_path):
            with open(data_path, mode='r') as f:
                return json.loads(f.read())

    def backup_file(self, path, id=uuid.uuid4()):
        directory = os.path.dirname(path)
        file_name = os.path.basename(path)
        elements = file_name.split('.')
        if len(elements) < 2:
            raise StandardError('Invalid path: %s' % path)
        suffix = elements[-1]
        name = '.'.join(elements[0:-1])
        if os.path.exists(path):
            versions_directory = '%s/versions' % directory
            if not os.path.exists(versions_directory):
                os.makedirs(versions_directory)
            version_path = '%s/%s_%s.%s' % (versions_directory, name, id, suffix)
            version_subdir = os.path.dirname(version_path)
            if not os.path.exists(version_subdir):
                os.makedirs(version_subdir)
            try:
                shutil.move(path, version_path)
            except Exception, e:
                print e.message
            if suffix == 'ma':
                json_path = path.replace('.ma', '_objects.json')
                if os.path.exists(json_path):
                    version_json_path = '%s/%s_%s_objects.json' % (versions_directory, name, id)
                    shutil.move(json_path, version_json_path)

    def get_entity_variables_directory(self):
        if self.ez_path:
            directory = str(self.ez_path.gen_elems / 'workflows' / 'entity_variables' / self.entity.name)
        else:
            directory = '%s/assets/gen_elems/workflows/entity_variables/%s' % (
                self.get_project_directory(),
                self.entity.name
            )
        if not os.path.exists(directory):
            try_make_dirs(directory)

        return directory

    def get_entity_variables_path(self):
        if self.name:
            safe_name = re.sub(
                ' |<|>|:"|/|\|\||\?|\*',
                '_',
                self.name
            )
            return '%s/%s.json' % (
                self.get_entity_variables_directory(),
                safe_name
            )

    def load_entity_variables(self):
        entity_variable_path = self.get_entity_variables_path()
        if entity_variable_path:
            if os.path.exists(entity_variable_path):
                with open(entity_variable_path, mode='r') as f:
                    try:
                        self.entity_variables = json.load(f)
                    except Exception, e:
                        print 'Unable to load entity variables\n%s' % e.message

    def set_entity_variables(self, **variables):
        try:
            json.dumps(variables)
        except Exception, e:
            raise TypeError('One or more entity variables was not json serializable')

        "Need to add UPDATE environment variables "
        self.entity_variables.update(variables)
        entity_variable_path = self.get_entity_variables_path()
        try:
            write_data(entity_variable_path, self.entity_variables)
        except Exception, e:
            print 'Unable to save entity variables\n%s' % e.message

    def update_entity_variables(self, **variables):
        try:
            json.dumps(variables)
        except Exception, e:
            raise TypeError('One or more entity variables was not json serializable')

        "Need to add UPDATE environment variables "
        self.entity_variables.update(variables)
        entity_variable_path = self.get_entity_variables_path()
        try:
            write_data(entity_variable_path, self.entity_variables)
        except Exception, e:
            print 'Unable to save entity variables\n%s' % e.message

    def get_post_scripts_directory(self):
        post_scripts_directory = '%s/post_scripts' % self.get_data_directory()
        if not os.path.exists(post_scripts_directory):
            os.makedirs(post_scripts_directory)
        return post_scripts_directory

    def get_finalize_scripts_directory(self):
        finalize_scripts_directory = '%s/finalize_scripts' % self.get_data_directory()
        if not os.path.exists(finalize_scripts_directory):
            os.makedirs(finalize_scripts_directory)
        return finalize_scripts_directory

def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))


def try_make_dirs(directory):
    try:
        os.makedirs(directory)
    except Exception, e:
        print e.message

