import rig_factory
from base_container import BaseContainer
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
from rig_factory.objects.node_objects.joint import Joint


class PartGroupGuide(BaseContainer):

    rig_data = DataProperty(
        name='rig_data',
    )

    default_settings = dict(
        root_name='group',
        side='center'
    )

    base_handles = ObjectListProperty(
        name='base_handles'
    )

    def __init__(self, **kwargs):
        super(PartGroupGuide, self).__init__(**kwargs)
        self.toggle_class = PartGroup.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        return super(PartGroupGuide, cls).create(controller, **kwargs)

    def reset_parent_joint(self):
        parent_joint = self.parent_joint
        if parent_joint:
            self.controller.start_unparent_joint_signal.emit(self)
            parent_joint.child_parts.remove(self)
            self.parent_joint = None
            self.controller.finish_unparent_joint_signal.emit(self)
            
    def set_parent_joint(self, joint):
        if not isinstance(joint, Joint)and joint is not None:
            raise Exception(
                'To set_parent_joint, you must provide type Joint or type(None), not %s' % joint.__class__.__name__
            )
        if self.parent_joint and self.parent_joint in self.parent_joint.child_parts:
            self.parent_joint.child_parts.remove(self.parent_joint)
        self.parent_joint = joint
        joint.child_parts.append(self)
        for part in self.parts:
            part.set_parent_joint(joint)

    def create_handle(self, **kwargs):
        return self.controller.create_guide_handle(self, **kwargs)

    def create_part(self, object_type, **kwargs):
        kwargs['parent'] = self
        return super(PartGroupGuide, self).create_part(object_type, **kwargs)

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            base_type=PartGroupGuide.__name__  # needed by blueprint view
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = dict(
            klass=self.toggle_class,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index
        )
        if self.rig_data:
            blueprint.update(self.rig_data)
        blueprint['guide_blueprint'] = self.get_blueprint()
        return blueprint

    def get_mirror_blueprint(self):
        """
        It would be great to just share this function with PartGuide somehow (they are identical)
        :return:
        """
        sides = dict(right='left', left='right')
        if self.side not in sides:
            raise Exception('Cannot mirror "%s" invalid side "%s"' % (self, self.side))
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=sides[self.side],
            size=self.size,
            index=self.index
        )
        blueprint['disconnected_joints'] = self.disconnected_joints
        mirrored_handle_positions = dict()
        for handle in self.handles:
            search_prefix = rig_factory.settings_data['side_prefixes'][handle.side]
            replace_prefix = rig_factory.settings_data['side_prefixes'][sides[handle.side]]
            position = list(handle.get_translation())
            position[0] = position[0] * -1.0
            mirrored_handle_positions[handle.name.replace(search_prefix, replace_prefix)] = position
        blueprint['handle_positions'] = mirrored_handle_positions
        return blueprint

    def set_owner(self, owner):
        self.controller.set_owner(self, owner)

    def set_root_name(self, root_name):
        self.controller.named_objects.pop(self.name)
        self.root_name = root_name
        self.name = self.controller.name_function(
            self.__class__.__name__,
            root_name=self.root_name,
            side=self.side,
            index=self.index
        )
        self.controller.named_objects[self.name] = self


class PartGroup(BaseContainer):

    guide_blueprint = DataProperty(
        name='guide_blueprint'
    )

    deform_joints = ObjectListProperty(
        name='deform_joints'
    )

    base_deform_joints = ObjectListProperty(
        name='base_deform_joints'
    )

    secondary_handles = ObjectListProperty(
        name='secondary_handles'
    )
    disconnected_joints = DataProperty(
        name='disconnected_joints',
        default_value=True
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(PartGroup, cls).create(controller, **kwargs)
        return this

    def __init__(self, **kwargs):
        super(PartGroup, self).__init__(**kwargs)
        self.toggle_class = PartGroupGuide.__name__

    def create_handle(self, **kwargs):
        return self.controller.create_standard_handle(self, **kwargs)

    def create_part(self, object_type, **kwargs):
        kwargs['parent'] = self
        return super(PartGroup, self).create_part(object_type, **kwargs)


    def set_parent_joint(self, joint):
        if not isinstance(joint, Joint):
            raise Exception(
                'To set_parent_joint, you must provide type Joint, not %s' % joint.__class__.__name__
            )
        #if not isinstance(self.parent, BaseContainer):
        #    self.set_parent(joint)
        self.controller.create_parent_constraint(
            joint,
            self,
            mo=True
        )
        self.controller.create_scale_constraint(
            joint,
            self
        )
        self.parent_joint = joint

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            guide_blueprint=self.guide_blueprint
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = self.guide_blueprint
        return blueprint

