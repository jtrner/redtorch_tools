import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya_tools.utilities.selection_utilities as stl

curve_functions = oma.MFnAnimCurve

infinity_types = {
    'constant': oma.MFnAnimCurve.kConstant,
    'linear': oma.MFnAnimCurve.kLinear,
    'cycle': oma.MFnAnimCurve.kCycle,
    'cycle_relative': oma.MFnAnimCurve.kCycleRelative,
    'oscilate': oma.MFnAnimCurve.kOscillate,

}

tangents = {
    'auto': curve_functions.kTangentAuto,
    'clamped': curve_functions.kTangentClamped,
    'fast': curve_functions.kTangentFast,
    'fixed': curve_functions.kTangentFixed,
    'flat': curve_functions.kTangentFlat,
    'global': curve_functions.kTangentGlobal,
    'linear': curve_functions.kTangentLinear,
    'plateau': curve_functions.kTangentPlateau,
    'slow': curve_functions.kTangentSlow,
    'smooth': curve_functions.kTangentSmooth,
    'step': curve_functions.kTangentStep,
    'step_next': curve_functions.kTangentStepNext,
}


def create_animation_curve(m_plug, **kwargs):
    curve_functions = oma.MFnAnimCurve()
    curve_type = curve_functions.unitlessAnimCurveTypeForPlug(m_plug)
    m_object = curve_functions.create(
        m_plug,
        curve_type
    )
    animation_curve = oma.MFnAnimCurve(m_object)
    animation_curve.setPostInfinityType(
        infinity_types[
            kwargs.get(
                'post_infinity_type',
                'linear'
            )
        ]
    )
    animation_curve.setPreInfinityType(
        infinity_types[
            kwargs.get(
                'pre_infinity_type',
                'linear'
            )
        ]
    )
    if 'name' in kwargs:
        mc.rename(
            get_selection_string(m_object),
            kwargs['name']
        )

    return m_object

def add_keyframe(animation_curve, in_value, out_value, in_targent='linear', out_tangent='linear'):
    animation_curve = oma.MFnAnimCurve(animation_curve)
    animation_curve.addKey(
        in_value,
        out_value,
        tangents[in_targent],
        tangents[out_tangent]
    )


def delete_keyframe(animation_curve, in_value):
    """

    This is super slow.. use cmds
    :param animation_curve:
    :param in_value:
    :return:
    """
    animation_curve_functions = oma.MFnAnimCurve(animation_curve)
    index = animation_curve_functions.findClosest(in_value)
    if index is not None:
        animation_curve_functions.remove(index)
    else:
        print 'Warning, "%s" had no keyframe with a driver value of "%s". Cannot delete.' % (
            stl.get_selection_string(animation_curve),
            in_value
        )

def change_keyframe(animation_curve, current_in_value, **kwargs):
    in_value = kwargs.get('in_value', None)
    out_value = kwargs.get('out_value', None)
    in_tangent = kwargs.get('in_tangent', None)
    out_tangent = kwargs.get('out_tangent', None)
    anim_curve_functions = oma.MFnAnimCurve(animation_curve)
    index_utility = om.MScriptUtil()
    index_utility.createFromInt(0)
    index_pointer = index_utility.asUintPtr()
    anim_curve_functions.find(current_in_value, index_pointer)
    index = om.MScriptUtil.getUint(index_pointer)
    if index is not None:
        if out_value is not None:
            anim_curve_functions.setValue(
                index,
                out_value
            )
        if in_tangent is not None:
            anim_curve_functions.setInTangentType(
                index,
                tangents[in_tangent]
            )
        if out_tangent is not None:
            anim_curve_functions.setOutTangentType(
                index,
                tangents[out_tangent]
            )
        if in_value is not None:
            if current_in_value != in_value:
                anim_curve_functions.setUnitlessInput(
                    index,
                    in_value
                )
    else:
        raise Exception('Unable to find keyframe index for "%s" at value %s' % (
            stl.get_selection_string(animation_curve),
            current_in_value))


def get_value_at_index(curve, index):
    return oma.MFnAnimCurve(curve).value(index)


def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]


