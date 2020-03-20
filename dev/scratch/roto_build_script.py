"""
import sys
path = os.path.join("D:/all_works/scratch")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import roto_build_script
reload(roto_build_script)


roto_build_script.import_model()
#roto_build_script.create_packs()
#roto_build_script.save_pack_guides()
#roto_build_script.load_pack_guides()
#roto_build_script.create_bits()

"""
import os
import json
from collections import OrderedDict

import maya.cmds as mc

from rig_tools.frankenstein.character import spine_simple
from rig_tools.frankenstein.templates import master

reload(spine_simple)
reload(master)

INSTANCES = OrderedDict()
PACK_GUIDE_JSON = 'D:/test/test.json'
asset_name = 'Roto'


def import_model():
    model_dir = 'Y:/MAW/assets/type/Character/{}/products/model'.format(asset_name)
    model_path = sorted(os.listdir(model_dir))[-1]
    mc.file(os.path.join(model_dir, model_path), i=True)

    #
    mc.parent('Geo_Grp', world=True)
    mc.delete('Character_Grp')

    # fix modeling shit
    mc.setAttr('Model_A_Grp.tx', -20.175)

    #
    mc.hide('character_utilities_gp', 'Model_B_Grp')

    # put fur in a template
    for geo in mc.listRelatives('Model_A_Grp'):
        mc.setAttr(geo + '.overrideEnabled', True)
        mc.setAttr(geo + '.overrideDisplayType', 2)

    mc.setAttr("fur_groom_volume_Geo.overrideEnabled", True)
    mc.setAttr('fur_groom_volume_Geo.overrideDisplayType', 1)



def create_packs():
    INSTANCES['master'] = master.Template_Master()
    INSTANCES['master'].create_packs()

    INSTANCES['spine'] = spine_simple.Build_Spine_Simple()
    INSTANCES['spine'].create_pack()


def load_pack_guides():
    with open(PACK_GUIDE_JSON, 'r') as f:
        packs_data = json.load(f, object_pairs_hook=OrderedDict)
    if not packs_data:
        return

    for pack, guides_data in packs_data.items():
        if not mc.objExists(pack):
            continue
        for g, m in guides_data.items():
            if not mc.objExists(g):
                continue
            mc.xform(g, ws=True, m=m)


def save_pack_guides():
    packs_data = OrderedDict()
    packs = mc.listRelatives('BuildPack_Grp')
    for pack in packs:
        packs_data[pack] = OrderedDict()
        guides = mc.listRelatives(pack, ad=True) or []
        for g in reversed(guides):
            m = mc.xform(g, q=True, ws=True, m=True)
            packs_data[pack][g] = m

    with open(PACK_GUIDE_JSON, 'w') as f:
        json.dump(packs_data, f, sort_keys=False, indent=4)


def create_bits():
    master = INSTANCES.pop('master')
    master.create_bits()

    for instance in INSTANCES.values():
        instance.create_bit()


def fixSpine():
    aim = 'C_spine_ik_upper_torso_gimbal_Ctrl_C_spine_ik_lower_aim_gp_acn'
    mc.setAttr(aim + '.worldUpVector', 0, 1, 0)
