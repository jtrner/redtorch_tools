import math
import maya.cmds as mc
import maya.OpenMaya as om


def initialize_plug(owner, key):
    if isinstance(owner, om.MPlug):
        if owner.isArray():
            return owner.elementByLogicalIndex(key)
        if owner.isCompound():
            return owner.child(key)
        else:
            raise Exception('invalid plug owner type: "%s"' % type(owner))

    elif isinstance(owner, om.MObject):
        try:
            node_functions = om.MFnDependencyNode(owner)
            m_attribute = node_functions.attribute(key)
            return node_functions.findPlug(m_attribute, False)
        except Exception, e:
            print e.message
            raise Exception('Failed to initialize plug: %s.%s' % (
                get_selection_string(owner),
                key
            ))

    else:
        raise Exception('invalid plug owner type: "%s"' % type(owner))


def create_plug(owner, key, **kwargs):
    mc.addAttr(
        get_selection_string(owner),
        ln=key,
        **kwargs
    )
    return initialize_plug(owner, key)


def get_next_avaliable_plug_index(plug):
    if not plug.isArray():
        raise TypeError('Plug is not an array')
    current_index = 0
    while True:
        element_plug = plug.elementByLogicalIndex(current_index)
        connected_plugs = om.MPlugArray()
        is_connected = element_plug.connectedTo(connected_plugs, True, False)
        if not is_connected:
            return current_index
        current_index += 1


def set_plug_value(plug, value):
    if not isinstance(plug, om.MPlug):
        raise Exception('Plug is not type "MPlug"')
    if plug.isCompound():
        for i in range(plug.numChildren()):
            set_plug_value(plug.child(i), value[i])
    elif plug.isArray():
        for i in range(plug.numElements()):
            set_plug_value(plug.elementByPhysicalIndex(i), value[i])
    else:
        attribute = plug.attribute()
        if attribute.hasFn(om.MFn.kNumericAttribute):
            attribute_type = om.MFnNumericAttribute(attribute).unitType()
            if attribute_type in [om.MFnNumericData.kBoolean]:
                plug.setBool(value)
            elif attribute_type == om.MFnNumericData.kChar:
                plug.setChar(value)
            elif attribute_type == om.MFnNumericData.kShort:
                plug.setShort(value)
            elif attribute_type in (
                    om.MFnNumericData.kInt,
                    om.MFnNumericData.kLong,
                    om.MFnNumericData.kByte
            ):
                plug.setInt(value)
            elif attribute_type == om.MFnNumericData.kFloat:
                plug.setFloat(value)
            elif attribute_type == om.MFnNumericData.kDouble:
                plug.setDouble(value)
            else:
                #print 'Plug type not supported "%s"' % attribute_type
                plug.setInt(value)
        elif attribute.hasFn(om.MFn.kUnitAttribute):
            unit_type = om.MFnUnitAttribute(attribute).unitType()
            if unit_type == om.MFnUnitAttribute.kAngle:
                plug.setMAngle(om.MAngle(math.radians(value)))
            elif unit_type == om.MFnUnitAttribute.kDistance:
                plug.setMDistance(om.MDistance(value))
            elif unit_type == om.MFnUnitAttribute.kTime:
                plug.setMTime(om.MTime(value))
        elif attribute.hasFn(om.MFn.kTypedAttribute):
            attr_type = om.MFnTypedAttribute(attribute).attrType()
            if attr_type == om.MFnData.kString:
                plug.setString(value)
        elif attribute.hasFn(om.MFn.kMatrixAttribute):
            m = value
            matrix = om.MMatrix()
            om.MScriptUtil.setDoubleArray(matrix[0], 0, value[0])
            om.MScriptUtil.setDoubleArray(matrix[0], 1, value[1])
            om.MScriptUtil.setDoubleArray(matrix[0], 2, value[2])
            om.MScriptUtil.setDoubleArray(matrix[0], 3, value[3])
            om.MScriptUtil.setDoubleArray(matrix[1], 0, value[4])
            om.MScriptUtil.setDoubleArray(matrix[1], 1, value[5])
            om.MScriptUtil.setDoubleArray(matrix[1], 2, value[6])
            om.MScriptUtil.setDoubleArray(matrix[1], 3, value[7])
            om.MScriptUtil.setDoubleArray(matrix[2], 0, value[8])
            om.MScriptUtil.setDoubleArray(matrix[2], 1, value[9])
            om.MScriptUtil.setDoubleArray(matrix[2], 2, value[10])
            om.MScriptUtil.setDoubleArray(matrix[2], 3, value[11])
            om.MScriptUtil.setDoubleArray(matrix[3], 0, value[12])
            om.MScriptUtil.setDoubleArray(matrix[3], 1, value[13])
            om.MScriptUtil.setDoubleArray(matrix[3], 2, value[14])
            om.MScriptUtil.setDoubleArray(matrix[3], 3, value[15])
            m_object = om.MFnMatrixData().create(matrix)
            plug.setMObject(m_object)

        else:
            #print 'Plug type not supported print setting %s to %s' % (plug, value)

            plug.setFloat(value)


