import json
from rig_factory.controllers.rig_controller import RigController

controller = RigController.get_controller()

rig_blueprint = 'Y:/RCL/assets/type/Character/Paxton_Sandbox/work/rig/Maya/paxtong/rig_blueprint/Paxton_Sandbox_rig_blueprint_v0000.0002.json'
face_blueprint = 'Y:/RCL/assets/type/Character/Paxton_Sandbox/work/rig/Maya/paxtong/face_blueprint/Paxton_Sandbox_face_blueprint_v0000.0003.json'

with open(rig_blueprint, mode='r') as f:
    controller.build_blueprint(json.load(f))

controller.import_face(face_blueprint)

"""
hmm 
well you could import the blueprints from here
Y:\RCL\assets\type\Character\Paxton_Sandbox\work\rig\Maya\paxtong
ill show you how with code
first.. This is a copy of that same SDK code, but with the groups working. I can explain what was going on if you like:
   https://paste.ofcode.org/8NYK92HQ8VB4nPjTNRE5Vp   
i had forgotten to set the scene root. which is important
and here is how to import blueprints:
   https://paste.ofcode.org/39iV3QFqk35giGV8BSW9dtw   
"""