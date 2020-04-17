import PySignal
from rig_factory.controllers.node_controller import NodeController
from rig_factory.objects.blendshape_objects.blendshape import BlendshapeTarget, Blendshape, BlendshapeGroup, \
    BlendshapeInbetween
import rig_factory.utilities.blendshape_utilities.blueprint_utilities as blt
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.shader import Shader
import rig_factory


class BlendshapeController(NodeController):

    blendshape_changed_signal = PySignal.ClassSignal()
    blendshape_group_changed_signal = PySignal.ClassSignal()

    def __init__(self):
        super(BlendshapeController, self).__init__()

    def reset(self, *args):
        super(BlendshapeController, self).reset()

    def add_blendshape_base_geometry(self, blendshape, *geometry):
        for g in geometry:
            blendshape.base_geometry.append(g)
        self.scene.add_blendshape_base_geometry(
            blendshape.m_object,
            *[x.m_object for x in geometry]
        )


    def create_blendshape(self, *base_geometry, **kwargs):
        if len(base_geometry) < 1:
            raise Exception('provide geometry')
        kwargs['base_geometry'] = list(base_geometry)
        this = self.create_object(
            Blendshape,
            **kwargs
        )
        return this

    def flip_blendshape_weights(self, *args, **kwargs):
        return self.scene.flip_blendshape_weights(*args, **kwargs)

    def create_blendshape_group(self, blendshape, *targets, **kwargs):
        if isinstance(blendshape, Blendshape):
            if blendshape.index:
                kwargs['root_name'] = '%s_%s' % (kwargs.get('root_name', 'target'), rig_factory.index_dictionary[blendshape.index])
            kwargs['index'] = blendshape.get_next_weight_index()

            kwargs.setdefault(
                'parent',
                blendshape
            )
            blendshape_group = self.create_object(
                BlendshapeGroup,
                **kwargs
            )
            self.start_ownership_signal.emit(
                blendshape_group,
                blendshape
            )
            blendshape_group.blendshape = blendshape
            blendshape.blendshape_groups.append(blendshape_group)
            self.end_ownership_signal.emit(
                blendshape_group,
                blendshape
            )
            for i, target in enumerate(targets):
                weight = 1.0 / len(targets) * (i+1)
                self.create_blendshape_inbetween(
                    blendshape_group,
                    target,
                    weight=weight
                )
            return blendshape_group
        else:
            raise TypeError('Invalid type "%s"' % type(blendshape))

    def create_blendshape_inbetween(self, group, *targets, **kwargs):
        if isinstance(group, BlendshapeGroup):
            blendshape = group.blendshape
            base_geometry = blendshape.base_geometry
            kwargs.setdefault('weight', 1.0)
            if targets and len(targets) != len(base_geometry):
                raise Exception('target shape mismatch')
            kwargs.setdefault('index', len(group.blendshape_inbetweens))
            kwargs.setdefault('root_name', group.root_name)
            kwargs.setdefault('side', group.side)
            kwargs.setdefault('parent', group)
            this = self.create_object(
                BlendshapeInbetween,
                **kwargs
            )
            self.start_ownership_signal.emit(this, group)
            this.blendshape_group = group
            group.blendshape_inbetweens.append(this)
            self.end_ownership_signal.emit(this, group)
            #self.create_blendshape_geometry(this, *targets)
            for target in targets:
                this.create_blendshape_target(
                    target,
                )
            return this
        else:
            raise TypeError('Invalid type "%s"' % type(group))

    def create_blendshape_target(self, inbetween, target_geometry=None, **kwargs):
        if isinstance(inbetween, BlendshapeInbetween):
            kwargs.setdefault('parent', inbetween)
            kwargs.setdefault('index', len(inbetween.target_shapes))
            kwargs.setdefault('root_name', '%s_%s' % (
                inbetween.root_name,
                rig_factory.index_dictionary[inbetween.index]
            ))
            kwargs.setdefault('side', inbetween.side)
            target_shape = self.create_object(
                BlendshapeTarget,
                **kwargs
            )
            target_shape.blendshape_inbetween = inbetween
            inbetween.target_shapes.append(target_shape)
            target_shape.target_geometry = target_geometry
            if target_geometry and inbetween.weight:
                self.connect_target_shape(target_shape)
            return target_shape
        else:
            raise TypeError('Invalid type "%s"' % type(inbetween))

    def disconnect_target_shape(self, target_shape):
        if isinstance(target_shape, BlendshapeTarget):
            target_geometry = target_shape.target_geometry
            if target_geometry:
                blendshape_inbetween = target_shape.blendshape_inbetween
                blendshape_group = blendshape_inbetween.blendshape_group
                blendshape = blendshape_group.blendshape
                shape_index = blendshape_inbetween.target_shapes.index(target_shape)
                base_geometry = blendshape.base_geometry[shape_index]
                self.scene.remove_blendshape_target(
                    blendshape.m_object,
                    base_geometry.m_object,
                    blendshape_group.index,
                    target_geometry.m_object,
                    blendshape_inbetween.weight
                )
        else:
            raise TypeError('Invalid type "%s"' % type(target_shape))

    def connect_target_shape(self, target_shape):
        if isinstance(target_shape, BlendshapeTarget):
            target_geometry = target_shape.target_geometry
            blendshape_inbetween = target_shape.blendshape_inbetween
            blendshape_group = blendshape_inbetween.blendshape_group
            blendshape = blendshape_group.blendshape
            shape_index = blendshape_inbetween.target_shapes.index(target_shape)
            base_geometry = blendshape.base_geometry[shape_index]
            base_geometry.plugs['visibility'].set_value(True)
            self.scene.create_blendshape_target(
                blendshape.m_object,
                base_geometry.m_object,
                blendshape_group.index,
                target_geometry.m_object,
                blendshape_inbetween.weight
            )
        else:
            raise TypeError('Invalid type "%s"' % type(target_shape))

    def disconnnect_targets(self, blendshape_group):
        if isinstance(blendshape_group, BlendshapeGroup):
            self.scene.clear_blendshape_group_targets(
                blendshape_group.blendshape.m_object,
                blendshape_group.index
            )
        else:
            raise TypeError('Invalid type "%s"' % type(blendshape_group))

    def connect_targets(self, blendshape_group):

        if isinstance(blendshape_group, BlendshapeGroup):
            blendshape = blendshape_group.blendshape
            base_geometry = blendshape.base_geometry
            for blendshape_inbetween in blendshape_group.blendshape_inbetweens:
                for i, target_shape in enumerate(blendshape_inbetween.target_shapes):
                    self.scene.create_blendshape_target(
                        blendshape.m_object,
                        base_geometry[i].m_object,
                        blendshape_group.index,
                        target_shape.target_geometry.m_object,
                        blendshape_inbetween.weight
                    )

        else:
            raise TypeError('Invalid type "%s"' % type(blendshape_group))

    def create_blendshape_geometry(self, blendshape_inbetween, *targets):
        """
        When users create an inbetween and don't provide mesh targets, we build a set of mesh targets by
        duplicating the base geometry.

        I think I should actually always build mesh targets and tot accept targets keywords
        Maybe xfer the mesh shape?

        """

        blendshape_group = blendshape_inbetween.blendshape_group
        blendshape = blendshape_group.blendshape
        inbetween_index = len(blendshape_group.blendshape_inbetweens)
        if not targets:
            mesh_group = self.create_object(
                Transform,
                root_name='%s_%s_%s_target' % (
                    blendshape_group.root_name,
                    blendshape_group.index,
                    inbetween_index
                ),
                parent=blendshape_inbetween
            )
            blendshape_inbetween.mesh_group = mesh_group
        for g, base_geometry in enumerate(blendshape.base_geometry):

            if not targets:
                target_parent = mesh_group.create_child(
                    Transform,
                    root_name=mesh_group.root_name,
                    index=g
                )
                new_mesh = self.copy_mesh(base_geometry, target_parent)
                self.assign_sculpt_shader(new_mesh)
                new_mesh = targets[g]
            else:
                new_mesh = targets[g]
            self.create_blendshape_target(
                blendshape_inbetween,
                target_geometry=new_mesh
            )
        if not targets:

            bounding_box = self.get_bounding_box(mesh_group)
            top = bounding_box[4]
            bottom = bounding_box[1]
            left = bounding_box[0]
            right = bounding_box[3]
            if right - left < 0.01:
                raise Exception('Mesh is too tiny!')
            x_spacing = 0.1
            y_spacing = 0.1
            x_position = (right - left + x_spacing) * (group_index + 1)
            y_position = (top - bottom + y_spacing) * inbetween_index
            mesh_group.plugs['tx'].set_value(x_position)
            mesh_group.plugs['ty'].set_value(y_position)

            return mesh_group

    def assign_sculpt_shader(self, mesh):
        if not self.sculpt_shader:
            shader = self.create_object(
                Shader,
                node_type='lambert',
                root_name='sculpt_shader',
                side=None
            )
            shader.plugs['ambientColorR'].set_value(0.0)
            shader.plugs['ambientColorG'].set_value(0.5)
            shader.plugs['ambientColorB'].set_value(1)
            shader.plugs['colorR'].set_value(0.175)
            shader.plugs['colorG'].set_value(0.509)
            shader.plugs['colorB'].set_value(0.739)
            shader.plugs['incandescenceR'].set_value(0.0)
            shader.plugs['incandescenceG'].set_value(0.0)
            shader.plugs['incandescenceB'].set_value(0.0)
            shader.plugs['diffuse'].set_value(0.5)
            self.sculpt_shader = shader
        self.assign_shader(self.sculpt_shader, mesh)

    def copy_mesh(self, mesh_name, parent_transform, name=None):

        if not isinstance(mesh_name, basestring):
            raise TypeError('"%s" was not string' % mesh_name)
        if not isinstance(parent_transform, Transform):
            raise TypeError('"%s" was not mesh' % parent_transform)

        if name is None:
            name = self.name_function(
                Mesh.__name__,
                root_name=parent_transform.root_name,
                index=parent_transform.index,
                side=parent_transform.side
            )
        new_mesh = Mesh(
            controller=self,
            root_name=parent_transform.root_name,
            index=parent_transform.index,
            side=parent_transform.side,
            parent=parent_transform
        )
        m_object = self.scene.get_m_object(mesh_name)
        new_mesh.m_object = self.scene.copy_mesh(
            m_object,
            parent_transform.m_object
        )
        new_mesh.set_name(name)
        self.register_item(new_mesh)
        self.named_objects[name] = new_mesh
        return new_mesh

    def copy_mesh_shape(self, target_mesh, base_mesh):
        self.scene.copy_mesh_shape(
            self.scene.get_m_object(target_mesh),
            base_mesh.m_object
        )

    def copy_selected_mesh_shape(self, mesh):
        self.scene.copy_selected_mesh_shape(mesh.m_object)

    def export_alembic(self, path, *nodes):
        self.scene.export_alembic(path, *nodes)

    # def view_blueprint(self):
    #     blt.view_blueprint(self)
    #
    # def get_blueprint(self, rig):
    #     return blt.get_blueprint(rig)
    #
    # def build_blueprint(self, blueprint):
    #     return blt.build_blueprint(self, blueprint)

    def set_blendshape_group(self, blendshape_group):
        self.blendshape_group_changed_signal.emit(blendshape_group)



if __name__ == '__main__':
    controller = BlendshapeController.get_controller(standalone=True)
    import maya.cmds as mc
    mc.loadPlugin('AbcImport')
    mc.loadPlugin('AbcExport')
    mc.AbcImport(
        r'D:\rigging_library\rig_builds\ambassador\ambassador.abc',
        mode='import'
    )
    head_mesh = controller.initialize_node('MOB_headShapeDeformed')
    smile_mesh = controller.initialize_node('mchr_ambassador_headShapeDeformed')

    face_blendahape = controller.create_blendshape(
        head_mesh,
        root_name='face'
    )
    face_blendahape.create_blendshape_group(
        smile_mesh,
        root_name='smile'
    )
