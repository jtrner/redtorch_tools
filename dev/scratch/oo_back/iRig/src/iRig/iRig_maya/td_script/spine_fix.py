from maya import cmds
import time


def get_ik_spline_solver():
    """
    Finds the ik spline solver.
    :returns: <str> ik effector node for a spline spine. <False> for failure.
    """
    for ik_effector_node in cmds.ls(type='ikEffector'):
        handle_node = cmds.listConnections(ik_effector_node + '.handlePath[0]', d=1, s=0, type='ikHandle')
        if not handle_node:
            continue
        handle_node = handle_node[0]
        ik_solver_node = cmds.listConnections(handle_node + '.ikSolver', s=1, d=0)
        start_joint_name = cmds.listConnections(handle_node + '.startJoint', s=1, d=0)
        if not start_joint_name:
            return False
        if not 'spine' in start_joint_name[0].lower():
            continue
        if cmds.objectType(ik_solver_node) == 'ikSplineSolver':
            return handle_node
    return False



def do_it():
    """
    Sets the ik spline solver attributes to fix the problem.
    :returns: <bool> True for success. <bool> False for failure.
    """
    start_time = time.time()
    world_base_object = 'C_Spine_Hips_Ctrl'
    world_up_object = 'C_Spine_Chest_Gimbal_Ctrl'
    ik_spline_solver = get_ik_spline_solver()
    if not ik_spline_solver:
        return False

    # set the splite spine attribute settings
    cmds.setAttr(ik_spline_solver + '.dTwistControlEnable', 1)
    cmds.setAttr(ik_spline_solver + '.dWorldUpType', 4)
    cmds.setAttr(ik_spline_solver + '.dWorldUpAxis', 4)
    cmds.setAttr(ik_spline_solver + '.dForwardAxis', 2)

    # set up vectors
    cmds.setAttr(ik_spline_solver + '.dWorldUpVectorX', 1)
    cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndX', 1)
    cmds.setAttr(ik_spline_solver + '.dWorldUpVectorY', 0)
    cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndY', 0)
    cmds.setAttr(ik_spline_solver + '.dWorldUpVectorZ', 0)
    cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndZ', 0)

    # set world up string attrs
    cmds.connectAttr(world_base_object + '.worldMatrix[0]', ik_spline_solver + '.dWorldUpMatrix', f=1)
    cmds.connectAttr(world_up_object + '.worldMatrix[0]', ik_spline_solver + '.dWorldUpMatrixEnd', f=1)

    # set up the twist value type
    cmds.setAttr(ik_spline_solver + '.dTwistValueType', 1)
    end_time = time.time()
    seconds = (end_time - start_time) % 60
    print("[Ik Spline Spine] :: {} settings set in {} seconds.".format(ik_spline_solver, seconds))
    return True