from rig_factory.objects.part_objects.part_array import PartArrayGuide, PartArray
from rig_factory.objects.biped_objects.eye import EyeGuide
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_math.matrix import Matrix
import rig_factory.positions as pos


class EyeArrayGuide(PartArrayGuide):

    default_settings = dict(
        root_name='eyes',
        size=1.0,
        side='center'
    )

    left_eye = ObjectProperty(
        name='left_eye'
    )
    right_eye = ObjectProperty(
        name='right_eye'
    )

    def __init__(self, **kwargs):
        super(EyeArrayGuide, self).__init__(**kwargs)
        self.toggle_class = EyeArray.__name__

    def create_members(self):
        super(EyeArrayGuide, self).create_members()
        left_eye = self.create_part(
            EyeGuide,
            parent=self,
            root_name='eye',
            side='left'
        )
        right_eye = self.create_part(
            EyeGuide,
            parent=self,
            root_name='eye',
            side='right'
        )
        self.left_eye = left_eye
        self.right_eye = right_eye
        self.set_handle_positions(pos.BIPED_POSITIONS)


class EyeArray(PartArray):

    def post_create(self, **kwargs):
        if self.parts:
            left_eye = self.parts[0]
            right_eye = self.parts[1]
            left_handle = left_eye.handles[1]
            right_handle = right_eye.handles[1]
            left_matrix = left_handle.get_matrix()
            right_matrix = right_handle.get_matrix()
            left_translation = left_matrix.get_translation()
            right_translation = right_matrix.get_translation()
            average_translation = (left_translation + right_translation) / 2
            distance = (left_translation - right_translation).mag()
            matrix = Matrix(*average_translation.data)
            shape_matrix = Matrix()
            shape_matrix.set_scale([(distance + (self.size * 2)), self.size * 2, self.size * 2])
            eye_handle = self.create_handle(
                shape='square',
                size=self.size,
                matrix=matrix,
                root_name='%s_aim' % self.root_name,
                axis='z'
            )
            cross_eye_plug = eye_handle.create_plug(
                'cross_eye',
                at='double',
                k=False,
                dv=0.0
            )
            eye_handle.plugs['shape_matrix'].set_value(list(shape_matrix))
            left_handle.groups[0].set_parent(eye_handle)
            right_handle.groups[0].set_parent(eye_handle)
            root = self.get_root()
            root.add_plugs([
                eye_handle.plugs['tx'],
                eye_handle.plugs['ty'],
                eye_handle.plugs['tz'],
                eye_handle.plugs['rz'],
                cross_eye_plug
            ])