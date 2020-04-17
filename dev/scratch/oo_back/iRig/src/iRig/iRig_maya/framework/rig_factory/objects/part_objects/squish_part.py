"""
TODO:
    Remove `reorder_deformers` from finish create WITHOUT breaking any
    existing blueprints.
"""

from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.deformer_objects.squash import Squash
from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.deformer_objects.bend import Bend
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.mesh import Mesh
from nonlinear_part import NonlinearPartGuide, NonlinearPart
import rig_factory.environment as env


class SquishPartGuide(NonlinearPartGuide):

    default_settings = {
        'root_name': 'squish',
        'tx_multiplier': 1,
        'ty_multiplier': 1,
        'tz_multiplier': 1,
        'squash_max_expand_position': 0.5,
    }

    tx_multiplier = DataProperty(
        name='tx_multiplier'
    )
    ty_multiplier = DataProperty(
        name='ty_multiplier'
    )
    tz_multiplier = DataProperty(
        name='tz_multiplier'
    )
    squash_max_expand_position = DataProperty(
        name='squash_max_expand_position'
    )

    @classmethod
    def create(self, *args, **kwargs):
        kwargs.setdefault('root_name', 'squish')
        self.tx_multiplier = kwargs.pop('tx_multiplier', 1)
        self.ty_multiplier = kwargs.pop('ty_multiplier', 1)
        self.tz_multiplier = kwargs.pop('tz_multiplier', 1)
        self.squash_max_expand_position = kwargs.pop('squash_max_expand_position', 0.5)
        this = super(SquishPartGuide, self).create(*args, **kwargs)

        this.create_plug(
            'txMultiplier',
            at='double',
            k=True,
            dv=1.0
        )
        this.create_plug(
            'tyMultiplier',
            at='double',
            k=True,
            dv=1.0
        )
        this.create_plug(
            'tzMultiplier',
            at='double',
            k=True,
            dv=1.0
        )
        this.create_plug(
            'squashMaxExpandPosition',
            at='double',
            k=True,
            dv=1.0,
            min=.01,
            max=.99
        )
        this.plugs.set_values(
            txMultiplier=self.tx_multiplier,
            tyMultiplier=self.ty_multiplier,
            tzMultiplier=self.tz_multiplier,
            squashMaxExpandPosition=self.squash_max_expand_position
        )

        return this

    def __init__(self, **kwargs):
        super(SquishPartGuide, self).__init__(**kwargs)
        self.toggle_class = SquishPart.__name__

    def get_toggle_blueprint(self):
        blueprint = super(SquishPartGuide, self).get_toggle_blueprint()
        blueprint['tx_multiplier'] = self.plugs['txMultiplier'].get_value()
        blueprint['ty_multiplier'] = self.plugs['tyMultiplier'].get_value()
        blueprint['tz_multiplier'] = self.plugs['tzMultiplier'].get_value()
        blueprint['squash_max_expand_position'] = self.plugs['squashMaxExpandPosition'].get_value()
        return blueprint

    def get_blueprint(self):
        blueprint = super(SquishPartGuide, self).get_blueprint()
        blueprint['tx_multiplier'] = self.plugs['txMultiplier'].get_value()
        blueprint['ty_multiplier'] = self.plugs['tyMultiplier'].get_value()
        blueprint['tz_multiplier'] = self.plugs['tzMultiplier'].get_value()
        blueprint['squash_max_expand_position'] = self.plugs['squashMaxExpandPosition'].get_value()
        return blueprint


