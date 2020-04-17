from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty


class IkSplineHandle(Transform):

    start_joint = ObjectProperty(
        name='start_joint'
    )

    end_effector = ObjectProperty(
        name='end_effector'
    )

    end_joint = ObjectProperty(
        name='end_joint'
    )

    solver = DataProperty(
        name='solver'
    )

    curve = ObjectProperty(
        name='curve'
    )

    def __init__(self, **kwargs):
        super(IkSplineHandle, self).__init__(**kwargs)
        self.node_type = 'ikHandle'
        self.solver = 'ikSplineSolver'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) != 3:
            raise Exception('You must pass two joints and a curve as arguments to create a {0}'.format(cls.__name__))

        start_joint, end_joint, curve = args
        kwargs.setdefault('index', end_joint.index)
        kwargs['root_name'] = '{0}_{1}_{2}'.format(start_joint.name, end_joint.name, curve.name)
        kwargs['end_joint'] = end_joint
        kwargs['start_joint'] = start_joint
        kwargs['curve'] = curve
        effector_kwargs = dict(kwargs)
        effector_kwargs['parent'] = end_joint.parent
        end_effector = controller.create_object(
            'IkEffector',
            **effector_kwargs
        )
        end_joint.plugs['tx'].connect_to(end_effector.plugs['tx'])
        end_joint.plugs['ty'].connect_to(end_effector.plugs['ty'])
        end_joint.plugs['tz'].connect_to(end_effector.plugs['tz'])
        kwargs['end_effector'] = end_effector
        this = super(IkSplineHandle, cls).create(controller, **kwargs)
        return this

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_ik_spline_handle(
            self.start_joint.m_object,
            self.end_effector.m_object,
            self.curve.m_object,
            solver=self.solver,
            parent=self.parent,
        )
