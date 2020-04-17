import maya.cmds as mc
import maya_tools.utilities.mesh_utilities as mut


def get_selected_face_indices():
    indices = []
    for x in mc.ls(sl=True, fl=True):
        if 'f[' not in x:
            raise Exception('Select only Faces !!')
        indices.append(int(x.split('[')[-1].split(']')[0]))
    return indices


def cut_head(mesh=None, face_indices=None):
    if not mesh:
        mesh_objects = mut.get_selected_mesh_names()
        if len(mesh_objects) != 1:
            raise Exception('Select only ONE mesh !!')
        mesh = mc.listRelatives(mesh_objects[0], p=True)[0]
    if face_indices is None:
            face_indices = get_selected_face_indices()
    head_mesh = mc.duplicate(mesh, name='head_mesh')[0]
    body_mesh = mc.duplicate(mesh, name='body_mesh')[0]
    mc.select(['%s.f[%s]' % (body_mesh, x) for x in face_indices])
    mc.delete()
    mc.select(mc.ls('%s.f[*]' % head_mesh))
    mc.select(['%s.f[%s]' % (head_mesh, x) for x in face_indices], d=True)
    mc.delete()
    head_2_mesh = mc.duplicate(head_mesh, name='head_2_mesh')[0]
    combined_mesh = mc.polyUnite(
        head_2_mesh,
        body_mesh,
        ch=False,
        mergeUVSets=True,
        centerPivot=False,
        name='combined_mesh'
    )[0]
    try:
        mc.parent(head_mesh, w=True)
    except Exception, e:
        print e.message
    mc.polyMergeVertex(combined_mesh, d=0.0001, am=1, ch=0)