class SquishPart(NonlinearPart):

    tx_multiplier = DataProperty(
        name='tx_multiplier'
    )
    ty_multiplier = DataProperty(
        name='ty_multiplier'
    )
    tz_multiplier = DataProperty(
        name='tz_multiplier'
    )
    squash_max_expand_position = DataProperty(
        name='squash_max_expand_position'
    )

    def __init__(self, **kwargs):
        self.tx_multiplier = kwargs.pop('tx_multiplier', 1)
        self.ty_multiplier = kwargs.pop('ty_multiplier', 1)
        self.tz_multiplier = kwargs.pop('tz_multiplier', 1)
        self.squash_max_expand_position = kwargs.pop('squash_max_expand_position', 0.5)
        super(SquishPart, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(SquishPart, cls).create(controller, **kwargs)
        root = this.get_root()
        size = this.size
        matrices = this.matrices
        controller.create_parent_constraint(
            this,
            this.joints[0],
            mo=True
        )
        squash_handle = this.create_handle(
            shape='circle',
            size=size * 4.0,
            matrix=matrices[1]
        )
        controller.create_parent_constraint(
            squash_handle,
            this.joints[1],
            mo=False
        )

        this.handles = [squash_handle]
        root.add_plugs(
            squash_handle.plugs['tx'],
            squash_handle.plugs['ty'],
            squash_handle.plugs['tz'],
        )
        return this

    def create_deformers(self, geometry):
        if not geometry:
            raise Exception('You must pass some geometry as arguments to create_deformers')
        size = self.size
        joint_1 = self.joints[0]
        joint_2 = self.joints[1]
        position_1 = joint_1.get_matrix().get_translation()
        position_2 = joint_2.get_matrix().get_translation()
        distance = (position_2 - position_1).mag()
        create_kwargs = {
            'side': self.side,
            'size': size,
            'index': self.index,
            'parent': joint_1
        }
        tx_multiplier = self.tx_multiplier
        ty_multiplier = self.ty_multiplier
        tz_multiplier = self.tz_multiplier

        squash_deformer = self.controller.create_nonlinear_deformer(
            Squash,
            geometry,
            root_name=self.root_name + '_side_squash',
            **create_kwargs
        )
        squash_deformer.plugs['maxExpandPos'].set_value(
            self.squash_max_expand_position
        )

        bend_deformer_x = self.controller.create_nonlinear_deformer(
            Bend,
            geometry,
            root_name=self.root_name + '_front_bend',
            **create_kwargs
        )

        bend_deformer_z = self.controller.create_nonlinear_deformer(
            Bend,
            geometry,
            root_name=self.root_name + '_side_bend',
            **create_kwargs
        )

        size_multiply_node = self.create_child(
            DependNode,
            node_type='multiplyDivide'
        )
        size_multiply_node.plugs['input2X'].set_value(
            1.0 / size * 10 * tx_multiplier
        )
        size_multiply_node.plugs['input2Y'].set_value(
            1.0 / distance * ty_multiplier
        )
        size_multiply_node.plugs['input2Z'].set_value(
            1.0 / size * 10 * tz_multiplier
        )

        self.handles[0].plugs['translateY'].connect_to(size_multiply_node.plugs['input1Y'])
        self.handles[0].plugs['translateX'].connect_to(size_multiply_node.plugs['input1X'])
        self.handles[0].plugs['translateZ'].connect_to(size_multiply_node.plugs['input1Z'])

        size_multiply_node.plugs['outputX'].connect_to(bend_deformer_x.plugs['curvature'])
        size_multiply_node.plugs['outputZ'].connect_to(bend_deformer_z.plugs['curvature'])
        size_multiply_node.plugs['outputY'].connect_to(squash_deformer.plugs['factor'])
        bend_deformer_x.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 0.0, 0.0],
            scaleX=distance,
            scaleY=distance,
            scaleZ=distance,
            visibility=False
        )
        bend_deformer_z.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[x * -90.0 for x in env.aim_vector],
            scaleX=distance,
            scaleY=distance,
            scaleZ=distance,
            visibility=False
        )
        squash_deformer.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 0.0, 0.0],
            scaleX=size,
            scaleY=distance,
            scaleZ=size,
            visibility=False
        )
        self.deformers = [squash_deformer, bend_deformer_x, bend_deformer_z]
        self.geometry = geometry
        return self.deformers


    def get_toggle_blueprint(self):
        blueprint = super(SquishPart, self).get_toggle_blueprint()
        blueprint['tx_multiplier'] = self.tx_multiplier
        blueprint['ty_multiplier'] = self.ty_multiplier
        blueprint['tz_multiplier'] = self.tz_multiplier
        blueprint['squash_max_expand_position'] = self.squash_max_expand_position
        return blueprint

    def get_blueprint(self):
        blueprint = super(SquishPart, self).get_blueprint()
        blueprint['tx_multiplier'] = self.tx_multiplier
        blueprint['ty_multiplier'] = self.ty_multiplier
        blueprint['tz_multiplier'] = self.tz_multiplier
        blueprint['squash_max_expand_position'] = self.squash_max_expand_position
        return blueprint
