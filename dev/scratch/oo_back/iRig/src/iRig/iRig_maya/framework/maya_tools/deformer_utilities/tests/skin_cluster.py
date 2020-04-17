import pprint
import maya.standalone
import maya.cmds as mc
import maya_tools.deformer_utilities.skin_cluster as skn
import json
maya.standalone.initialize(name='python')

cube_mesh_1 = mc.listRelatives(
    mc.polyCube(ch=False, sx=1, sy=1, sz=1)[0],
    c=True,
    type='mesh'

)

joint_1 = mc.createNode('joint')
joint_2 = mc.createNode('joint')
joint_3 = mc.createNode('joint')
joint_4 = mc.createNode('joint')
joint_5 = mc.createNode('joint')
joint_6 = mc.createNode('joint')
joint_7 = mc.createNode('joint')

skin_cluster_name = mc.skinCluster(
    [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6, joint_7],
    cube_mesh_1,
    tsb=True
)[0]

mesh = skn.get_mesh(skin_cluster_name)
influences = skn.get_influences(skin_cluster_name)
components = skn.get_components(skin_cluster_name)
weights = skn.get_weights(skin_cluster_name)
skn.set_weights(skin_cluster_name, weights)
with open('G:/Rigging/Paxton/data.json', mode='w') as f:
    f.write(
        json.dumps(
            weights,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    )
