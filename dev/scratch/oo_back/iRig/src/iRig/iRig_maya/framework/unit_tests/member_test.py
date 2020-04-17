import json
from rig_factory.controllers.rig_controller import RigController
from rig_factory.objects.part_objects.container import ContainerGuide, Container
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.part_objects.part_group import PartGroupGuide, PartGroup
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
import rig_factory.objects as obs
obs.register_classes()


def test_members():
    controller = create_rig()
    perform_member_test(controller.root)
    controller.root = controller.toggle_state()
    perform_member_test(controller.root)


def get_subclasses(base_class):
    sub_classes = list(base_class.__subclasses__())
    for sub_class in sub_classes:
        sub_classes.extend(get_subclasses(sub_class))
    return sub_classes


def create_rig():
    controller = RigController.get_controller(mock=True)

    controller.root = controller.create_object(
        obs.ContainerGuide,
        root_name='root'
    )

    for index, class_guide in enumerate(get_subclasses(obs.PartGuide)):
        class_name = class_guide.__name__
        guide_obj = controller.root.create_part(
            class_guide,
            root_name='{0}_{1}'.format(index, class_name)
        )
        if guide_obj.toggle_class is None:
            joint_parent = controller.root
            matrix_list = []
            for ind in range(5):
                joint = controller.root.create_part(
                    obs.Joint,
                    root_name='{0}_{1}'.format(guide_obj.name, ind),
                    parent=joint_parent
                )
                matrix_list.append(joint.get_matrix())
            spine = controller.root.create_part(
                obs.BipedSpineGuide,
                root_name=guide_obj.name,
                matrix=matrix_list
            )
            guide_obj.toggle_class = spine.toggle_class

    for index, class_guide in enumerate(get_subclasses(obs.PartGroupGuide)):
        class_name = class_guide.__name__
        guide_obj = controller.root.create_part(
            class_guide,
            root_name='{0}_{1}'.format(index, class_name)
        )
        if 'Hand' in class_name:
            guide_obj.create_fingers()
        elif 'Eye' in class_name:
            guide_obj.create_eyes()
    return controller

def perform_member_test(part):
    for member in get_members(part):
        assert member.owner == part, 'The owner of "%s" should be "%s" instead it is "%s"' % (member, part, member.owner)
    if isinstance(part, BaseContainer):
        for part in part.parts:
            perform_member_test(part)


def get_ancestors(item):
    ancestors = [item]
    owner = get_owner(item)
    while owner:
        ancestors.insert(0, owner)
        owner = get_owner(owner)
    return ancestors


def get_descendants(item):
    descendants = [item]
    members = get_members(item)
    descendants.extend(members)
    for member in members:
        descendants.extend(get_descendants(member))
    return descendants


def get_members(item):
    if isinstance(item, BaseContainer):
        return item.parts
    elif isinstance(item, (Part, PartGuide)):
        return item.handles
    elif isinstance(item, (CurveHandle, GuideHandle)):
        return []
    else:
        raise Exception('The model does not support object type "%s"' % type(item))


def get_owner(item):
    if isinstance(item, (
            Part,
            PartGuide,
            CurveHandle,
            GuideHandle,
            PartGroup,
            PartGroupGuide
    )):
        return item.owner
    elif isinstance(item, (
            Container,
            ContainerGuide
    )):
        return None
    else:
        raise Exception('The model does not support object type "%s"' % type(item))
