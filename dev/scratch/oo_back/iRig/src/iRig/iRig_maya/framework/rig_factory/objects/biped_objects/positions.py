import os
import json
POSITIONS_FILEPATH = '%s/data/biped_positions.json' % os.path.dirname(__file__).replace('\\', '/')

with open(POSITIONS_FILEPATH, mode='r') as f:
    BIPED_POSITIONS = json.loads(f.read())