def get_plug_value(plug):
    if not isinstance(plug, om.MPlug):
        raise Exception('Plug is not type "MPlug"')
    m_plug = plug
    if m_plug.isCompound():
        plugs = []
        for i in range(m_plug.numChildren()):
            plugs.append(m_plug.child(i))
        return [get_plug_value(x) for x in plugs]
    if m_plug.isArray():
        plugs = []
        for i in range(m_plug.numElements()):
            plugs.append(m_plug.elementByPhysicalIndex(i))
        return [get_plug_value(x) for x in plugs]
    attribute = m_plug.attribute()
    if attribute.hasFn(om.MFn.kNumericAttribute):
        attribute_type = om.MFnNumericAttribute(attribute).unitType()
        if attribute_type in [om.MFnNumericData.kBoolean]:
            return m_plug.asBool()
        elif attribute_type == om.MFnNumericData.kChar:
            return m_plug.asChar()
        elif attribute_type == om.MFnNumericData.kShort:
            return m_plug.asShort()
        elif attribute_type in (
                om.MFnNumericData.kInt,
                om.MFnNumericData.kLong,
                om.MFnNumericData.kByte
        ):
            return m_plug.asInt()
        elif attribute_type == om.MFnNumericData.kFloat:
            return m_plug.asFloat()
        elif attribute_type == om.MFnNumericData.kDouble:
            return m_plug.asDouble()
        else:
            return m_plug.asFloat()
            #print 'Plug type not supported', attribute_type
    elif attribute.hasFn(om.MFn.kUnitAttribute):
        unit_type = om.MFnUnitAttribute(attribute).unitType()
        if unit_type == om.MFnUnitAttribute.kAngle:
            return math.degrees(m_plug.asMAngle().value())
        elif unit_type == om.MFnUnitAttribute.kDistance:
            return m_plug.asMDistance().value()
        elif unit_type == om.MFnUnitAttribute.kTime:
            return m_plug.asMTime().value()
        else:
            return m_plug.asFloat()
            #print 'Plug type "%s" not supported' % unit_type

    elif attribute.hasFn(om.MFn.kTypedAttribute):
        attr_type = om.MFnTypedAttribute(attribute).attrType()
        if attr_type == om.MFnData.kString:
            return m_plug.asString()
        if attr_type == om.MFnData.kMatrix:
            matrix_data = om.MFnMatrixData(m_plug.asMObject())
            m = matrix_data.matrix()
            return [
                m(0, 0), m(0, 1), m(0, 2), m(0, 3),
                m(1, 0), m(1, 1), m(1, 2), m(1, 3),
                m(2, 0), m(2, 1), m(2, 2), m(2, 3),
                m(3, 0), m(3, 1), m(3, 2), m(3, 3)
            ]
            return values

        else:
            raise Exception('Plug type "%s" not supported' % attr_type)

    elif attribute.hasFn(om.MFn.kMatrixAttribute):
        matrix_data = om.MFnMatrixData(m_plug.asMObject())
        m = matrix_data.matrix()
        return [
            m(0, 0), m(0, 1), m(0, 2), m(0, 3),
            m(1, 0), m(1, 1), m(1, 2), m(1, 3),
            m(2, 0), m(2, 1), m(2, 2), m(2, 3),
            m(3, 0), m(3, 1), m(3, 2), m(3, 3)
        ]

    else:
        #print 'Plug type not supported "%s"' % plug
        return mc.getAttr(get_selection_string(plug))

def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]