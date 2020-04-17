# define private variables
__author__ = "Alexei Gaidachev"
__vendor__ = "ICON"
__version__ = "1.0.0"

# import standard modules
import time

# import maya modules
from maya import cmds


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print '[%r Elapsed Time] :: %2.2f ms' % \
                  (method.__name__.title(), (te - ts) * 1000)
        return result
    return timed


@timeit
def check_error():
    cog_ctrl = 'COG_Ctrl'
    autoaim_grps = ['{}_BackLeg_Top_Bend_Start_Ctrl_Hip_AutoAim_Foot_Grp',
                    '{}_FrontLeg_Top_Bend_Start_Ctrl_Hip_AutoAim_Foot_Grp']
    ikfk_ls = ['L_BackFoot_IKFKSwitch_Ctrl', 'R_BackFoot_IKFKSwitch_Ctrl', 'L_FrontFoot_IKFKSwitch_Ctrl',
               'R_FrontFoot_IKFKSwitch_Ctrl']
    for ikfk in ikfk_ls:
        cmds.setAttr(ikfk + '.FKIKSwitch', 0.0)

    cmds.setAttr(cog_ctrl + '.ry', 180.0)

    for side in "LR":
        for aim_grp in autoaim_grps:
            autoaim_grp = aim_grp.format(side)
            aim_connection = cmds.getAttr(autoaim_grp + '.ry')
            if aim_connection == 180:
                print("[FK Leg Twist] :: {}, Found Error.".format(aim_grp))
            else:
                print("[FK Leg Twist] :: {}, All Good.".format(aim_grp))
    cmds.setAttr(cog_ctrl + '.ry', 0.0)
    for ikfk in ikfk_ls:
        cmds.setAttr(ikfk + '.FKIKSwitch', 1.0)
    return True


@timeit
def fix_error():
    """
    Fix the rotation issue on quadrupeds.
    """
    transforms = []
    controls = []
    if cmds.objExists("L_BackLeg_Hip_Twist_Tfm_Offset_Grp"):
        transforms.append("{}_BackLeg_Hip_Twist_Tfm_Offset_Grp")
        controls.append("{}_BackLeg_Hip_Fk_Ctrl")
    if cmds.objExists("L_FrontLeg_Hip_Twist_Tfm_Offset_Grp"):
        transforms.append("{}_FrontLeg_Hip_Twist_Tfm_Offset_Grp")
        controls.append("{}_FrontLeg_Hip_Fk_Ctrl")
    if cmds.objExists("L_Leg_Hip_Twist_Tfm_Offset_Grp"):
        transforms.append("{}_Leg_Hip_Twist_Tfm_Offset_Grp")
        controls.append("{}_Leg_Hip_Fk_Ctrl")
    if cmds.objExists("L_Arm_Shoulder_Twist_Tfm_Offset_Grp"):
        transforms.append("{}_Arm_Shoulder_Twist_Tfm_Offset_Grp")
        controls.append("{}_Arm_Shoulder_Fk_Ctrl")

    for side in "LR":
        for leg_trm, leg_ctrl in zip(transforms, controls):
            leg = leg_trm.format(side)
            leg_ctl = leg_ctrl.format(side)
            # find the constraint
            constraint = cmds.listConnections(leg + '.ry', s=1, d=0, type='parentConstraint')
            if not constraint:
                continue
            constraint = constraint[0]
            # connect a condition to the eveluator
            weight_attr = [w for w in cmds.listAttr(constraint, ud=1) if 'W0' in w][0]
            condition_name = leg_ctl.replace('_Ctrl', '_Condition')
            if not cmds.objExists(condition_name):
                cmds.createNode('condition', name=condition_name)
            cmds.setAttr(condition_name + '.operation', 2)
            cmds.setAttr(condition_name + '.secondTerm', 1.0)
            cmds.setAttr(condition_name + '.colorIfTrueR', 1.0)
            cmds.setAttr(condition_name + '.colorIfFalseR', 0.0)
            follow_attr = leg_ctl + '.Follow'
            cond_first_term_attr = condition_name + '.firstTerm'
            if not cmds.isConnected(follow_attr, cond_first_term_attr):
                cmds.connectAttr(leg_ctl + '.Follow', condition_name + '.firstTerm', f=1)
            cond_out_color_attr = condition_name + '.outColorR'
            cnst_weight_attr = constraint + '.' + weight_attr
            if not cmds.isConnected(cond_out_color_attr, cnst_weight_attr):
                cmds.connectAttr(cond_out_color_attr, cnst_weight_attr, f=1)
    return True