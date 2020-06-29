# ======================================================================================
# create curve
import maya.api.OpenMaya as om2

points = [
    (0, 0, 0),
    (1, 1, 0),
    (2, 0, 0),
    (3, 1, 0),
    (4, 0, 0)
]
degree = 1
spans_len = len(points) - degree
knots_len = spans_len + 2 * degree - 1
knots = range(knots_len)

cvs = om2.MPointArray(points)
crv_fn = om2.MFnNurbsCurve()

crv_fn.create(cvs, knots, degree, crv_fn.kOpen, True, True)

# ======================================================================================
# create matrix attribute
import maya.OpenMaya as omp

matAttr = om.MFnMatrixAttribute()
YOUR_NODE.matrix = matAttr.create('matrix', 'matrix', 1)
matAttr.default = om.MMatrix()
matAttr.setStorable(True)
matAttr.setWritable(True)

# ======================================================================================
# get type of selected
import maya.api.OpenMaya as om2

sels = om2.MGlobal.getActiveSelectionList()
dep = sels.getDependNode(0)
dep_fn = om2.MFnDependencyNode(dep)
print dep_fn.typeName

# ======================================================================================
# get transforms in the given distance from selected transforms
import maya.api.OpenMaya as om2

# inputs
start = 0
end = 15

# result selection
result_sels = om2.MSelectionList()

# get selected transforms
srcs_sel = om2.MGlobal.getActiveSelectionList()
srcs_it = om2.MItSelectionList(srcs_sel, om2.MFn.kTransform)

while not srcs_it.isDone():
    src_dag = srcs_it.getDagPath()
    print 'looking for neighours of ...................', src_dag.fullPathName()

    # get world position of current selection
    src_trs = om2.MFnTransform(src_dag)
    src_vec = om2.MVector(src_trs.translation(om2.MSpace.kWorld))

    # find and go through all transforms in the scene
    trs_filter = om2.MIteratorType()
    trs_filter.filterType = om2.MFn.kTransform
    all_dag_it = om2.MItDag(trs_filter)
    dag_fn = om2.MFnDagNode()
    while not all_dag_it.isDone():
        # get world position of obj
        dag = all_dag_it.getPath()
        dag_fn.setObject(dag)
        # print dag.partialPathName(), '\t\t.....', dag_fn.typeName, '\t\t.....', dag.apiType()

        # get world position of obj
        tgt_trs = om2.MFnTransform(dag)
        tgt_vec = om2.MVector(tgt_trs.translation(om2.MSpace.kWorld))

        # get distance from current selection to this transform
        dist = (tgt_vec - src_vec).length()
        if dist <= end and dist >= start:
            result_sels.add(dag)

        #
        all_dag_it.next()

    #
    srcs_it.next()

om2.MGlobal.setActiveSelectionList(result_sels)

# ======================================================================================
# add float attribute
import maya.api.OpenMaya as om2
import maya.cmds as mc

cube = mc.polyCube()[0]
attrName = 'aaa'

src_sel = om2.MSelectionList()
src_sel.add(cube)
sel_dep = src_sel.getDependNode(0)

dep_fn = om2.MFnDependencyNode(sel_dep)

num_afn = om2.MFnNumericAttribute()
aaa_af = num_afn.create(attrName, attrName, om2.MFnNumericData.kFloat)
num_afn.keyable = True

dep_fn.addAttribute(aaa_af)

mc.setAttr(cube + '.' + attrName, 0.15)
print mc.getAttr(cube + '.' + attrName)

# ======================================================================================
# access attribute
import maya.api.OpenMaya as om2
import maya.cmds as mc

node = 'pCube1'
attrName = 'tx'
attrName2 = 'ty'

# get depend node
src_sel = om2.MSelectionList()
src_sel.add(node)
sel_dep = src_sel.getDependNode(0)

dep_fn = om2.MFnDependencyNode(sel_dep)

# find plug value and test some plug functions
plug = dep_fn.findPlug(attrName, False)
print plug.asBool()
print plug.getSetAttrCmds()
print plug.isDefaultValue()
print plug.name()

plug.isKeyable = False

if plug.isChild:
    print plug.parent()
if plug.isCompound:
    for i in range(plug.numChildren()):
        print plug.child(i).name()

# get attribute and test attribute functions
plug2 = dep_fn.findPlug(attrName2, False)
plug2.setFloat(plug.asFloat())

attr = dep_fn.attribute(attrName)
num_at_fn = om2.MFnNumericAttribute(attr)

print num_at_fn.keyable
print num_at_fn.dynamic
print num_at_fn.getAddAttrCmd(True)

# ======================================================================================
# add color attribute
import maya.api.OpenMaya as om2
import maya.cmds as mc

node = 'pCube1'
attrName = 'testColor'

