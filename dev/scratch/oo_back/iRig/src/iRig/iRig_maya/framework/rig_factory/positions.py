import os
import json
import rig_factory
package_location = os.path.dirname(rig_factory.__file__).replace('\\', '/')

with open('%s/static/data/quadruped_positions.json' % package_location, mode='r') as f:
    QUADRUPED_POSITIONS = json.loads(f.read())

with open('%s/static/data/biped_positions.json' % package_location, mode='r') as f:
    BIPED_POSITIONS = json.loads(f.read())

with open('%s/static/data/biped_handle_spaces.json' % package_location, mode='r') as f:
    BIPED_HANDLE_SPACES = json.loads(f.read())


with open('%s/static/data/quadruped_ik_back_leg_positions.json' % package_location, mode='r') as f:
    QUADRUPED_IK_BACK_LEG_POSITIONS = json.loads(f.read())
