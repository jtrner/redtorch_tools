import maya.cmds as mc
import sys;

sys.path.insert(0, 'D:/rigging_library/')
from rig_factory.controllers.rig_controller import RigController

import json
controller = RigController.get_controller()
file_name = '.json'
with open(file_name, mode='r') as f:
    controller.root = controller.build_blueprint(json.loads(f.read()))

def plug_walk(plug):
    if plug.m_plug.isArray():
        for e in range(plug.m_plug.numElements()):
            element_plug = plug.element(e)
            yield element_plug
            for x in plug_walk(element_plug):
                yield x
    if plug.m_plug.isCompound():
        for c in range(plug.m_plug.numChildren()):
            child_plug = plug.child(c)
            yield child_plug
            for x in plug_walk(child_plug):
                yield x

controller.initialize_node('<SOME-NODE-NAME>')

def node_plug_walk(node):
    node = controller.initialize_node(node)
    for attribute in mc.listAttr(node.get_selection_string()):
        if '.' not in attribute:
            yield node.plugs[attribute]
            if mc.attributeQuery(attribute, node=node.get_selection_string(), lc=True):
                for plug in plug_walk(node.plugs[attribute]):
                    yield plug


node_1 = mc.createNode('multiplyDivide')
node_2 = mc.createNode('AISEnvFacade')

