from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty


class IkHandle(Transform):

    end_effector = ObjectProperty(
        name='end_effector'
    )

    start_joint = ObjectProperty(
        name='start_joint'
    )

    end_joint = ObjectProperty(
        name='end_joint'
    )

    solver = DataProperty(
        name='solver'
    )

    def __init__(self, **kwargs):
        super(IkHandle, self).__init__(**kwargs)
        self.node_type = 'ikHandle'
        self.solver = 'ikSCsolver'

    @classmethod
    def create(cls, controller, *args, **kwargs):

        if len(args) != 2:
            raise Exception('You must pass two joints as arguments to create a %s' % cls.__name__)

        start_joint, end_joint = args
        if not isinstance(start_joint, Joint) or not isinstance(end_joint, Joint):
            raise Exception('You must use two "Joint" node_objects as arguments when you call "create_ik_handle"')

        kwargs.setdefault('matrix', end_joint.get_matrix())
        kwargs.setdefault('index', end_joint.index)
        kwargs['root_name'] = '%s_%s' % (start_joint.name, end_joint.name)

        effector_kwargs = dict(kwargs)
        effector_kwargs['parent'] = end_joint.parent

        end_effector = controller.create_object(
            'IkEffector',
            **effector_kwargs
        )

        end_joint.plugs['tx'].connect_to(end_effector.plugs['tx'])
        end_joint.plugs['ty'].connect_to(end_effector.plugs['ty'])
        end_joint.plugs['tz'].connect_to(end_effector.plugs['tz'])

        kwargs.setdefault('end_effector', end_effector)
        kwargs.setdefault('parent', end_effector)
        kwargs.setdefault('start_joint', start_joint)
        kwargs.setdefault('end_joint', end_joint)
        kwargs.setdefault('solver', 'ikSCsolver')

        return super(IkHandle, cls).create(controller, **kwargs)

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_ik_handle(
            self.start_joint.m_object,
            self.end_effector.m_object,
            solver=self.solver,
            parent=self.parent.m_object,
            name=self.name
        )


class IkEffector(Transform):

    def __init__(self, **kwargs):
        super(IkEffector, self).__init__(**kwargs)
        self.node_type = 'ikEffector'
