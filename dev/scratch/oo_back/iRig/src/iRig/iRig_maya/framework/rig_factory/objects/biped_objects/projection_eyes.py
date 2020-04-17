from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.biped_objects.eye_array import EyeArray, EyeArrayGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_math.matrix import Matrix
import traceback


class ProjectionEyesGuide(EyeArrayGuide):

    default_settings = {
        'root_name': 'projection_eyes',
        'size': 1.0,
        'side': 'center',
        'left_eye_target': '',
        'right_eye_target': '',
    }

    left_eye_target = DataProperty(
        name='left_eye_target'
    )
    right_eye_target = DataProperty(
        name='right_eye_target'
    )

    def __init__(self, **kwargs):
        super(ProjectionEyesGuide, self).__init__(**kwargs)
        self.toggle_class = ProjectionEyes.__name__

    # Un-comment this to have the eye parts be created with names that
    # have their root included in them (making them unique).
    # Currently this follows how the `eye_array` functions (not unique).
    #
    # def create_members(self):
    #     super(EyeArrayGuide, self).create_members()
    #     root_name = self.root_name
    #     left_eye = self.create_part(
    #         EyeGuide,
    #         parent=self,
    #         root_name='%s_eye' % root_name,
    #         side='left'
    #     )
    #     right_eye = self.create_part(
    #         EyeGuide,
    #         parent=self,
    #         root_name='%s_eye' % root_name,
    #         side='right'
    #     )
    #     self.left_eye = left_eye
    #     self.right_eye = right_eye
    #     self.set_handle_positions(BIPED_POSITIONS)


