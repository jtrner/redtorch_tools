"""
Tests if joint_count is maintained between states (toggle_state, guide/rig states)
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
                class_guide.__name__.replace('Guide', '')
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


def joint_count_report(controller, guide_joints, part_guide_joint_dict, rig_joints, part_joint_dict):
    report_str = list()

    # compare total # of joints
    test_reports = []
    if not len(guide_joints) == len(rig_joints):
        test_reports = list(['\n----- Joints mismatching report -----'])
        test_reports.append(
            'Total joint count mismatch! Guide has {0} joints, build has {1} joints.'.format(len(guide_joints),
                                                                                             len(rig_joints)))
    report_str.extend(test_reports)

    # compare total # of parts
    test_reports = []
    if not len(part_guide_joint_dict) == len(part_joint_dict):
        test_reports = list(['\n----- Parts mismatching report -----'])
        test_reports.append(
            'Total part count mismatch! Guide has {0} parts, build has {1} parts.'.format(len(part_guide_joint_dict),
                                                                                          len(part_joint_dict)))
    report_str.extend(test_reports)

    # compare # joints per part
    test_reports = list(['\n----- Joints per Part mismatching report -----'])
    for part in controller.root.get_parts():
        guide_count = len(part_guide_joint_dict['{0}_{1}'.format(part.side, part.root_name)])
        current_count = len(part_joint_dict['{0}_{1}'.format(part.side, part.root_name)])
        if not guide_count == current_count:
            test_reports.append(
                "# of joints per part mismatch: {0}_{1}, Guide: {2}, Rig: {3}".format(part.side, part.root_name,
                                                                                      guide_count, current_count))
    if len(test_reports) > 1:
        report_str.extend(test_reports)

    if not report_str == []:
        raise Exception('\n'.join(report_str))


# py test
def test_joint_count():
    controller = create_rig()
    guide_joints = controller.root.get_joints()
    part_guide_joint_count = {}
    for part in controller.root.get_parts():
        part_guide_joint_count['{0}_{1}'.format(part.side, part.root_name)] = list(part.get_joints())

    controller.toggle_state()
    rig_joints = controller.root.get_joints()
    part_joint_count = {}
    for part in controller.root.get_parts():
        part_joint_count['{0}_{1}'.format(part.side, part.root_name)] = list(part.get_joints())

    joint_count_report(controller, guide_joints, part_guide_joint_count, rig_joints, part_joint_count)

    controller.toggle_state()
    guide_joints = controller.root.get_joints()
    part_guide_joint_count = {}
    for part in controller.root.get_parts():
        part_guide_joint_count['{0}_{1}'.format(part.side, part.root_name)] = list(part.get_joints())

    joint_count_report(controller, guide_joints, part_guide_joint_count, rig_joints, part_joint_count)

    controller.toggle_state()
    rig_joints = controller.root.get_joints()
    part_joint_count = {}
    for part in controller.root.get_parts():
        part_joint_count['{0}_{1}'.format(part.side, part.root_name)] = list(part.get_joints())
    joint_count_report(controller, guide_joints, part_guide_joint_count, rig_joints, part_joint_count)


# Unit test
if __name__ == '__main__':
    test_controller = create_rig()
    test_guide_joints = test_controller.root.get_joints()
    test_part_guide_joint_count = {}
    for test_part in test_controller.root.get_parts():
        test_part_guide_joint_count['{0}_{1}'.format(test_part.side,
                                                     test_part.root_name)] = list(test_part.get_joints())

    test_controller.toggle_state()
    test_rig_joints = test_controller.root.get_joints()
    test_part_joint_count = {}
    for test_part in test_controller.root.get_parts():
        test_part_joint_count['{0}_{1}'.format(test_part.side, test_part.root_name)] = list(test_part.get_joints())

    joint_count_report(test_controller, test_guide_joints, test_part_guide_joint_count, test_rig_joints,
                       test_part_joint_count)

    test_controller.toggle_state()
    test_guide_joints = test_controller.root.get_joints()
    test_part_guide_joint_count = {}
    for test_part in test_controller.root.get_parts():
        test_part_guide_joint_count['{0}_{1}'.format(test_part.side,
                                                     test_part.root_name)] = list(test_part.get_joints())

    joint_count_report(test_controller, test_guide_joints, test_part_guide_joint_count, test_rig_joints,
                       test_part_joint_count)

    test_controller.toggle_state()
    test_rig_joints = test_controller.root.get_joints()
    test_part_joint_count = {}
    for test_part in test_controller.root.get_parts():
        test_part_joint_count['{0}_{1}'.format(test_part.side,
                                               test_part.root_name)] = list(test_part.get_joints())

    joint_count_report(test_controller, test_guide_joints, test_part_guide_joint_count, test_rig_joints,
                       test_part_joint_count)

