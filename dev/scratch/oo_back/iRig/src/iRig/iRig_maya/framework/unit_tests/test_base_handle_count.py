"""
Test if a part's joint_chain property is False and checks if the joint is parented to another joint
according to it's hierarchy
"""
from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs
import rig_factory.utilities.object_utilities.name_utilities as ntl

obs.register_classes()

index_dictionary = ntl.create_alpha_dictionary()


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
    subclasses = get_subclasses(obs.PartGuide)
    for c, class_guide in enumerate(subclasses):

        root_name = '{0}_{1}'.format(
                index_dictionary[c],
                class_guide.__name__
            )
        guide_obj = controller.root.create_part(
            class_guide,
            root_name=root_name

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
        controller.root.create_part(
            class_guide,
            root_name='{0}_{1}'.format(
                index_dictionary[index],
                class_guide.__name__.replace('Guide', '')
            )
        )

    return controller


def base_handle_report(controller):
    report_str = list(['\n----- Invalid base handle report -----'])
    for part in controller.root.get_parts():
        if isinstance(part, obs.PartGuide):
            if len(part.joints) != 1 and len(part.joints) != len(part.base_handles):
                report_str.append(
                    'Invalid Base Handle Count! %s has %s joints and %s base handles. (They should match)' % (
                            part.__class__.__name__,
                            len(part.joints),
                            len(part.base_handles)
                    )
                )

    if len(report_str) > 1:
        raise Exception('\n'.join(report_str))


# py test
def test_joint_count():
    controller = create_rig()
    base_handle_report(controller)


# Unit test
if __name__ == '__main__':
    test_controller = create_rig()
    base_handle_report(test_controller)