class ProjectionEyes(EyeArray):

    left_eye_target = DataProperty(
        name='left_eye_target'
    )
    right_eye_target = DataProperty(
        name='right_eye_target'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(ProjectionEyes, cls).create(controller, **kwargs)

        this.left_eye_target = kwargs['guide_blueprint']['left_eye_target']
        this.right_eye_target = kwargs['guide_blueprint']['right_eye_target']

        return this

    def post_create(self, **kwargs):

        if not self.parts:
            return None

        root = self.get_root()

        root_name = self.root_name

        left_eye_part = self.parts[0]
        right_eye_part = self.parts[1]
        if not self.right_eye_target:
            right_eye_part.plugs['v'].set_value(False)

        left_eye_joint = left_eye_part.joints[0]
        right_eye_joint = right_eye_part.joints[0]

        left_arrow_handle = left_eye_part.handles[0]
        right_arrow_handle = right_eye_part.handles[0]

        left_aim_handle = left_eye_part.handles[1]
        right_aim_handle = right_eye_part.handles[1]

        left_aim_matrix = left_aim_handle.get_matrix()
        right_aim_matrix = right_aim_handle.get_matrix()

        left_aim_translation = left_aim_matrix.get_translation()
        right_aim_translation = right_aim_matrix.get_translation()

        if self.right_eye_target:
            average_translation = (left_aim_translation + right_aim_translation) / 2
            distance = (left_aim_translation - right_aim_translation).mag()
        else:
            average_translation = left_aim_translation
            distance = 1

        matrix = Matrix(*average_translation.data)

        shape_matrix = Matrix()
        shape_matrix.set_scale([
            self.size * 2 + distance,
            self.size * 2,
            self.size * 2,
        ])

        left_eye_target = self.left_eye_target
        right_eye_target = self.right_eye_target

        eye_handle = self.create_handle(
            shape='square',
            size=self.size,
            matrix=matrix,
            root_name='%s_aim' % self.root_name,
            axis='z'
        )
        eye_handle.plugs['shape_matrix'].set_value(list(shape_matrix))

        # Sets up cross eye.

        cross_eye_plug = eye_handle.create_plug(
            'cross_eye',
            attributeType='double',
            keyable=True,
            defaultValue=0.0
        )

        left_cross_eye_transform = self.create_child(
            Transform,
            root_name=root_name + '_L_crosseye',
            parent=eye_handle
        )
        cross_eye_plug.connect_to(
            left_cross_eye_transform.plugs['translateX']
        )
        left_aim_handle.groups[0].set_parent(left_cross_eye_transform)

        if right_eye_target:
            right_cross_eye_transform = self.create_child(
                Transform,
                root_name=root_name + '_R_crosseye',
                parent=eye_handle
            )
            right_cross_eye_reverse = self.create_child(
                DependNode,
                node_type='reverse',
                root_name=root_name + '_crosseye_reverse'
            )
            cross_eye_plug.connect_to(right_cross_eye_reverse.plugs['inputX'])
            right_cross_eye_reverse.plugs['outputX'].connect_to(
                right_cross_eye_transform.plugs['translateX']
            )
            right_aim_handle.groups[0].set_parent(right_cross_eye_transform)

        root.add_plugs([
            eye_handle.plugs['tx'],
            eye_handle.plugs['ty'],
            eye_handle.plugs['tz'],
            eye_handle.plugs['rz'],
            cross_eye_plug
        ])

        # Import shader network and projection nodes.
        self.controller.scene.file(
            r'Y:\MAW\assets\type\Character\Eyes\publish\eye_lamberts\eyes_rigging_lambert.ma',
            i=True,
        )

        try:
            self.controller.scene.sets(
                left_eye_target,
                edit=True,
                forceElement="Eye_flounder_anim_LSG",
            )
            if right_eye_target:
                self.controller.scene.sets(
                    right_eye_target,
                    edit=True,
                    forceElement="Eye_flounder_anim_RSG",
                )

            # Creates the left and right projection setups.
            items = zip(
                (left_arrow_handle, right_arrow_handle),
                (left_aim_handle, right_aim_handle),
                (left_eye_joint, right_eye_joint),
                'LR' if right_eye_target else 'L',
            )
            for arrow_handle, aim_handle, joint, side in items:

                # Variables for the loaded settings.

                aov_locator = 'eye_%s_AOV_place3dTexture_ExportData' % side
                env_locator = 'eye_%s_envSphere_place3dTexture_ExportData' % side

                dilate_locator = 'ATTR_iris_inner_dilation_%s_ExportData' % side
                dilate_node = '%s_Pupil_Dilation' % side
                dilate_value = self.controller.scene.getAttr(dilate_node + '.inFloat')

                hue_locator = 'ATTR_iris_color_%s_floatConstant_ExportData' % side
                hue_node = '%s_Iris_RemapHSV' % side
                hue_value = self.controller.scene.getAttr(hue_locator + '.outFloat')

                eye_place_3d = 'eye_%s_place3dTexture' % side
                place_locator = 'eye_%s_place3dTexture_ExportData' % side
                sclera_place_3d = 'eye_%s_sclera_place3dTexture_ExportData' % side

                # Sets the eye color, and dilation amount.

                self.controller.scene.setAttr(
                    dilate_node + ".inFloat",
                    dilate_value,
                )
                self.controller.scene.setAttr(
                    hue_node + ".hue[1].hue_FloatValue",
                    hue_value,
                )

                # Eye plane allowing head squash to have an effect on the
                # part.

                plane_transform = self.create_child(
                    Transform,
                    root_name='%s_%s_plane' % (side, root_name),
                )
                plane_mesh = plane_transform.create_child(
                    Mesh,
                    root_name='%s_%s_planeShape' % (side, root_name),
                )
                root.geometry[plane_mesh.name] = plane_mesh

                plane_poly_plane = plane_transform.create_child(
                    DependNode,
                    node_type='polyPlane',
                    root_name='%s_%s_polyPlane' % (side, root_name),
                )
                plane_poly_plane.plugs.set_values(
                    subdivisionsWidth=1,
                    subdivisionsHeight=1,
                )
                plane_poly_plane.plugs['output'].connect_to(
                    plane_mesh.plugs['inMesh'],
                )
                self.controller.create_parent_constraint(
                    arrow_handle,
                    plane_transform,
                )

                # Surface point for mounting the projections.

                surface_point = self.create_child(
                    SurfacePoint,
                    root_name='%s_%s_follicle' % (side, root_name),
                    surface=plane_mesh,
                )
                surface_point.follicle.plugs.set_values(
                    parameterU=.5,
                    parameterV=.5,
                )

                # Transform containing the projection.
                # Is parent constrained to the follicle.

                matrix = Matrix(
                    self.controller.scene.xform(
                        place_locator,
                        query=True,
                        worldSpace=True,
                        translation=True,
                    ),
                )
                matrix.set_scale(
                    self.controller.scene.xform(
                        place_locator,
                        query=True,
                        worldSpace=True,
                        scale=True,
                    ),
                )
                sc_matrix = Matrix(
                    self.controller.scene.xform(
                        sclera_place_3d,
                        query=True,
                        worldSpace=True,
                        translation=True,
                    ),
                )
                sc_matrix.set_scale(
                    self.controller.scene.xform(
                        sclera_place_3d,
                        query=True,
                        worldSpace=True,
                        scale=True,
                    ),
                )

                value_grp = surface_point.create_child(
                    Transform,
                    root_name='%s_%s_value' % (side, root_name),
                    matrix=matrix,
                )

                self.scale_multiply_transform.plugs['scaleX'].connect_to(
                    surface_point.plugs['scaleX']
                )
                self.scale_multiply_transform.plugs['scaleX'].connect_to(
                    surface_point.plugs['scaleY']
                )
                self.scale_multiply_transform.plugs['scaleX'].connect_to(
                    surface_point.plugs['scaleZ']
                )

                # Reparents projections, and creates and connects related
                # attributes. This includes attributes not found on the
                # projection itself.

                self.controller.scene.parent(
                    eye_place_3d,
                    value_grp.name,
                )
                self.controller.scene.xform(
                    eye_place_3d,
                    translation=(0, 0, 0),
                    rotation=(0, 0, 0),
                    scale=(1, 1, 1),
                    shear=(0, 0, 0)
                )
                self.controller.scene.connectAttr(
                    aim_handle.name + '.rotateZ',
                    eye_place_3d + '.rotateZ',
                )
                self.controller.scene.connectAttr(
                    aim_handle.name + '.scaleX',
                    eye_place_3d + '.scaleX',
                )
                self.controller.scene.connectAttr(
                    aim_handle.name + '.scaleY',
                    eye_place_3d + '.scaleY',
                )
                self.controller.scene.connectAttr(
                    aim_handle.name + '.scaleZ',
                    eye_place_3d + '.scaleZ',
                )

                # Connects the projections to the data locators used for
                # LRC.

                self.controller.scene.parentConstraint(
                    eye_place_3d,
                    place_locator,
                )
                self.controller.scene.scaleConstraint(
                    eye_place_3d,
                    place_locator,
                )
                self.controller.scene.parentConstraint(
                    eye_place_3d,
                    aov_locator,
                )
                self.controller.scene.scaleConstraint(
                    eye_place_3d,
                    aov_locator,
                )

                # Adds and animation node in the middle of the network.
                # Not sure why, but it was in the example Sean gave me so I
                # added it anyways.

                dilate_anim_curve = self.create_child(
                    DependNode,
                    node_type='animCurveUA',
                    name='%s_%s_dilate_anim_curve' % (side, root_name),
                )
                self.controller.scene.keyTangent(
                    dilate_anim_curve.name,
                    inTangentType="linear",
                    outTangentType="linear",
                )
                self.controller.scene.setKeyframe(
                    dilate_anim_curve.name,
                    float=0,
                    value=0.02,
                )
                self.controller.scene.setKeyframe(
                    dilate_anim_curve.name,
                    float=50,
                    value=dilate_value,
                )
                self.controller.scene.setKeyframe(
                    dilate_anim_curve.name,
                    float=100,
                    value=0.28,
                )
                aim_handle.plugs['dilate'].connect_to(
                    dilate_anim_curve.plugs['input'],
                )
                self.controller.scene.connectAttr(
                    dilate_anim_curve.name + ".output",
                    dilate_node + ".inFloat",
                )

                # More data locator hookups.

                self.controller.scene.connectAttr(
                    dilate_node + ".outFloat",
                    dilate_locator+ ".inFloat",
                )
                self.controller.scene.connectAttr(
                    hue_node + ".hue[1].hue_FloatValue",
                    hue_locator + ".outFloat",
                )

                if self.controller.scene.objExists(env_locator):
                    self.controller.scene.parentConstraint(
                        self.name,
                        env_locator,
                        maintainOffset=True,
                    )
                    self.controller.scene.scaleConstraint(
                        self.name,
                        env_locator,
                    )

                if self.controller.scene.objExists(sclera_place_3d):
                    self.controller.scene.parentConstraint(
                        self.name,
                        sclera_place_3d,
                        maintainOffset=True,
                    )
                    self.controller.scene.scaleConstraint(
                        self.name,
                        sclera_place_3d,
                        maintainOffset=True
                    )

        except StandardError as e:
            self.controller.raise_warning('Projection Eyes FAILED.  This must be fixed before publishing this rig.')
            print e

        if self.controller.scene.objExists('|Eye_Utility_Grp'):
            self.controller.scene.delete(
                '|Eye_Utility_Grp'
            )