# get depend node
src_sel = om2.MSelectionList()
src_sel.add(node)
sel_dep = src_sel.getDependNode(0)
dep_fn = om2.MFnDependencyNode(sel_dep)

# find attribute and addAttr command
num_at_fn = om2.MFnNumericAttribute(attr)
attr = num_at_fn.createColor(attrName, attrName)
dep_fn.addAttribute(attr)

# ======================================================================================
# getClosestPointsFromTwoPointArrays
import scipy

tree = scipy.spatial.ckdtree.cKDTree(srcPnts)
distance, pnts = tree.query(tgtPnts)

# ======================================================================================
# array attributes
import maya.api.OpenMaya as om2
import maya.cmds as mc

node = 'pCube1'
at = 'u'

# get depend node
src_sel = om2.MSelectionList()
src_sel.add(node)
sel_dep = src_sel.getDependNode(0)
dep_fn = om2.MFnDependencyNode(sel_dep)

# addAttr
num_at_fn = om2.MFnNumericAttribute(sel_dep)
u_ar_at = num_at_fn.create(at, at, om2.MFnNumericData.kFloat)
num_at_fn.array = True
num_at_fn.keyable = True
dep_fn.addAttribute(u_ar_at)

# array of floats
plug = dep_fn.findPlug(at, False)

for i in range(4):
    p = plug.elementByLogicalIndex(i)
    p.setFloat(i)

last_plug = plug.elementByPhysicalIndex(plug.numElements() - 1)
numLogicalElements = last_plug.logicalIndex() + 1
for i in range(numLogicalElements):
    pl = plug.elementByLogicalIndex(i)
    pl.setFloat(i)

# color
col_at = num_at_fn.createColor('col', 'col')
dep_fn.addAttribute(col_at)

col_plug = dep_fn.findPlug(col_at, False)
r_p = col_plug.child(0)
g_p = col_plug.child(1)
b_p = col_plug.child(2)

# enum
en_at_fn = om2.MFnEnumAttribute(sel_dep)
en_at = en_at_fn.create(at, at, 1)
en_at_fn.keyable = True
en_at_fn.hidden = False
en_at_fn.addField('aaaa', 0)
en_at_fn.addField('bbbbb', 1)
dep_fn.addAttribute(en_at)

# matrix
atFn = om2.MFnMatrixAttribute(sel_dep)
en_at = atFn.create(at, at, 1)
atFn.keyable = True
atFn.hidden = False
atFn.default = om2.MMatrix([0, 0, 0, 0,
                            0, 0, 0, 0,
                            0, 0, 0, 0,
                            0, 0, 0, 0])
dep_fn.addAttribute(en_at)

# get matrix value
plug = dep_fn.findPlug(at, 0)
matFn = om2.MFnMatrixData(plug.asMObject())
matFn.matrix()

# set matrix value
plug = dep_fn.findPlug(at, 0)
matFn = om2.MFnMatrixData()
mat_obj = matFn.create(mat_iden)
plug.setMObject(mat_obj)

# get first matrix value of a matrix array
plug = dep_fn.findPlug(at, 0)
plug0 = plug.elementByLogicalIndex(0)
matFn = om2.MFnMatrixData(plug0.asMObject())
matFn.matrix()

# ======================================================================================
# connect deformer weights to blendShape weights
mc.getAttr('ehm_pushDeformer1.weightList[0].weights')
mc.getAttr('blendShape1.inputTarget[0].paintTargetWeights')

mc.connectAttr('ehm_pushDeformer1.weightList[0].weights', 'blendShape1.inputTarget[0].paintTargetWeights', f=True)

# ======================================================================================
# deformer weightList to doubleArray
import maya.api.OpenMaya as om2

sel = om2.MSelectionList()
sel.add('ehm_pushDeformer1')
dep = sel.getDependNode(0)

depFn = om2.MFnDependencyNode(dep)
attrObj = depFn.attribute('weightList')
plug = om2.MPlug(dep, attrObj)
plugE = plug.elementByLogicalIndex(0)
childPlug = plugE.child(0)


existingIds = childPlug.getExistingArrayAttributeIndices()

# get number of verts of output geometry
plug = depFn.findPlug('outputGeometry', 0)
index = plug.getExistingArrayAttributeIndices()
if index:
    plugE = plug.elementByLogicalIndex(index[0])
    dests = plugE.destinations()
    if dests:
        meshFn = om2.MFnMesh(dests[0].node())
        pnts = om2.MFloatArray()
        for i in range(meshFn.numVertices):
            if i in existingIds:
                pnt = childPlug.elementByLogicalIndex(i).asDouble()
                pnts.append(pnt)
            else:
                pnts.append(0.0)

# create doubleArray from found floats
daAttr = om2.MFnDoubleArrayData()
wgtAr = daAttr.create(pnts)
print daAttr.array()
