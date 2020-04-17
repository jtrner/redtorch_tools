import os
import maya.cmds as mc


def transform_walk(transform):
    yield transform
    children = mc.listRelatives(transform, c=True)
    if children:
        for x in children:
            if mc.nodeType(x) in ['transform', 'joint']:
                for y in transform_walk(x):
                    yield y



def recycle_scene():
    all_roots = [str(x) for x in mc.ls(assemblies=True)]
    roots = [x for x in all_roots if x not in ['persp', 'top', 'front', 'side']]

    if len(roots) != 1:
        raise Exception('There must be exactly one root')
    root = roots[0]

    def create_node_code(node):
        node_type = mc.nodeType(node)
        parents = mc.listRelatives(node, p=True)
        t1 = '\n    '
        if parents:
            parent_node = parents[0]
        else:
            parent_node = root
        class_string = class_strings.get(node_type, 'nob.DependencyNode')
        return "%s = controller.create_object(%s%s, %sroot_name='%s', %sparent=%s\n)\n" % (
            node, t1, class_string, t1, node, t1, parent_node)


    exclude = ['lightLinker1',
               'shapeEditorManager',
               'poseInterpolatorManager',
               'layerManager',
               'defaultLayer',
               'renderLayerManager',
               'defaultRenderLayer',
               'ikSCsolver',
               'ikRPsolver',
               'ikSplineSolver',
               'hikSolver',
               'persp',
               'perspShape',
               'top',
               'topShape',
               'front',
               'frontShape',
               'side',
               'sideShape',
               'MayaNodeEditorSavedTabsInfo'
               ]
    transforms = [x for x in transform_walk(roots[0])]

    persistent_nodes = mc.ls(persistentNodes=True)
    nodes = [str(x) for x in mc.ls() if x not in persistent_nodes and x != root and x not in transforms]
    nodes = [x for x in nodes if x not in exclude]

    class_strings = dict(
        joint='nob.Joint',
        transform='nob.Transform',
        mesh='nob.Mesh',
        ikHandle='nob.IKHandle',
        ikEffector='nob.IKEffector'
    )

    code_lines = ['\n# Create Heirarchy\n']
    code_lines.extend([create_node_code(x) for x in transforms])
    code_lines.append('\n# Create Nodes\n')
    code_lines.extend([create_node_code(x) for x in nodes])
    file_name = '%s/recycle_temp.py' % os.path.expanduser('~')

    with open(file_name, mode='w') as f:
        f.write('\n'.join(code_lines))
    os.system('start %s' % file_name)
