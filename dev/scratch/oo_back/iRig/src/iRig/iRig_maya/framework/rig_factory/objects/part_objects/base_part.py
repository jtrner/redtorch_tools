from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
import rig_factory.environment as env


class BasePart(Transform):

    pretty_name = DataProperty(
        name='pretty_name'
    )
    owner = ObjectProperty(
        name='owner'
    )
    disconnected_joints = DataProperty(
        name='disconnected_joints',
        default_value=False
    )
    joint_chain = DataProperty(
        name='joint_chain',
        default_value=True
    )
    joints = ObjectListProperty(
        name='joints'
    )
    deform_joints = ObjectListProperty(
        name='deform_joints'
    )
    base_deform_joints = ObjectListProperty(
        name='base_deform_joints'
    )
    handles = ObjectListProperty(
        name='handles'
    )
    color = DataProperty(
        name='color'
    )
    toggle_class = DataProperty(
        name='toggle_class'
    )
    version = DataProperty(
        name='version',
        default_value='0.0.0'
    )
    utility_group = ObjectProperty(
        name='utility_group'
    )
    parent_joint = ObjectProperty(
        name='parent_joint'
    )
    parent_capsule = ObjectProperty(
        name='parent_capsule'
    )
    default_settings = dict()

    def __init__(self, **kwargs):
        for x in self.default_settings:
            kwargs.setdefault(x, self.default_settings[x])
        super(BasePart, self).__init__(**kwargs)

    def teardown(self):
        self.controller.disown(self)
        super(BasePart, self).teardown()

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('side', 'center')
        if not kwargs.get('owner', None):
            raise StandardError('You must provide an owner to create a part')
        this = super(BasePart, cls).create(controller, **kwargs)
        if not isinstance(this.owner, BasePart):
            this.owner.parts.append(this)
        this.plugs['overrideEnabled'].set_value(True)
        if controller.scene.maya_version > '2015':
            if this.color is not None:
                color = this.color
            else:
                color = env.colors[this.side]
            this.plugs['overrideRGBColors'].set_value(True)
            this.plugs['overrideColorR'].set_value(color[0])
            this.plugs['overrideColorG'].set_value(color[1])
            this.plugs['overrideColorB'].set_value(color[2])
        else:
            index_color = env.index_colors[this.side]
            this.plugs['overrideColor'].set_value(index_color)
        return this

    def get_handle_positions(self):
        return dict((x.name, list(x.get_translation())) for x in self.get_handles())

    def get_index_handle_positions(self):
        return [self.controller.xform(x, q=True, t=True, ws=True)for x in self.get_handles()]

    def set_index_handle_positions(self, positions):
        if self.handles:
            handle_count = len(self.handles)
            for x in range(len(positions)):
                if x < handle_count:
                    self.controller.xform(
                        self.handles[x].get_selection_string(),
                        ws=True,
                        t=positions[x]
                    )

    def get_vertex_data(self):
        """
        Creates A Dictionary with an entry for each handle. Each key is the name of the handle, and each value is a list
        of Tuples two items long. Each tuple represents a vertex, the first item being the mesh name and the second
        item being the vertex index
        :return: dict
        """
        return dict((h.name, [(x.mesh.get_selection_string(), x.index) for x in h.vertices]) for h in self.handles)

    def get_joint_positions(self):
        return dict((x.name, list(x.get_matrix())) for x in self.get_joints())

    def get_joints(self):
        return self.joints

    def get_deform_joints(self):
        return self.deform_joints

    def get_base_deform_joints(self):
        return self.base_deform_joints

    def get_handles(self):
        return self.controller.get_handles(self)

    def set_handles(self, handles):
        self.handles = handles
        for handle in handles:
            handle.owner = self

    def set_handle_positions(self, positions):
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        for handle_name in positions:
            if handle_name in handle_map:
                handle_map[handle_name].plugs['translate'].set_value(positions[handle_name])
            else:
                print 'WARNING: Handle "%s" did not exist. Unable to set position' % handle_name

    def snap_to_mesh(self, mesh):
        self.controller.snap_part_to_mesh(self, mesh)

    def snap_to_selected_mesh(self):
        self.controller.snap_part_to_selected_mesh(self)

    def create_handles(self, count, **kwargs):
        return self.controller.create_handles(
            self,
            count,
            **kwargs
        )

    def get_root(self):
        if self.owner:
            return self.owner.get_root()
        else:
            raise StandardError('No owner. unable to find root from "%s"' % self)

    def post_create(self, **kwargs):
        for joint in self.joints:
            joint.parent_part = self

    def finish_create(self, **kwargs):
        pass

    def mirror(self):
        self.controller.mirror_part(self)

    def set_owner(self, owner):
        self.controller.set_owner(self, owner)

    def disown(self):
        self.controller.disown(self)

    def set_vertex_data(self, vertex_data):
        root = self.get_root()
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        for handle_name in vertex_data:
            if handle_name in handle_map:
                vertices = []
                for mesh_name, index in vertex_data[handle_name]:
                    if mesh_name in root.geometry:
                        vertex = root.geometry[mesh_name].get_vertex(index)
                        vertices.append(vertex)

                handle_map[handle_name].snap_to_vertices(vertices)
            else:
                print 'WARNING: Handle "%s" did not exist. Unable to set vertex_data' % handle_name

    def finalize(self):
        pass
