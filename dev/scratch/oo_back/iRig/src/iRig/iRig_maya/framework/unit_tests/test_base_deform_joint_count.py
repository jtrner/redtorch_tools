"""
Tests if joint_count is maintained between states (toggle_state, guide/rig states)
"""
from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs
import rig_factory.utilities.object_utilities.name_utilities as ntl
import json
obs.register_classes()

index_dictionary = ntl.create_alpha_dictionary()


controller = RigController.get_controller(mock=True)

with open('Y:/AWB/assets/type/Character/Alice/work/rig/Maya/willw/rig_blueprint/Alice_rig_blueprint_v0000.0137.json', mode='r') as f:
    controller.root = controller.build_blueprint(json.loads(f.read()))
controller.root = controller.toggle_state()
self = controller.root
base_deform_joints = self.get_base_deform_joints()
joints = self.get_joints()

print len(base_deform_joints)
print len(joints)

for x in range(len(joints)):
	print joints[x], '-------->>', base_deform_joints[x]