import maya.cmds as mc
import maya.api.OpenMaya as om2
from collections import OrderedDict

from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import connect
from ...lib import trsLib
from ...lib import display
from ...lib import crvLib
from ...lib import jntLib
from . import template
from ..command import fk


reload(connect)
reload(attrLib)
reload(display)
reload(fk)
reload(control)
reload(crvLib)
reload(attrLib)
reload(jntLib)
reload(trsLib)
reload(template)


class WingFeather(template.Template):

    def __init__(self, side='L', prefix='wing', **kwargs):

        kwargs['side'] = side
        kwargs['prefix'] = prefix

        self.aliases = {'firstPrimaryStart': 'firstPrimaryStart','firstPrimaryEnd': 'firstPrimaryEnd',
                        'feather_a_0' : 'feather_a_0','feather_a_1': 'feather_a_1',
                        'feather_a_2': 'feather_a_2','feather_a_3': 'feather_a_3','feather_b_0': 'feather_b_0',
                        'feather_b_1': 'feather_b_1','feather_b_2': 'feather_b_2','feather_b_3': 'feather_b_3',
                        'feather_c_0': 'feather_c_0','feather_c_1': 'feather_c_1','feather_c_2': 'feather_c_2',
                        'feather_c_3': 'feather_c_3','feather_d_0': 'feather_d_0','feather_d_1': 'feather_d_1',
                        'feather_d_2': 'feather_d_2','feather_d_3': 'feather_d_3','feather_e_0': 'feather_e_0',
                        'feather_e_1': 'feather_e_1','feather_e_2': 'feather_e_2','feather_e_3': 'feather_e_3',
                        'secondPrimaryStart': 'secondPrimaryStart','secondPrimaryEnd': 'secondPrimaryEnd',
                        'feather_f_0': 'feather_f_0', 'feather_f_1': 'feather_f_1',
                        'feather_f_2': 'feather_f_2', 'feather_f_3': 'feather_f_3', 'feather_g_0': 'feather_g_0',
                        'feather_g_1': 'feather_g_1', 'feather_g_2': 'feather_g_2', 'feather_g_3': 'feather_g_3',
                        'feather_h_0': 'feather_h_0', 'feather_h_1': 'feather_h_1', 'feather_h_2': 'feather_h_2',
                        'feather_h_3': 'feather_h_3', 'feather_i_0': 'feather_i_0', 'feather_i_1': 'feather_i_1',
                        'feather_i_2': 'feather_i_2', 'feather_i_3': 'feather_i_3', 'feather_j_0': 'feather_j_0',
                        'feather_j_1': 'feather_j_1', 'feather_j_2': 'feather_j_2', 'feather_j_3': 'feather_j_3',
                        'thirdPrimaryStart': 'thirdPrimaryStart','thirdPrimaryEnd': 'thirdPrimaryEnd',
                        'feather_k_0': 'feather_k_0', 'feather_k_1': 'feather_k_1',
                        'feather_k_2': 'feather_k_2', 'feather_k_3': 'feather_k_3', 'feather_l_0': 'feather_l_0',
                        'feather_l_1': 'feather_l_1', 'feather_l_2': 'feather_l_2', 'feather_l_3': 'feather_l_3',
                        'feather_m_0': 'feather_m_0', 'feather_m_1': 'feather_m_1', 'feather_m_2': 'feather_m_2',
                        'feather_m_3': 'feather_m_3', 'feather_n_0': 'feather_n_0', 'feather_n_1': 'feather_n_1',
                        'feather_n_2': 'feather_n_2', 'feather_n_3': 'feather_n_3', 'feather_o_0': 'feather_o_0',
                        'feather_o_1': 'feather_o_1', 'feather_o_2': 'feather_o_2', 'feather_o_3': 'feather_o_3',
                        'forthPrimaryStart': 'forthPrimaryStart','forthPrimaryEnd': 'forthPrimaryEnd',

                        }

        super(WingFeather, self).__init__(**kwargs)

    def createBlueprint(self):
        super(WingFeather, self).createBlueprint()

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        par = self.blueprintGrp


        self.blueprints['firstPrimaryStart'] = '{}_firstPrimaryStart_BLU'.format(self.name)
        self.blueprints['firstPrimaryEnd'] = '{}_firstPrimaryEnd_BLU'.format(self.name)

        self.blueprints['feather_a_0'] = '{}_feather_a_0_BLU'.format(self.name)
        self.blueprints['feather_a_1'] = '{}_feather_a_1_BLU'.format(self.name)
        self.blueprints['feather_a_2'] = '{}_feather_a_2_BLU'.format(self.name)
        self.blueprints['feather_a_3'] = '{}_feather_a_3_BLU'.format(self.name)

        self.blueprints['feather_b_0'] = '{}_feather_b_0_BLU'.format(self.name)
        self.blueprints['feather_b_1'] = '{}_feather_b_1_BLU'.format(self.name)
        self.blueprints['feather_b_2'] = '{}_feather_b_2_BLU'.format(self.name)
        self.blueprints['feather_b_3'] = '{}_feather_b_3_BLU'.format(self.name)

        self.blueprints['feather_c_0'] = '{}_feather_c_0_BLU'.format(self.name)
        self.blueprints['feather_c_1'] = '{}_feather_c_1_BLU'.format(self.name)
        self.blueprints['feather_c_2'] = '{}_feather_c_2_BLU'.format(self.name)
        self.blueprints['feather_c_3'] = '{}_feather_c_3_BLU'.format(self.name)

        self.blueprints['feather_d_0'] = '{}_feather_d_0_BLU'.format(self.name)
        self.blueprints['feather_d_1'] = '{}_feather_d_1_BLU'.format(self.name)
        self.blueprints['feather_d_2'] = '{}_feather_d_2_BLU'.format(self.name)
        self.blueprints['feather_d_3'] = '{}_feather_d_3_BLU'.format(self.name)

        self.blueprints['feather_e_0'] = '{}_feather_e_0_BLU'.format(self.name)
        self.blueprints['feather_e_1'] = '{}_feather_e_1_BLU'.format(self.name)
        self.blueprints['feather_e_2'] = '{}_feather_e_2_BLU'.format(self.name)
        self.blueprints['feather_e_3'] = '{}_feather_e_3_BLU'.format(self.name)


        self.blueprints['secondPrimaryStart'] = '{}_secondPrimaryStart_BLU'.format(self.name)
        self.blueprints['secondPrimaryEnd'] = '{}_secondPrimaryEnd_BLU'.format(self.name)

        self.blueprints['feather_f_0'] = '{}_feather_f_0_BLU'.format(self.name)
        self.blueprints['feather_f_1'] = '{}_feather_f_1_BLU'.format(self.name)
        self.blueprints['feather_f_2'] = '{}_feather_f_2_BLU'.format(self.name)
        self.blueprints['feather_f_3'] = '{}_feather_f_3_BLU'.format(self.name)

        self.blueprints['feather_g_0'] = '{}_feather_g_0_BLU'.format(self.name)
        self.blueprints['feather_g_1'] = '{}_feather_g_1_BLU'.format(self.name)
        self.blueprints['feather_g_2'] = '{}_feather_g_2_BLU'.format(self.name)
        self.blueprints['feather_g_3'] = '{}_feather_g_3_BLU'.format(self.name)

        self.blueprints['feather_h_0'] = '{}_feather_h_0_BLU'.format(self.name)
        self.blueprints['feather_h_1'] = '{}_feather_h_1_BLU'.format(self.name)
        self.blueprints['feather_h_2'] = '{}_feather_h_2_BLU'.format(self.name)
        self.blueprints['feather_h_3'] = '{}_feather_h_3_BLU'.format(self.name)

        self.blueprints['feather_i_0'] = '{}_feather_i_0_BLU'.format(self.name)
        self.blueprints['feather_i_1'] = '{}_feather_i_1_BLU'.format(self.name)
        self.blueprints['feather_i_2'] = '{}_feather_i_2_BLU'.format(self.name)
        self.blueprints['feather_i_3'] = '{}_feather_i_3_BLU'.format(self.name)

        self.blueprints['feather_j_0'] = '{}_feather_j_0_BLU'.format(self.name)
        self.blueprints['feather_j_1'] = '{}_feather_j_1_BLU'.format(self.name)
        self.blueprints['feather_j_2'] = '{}_feather_j_2_BLU'.format(self.name)
        self.blueprints['feather_j_3'] = '{}_feather_j_3_BLU'.format(self.name)

        self.blueprints['feather_k_0'] = '{}_feather_k_0_BLU'.format(self.name)
        self.blueprints['feather_k_1'] = '{}_feather_k_1_BLU'.format(self.name)
        self.blueprints['feather_k_2'] = '{}_feather_k_2_BLU'.format(self.name)
        self.blueprints['feather_k_3'] = '{}_feather_k_3_BLU'.format(self.name)


        self.blueprints['thirdPrimaryStart'] = '{}_thirdPrimaryStart_BLU'.format(self.name)
        self.blueprints['thirdPrimaryEnd'] = '{}_thirdPrimaryEnd_BLU'.format(self.name)

        self.blueprints['feather_l_0'] = '{}_feather_l_0_BLU'.format(self.name)
        self.blueprints['feather_l_1'] = '{}_feather_l_1_BLU'.format(self.name)
        self.blueprints['feather_l_2'] = '{}_feather_l_2_BLU'.format(self.name)
        self.blueprints['feather_l_3'] = '{}_feather_l_3_BLU'.format(self.name)

        self.blueprints['feather_m_0'] = '{}_feather_m_0_BLU'.format(self.name)
        self.blueprints['feather_m_1'] = '{}_feather_m_1_BLU'.format(self.name)
        self.blueprints['feather_m_2'] = '{}_feather_m_2_BLU'.format(self.name)
        self.blueprints['feather_m_3'] = '{}_feather_m_3_BLU'.format(self.name)

        self.blueprints['feather_n_0'] = '{}_feather_n_0_BLU'.format(self.name)
        self.blueprints['feather_n_1'] = '{}_feather_n_1_BLU'.format(self.name)
        self.blueprints['feather_n_2'] = '{}_feather_n_2_BLU'.format(self.name)
        self.blueprints['feather_n_3'] = '{}_feather_n_3_BLU'.format(self.name)

        self.blueprints['feather_o_0'] = '{}_feather_o_0_BLU'.format(self.name)
        self.blueprints['feather_o_1'] = '{}_feather_o_1_BLU'.format(self.name)
        self.blueprints['feather_o_2'] = '{}_feather_o_2_BLU'.format(self.name)
        self.blueprints['feather_o_3'] = '{}_feather_o_3_BLU'.format(self.name)


        self.blueprints['forthPrimaryStart'] = '{}_forthPrimaryStart_BLU'.format(self.name)
        self.blueprints['forthPrimaryEnd'] = '{}_forthPrimaryEnd_BLU'.format(self.name)

        # create input blueprints
        if not mc.objExists(self.blueprints['firstPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['firstPrimaryStart'])
            mc.xform(self.blueprints['firstPrimaryStart'], ws=True,  t=(3 * mult, 17, 0))

        if not mc.objExists(self.blueprints['firstPrimaryEnd']):
            mc.joint(self.blueprints['firstPrimaryStart'], name=self.blueprints['firstPrimaryEnd'])
            mc.xform(self.blueprints['firstPrimaryEnd'], ws=True, t=(3 * mult, 17, -7))


        if not mc.objExists(self.blueprints['feather_a_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_a_0'])
            mc.xform(self.blueprints['feather_a_0'], ws=True, t=(3.3 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_a_1']):
            mc.joint(self.blueprints['feather_a_0'], name=self.blueprints['feather_a_1'])
            mc.xform(self.blueprints['feather_a_1'], ws=True, t=(3.3 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_a_2']):
            mc.joint(self.blueprints['feather_a_1'], name=self.blueprints['feather_a_2'])
            mc.xform(self.blueprints['feather_a_2'], ws=True, t=(3.3 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_a_3']):
            mc.joint(self.blueprints['feather_a_2'], name=self.blueprints['feather_a_3'])
            mc.xform(self.blueprints['feather_a_3'], ws=True, t=(3.3 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_b_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_b_0'])
            mc.xform(self.blueprints['feather_b_0'], ws=True, t=(4.3 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_b_1']):
            mc.joint(self.blueprints['feather_b_0'], name=self.blueprints['feather_b_1'])
            mc.xform(self.blueprints['feather_b_1'], ws=True, t=(4.3 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_b_2']):
            mc.joint(self.blueprints['feather_b_1'], name=self.blueprints['feather_b_2'])
            mc.xform(self.blueprints['feather_b_2'], ws=True, t=(4.3 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_b_3']):
            mc.joint(self.blueprints['feather_b_2'], name=self.blueprints['feather_b_3'])
            mc.xform(self.blueprints['feather_b_3'], ws=True, t=(4.3 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_c_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_c_0'])
            mc.xform(self.blueprints['feather_c_0'], ws=True, t=(5.3 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_c_1']):
            mc.joint(self.blueprints['feather_c_0'], name=self.blueprints['feather_c_1'])
            mc.xform(self.blueprints['feather_c_1'], ws=True, t=(5.3 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_c_2']):
            mc.joint(self.blueprints['feather_c_1'], name=self.blueprints['feather_c_2'])
            mc.xform(self.blueprints['feather_c_2'], ws=True, t=(5.3 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_c_3']):
            mc.joint(self.blueprints['feather_c_2'], name=self.blueprints['feather_c_3'])
            mc.xform(self.blueprints['feather_c_3'], ws=True, t=(5.3 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_d_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_d_0'])
            mc.xform(self.blueprints['feather_d_0'], ws=True, t=(6.3 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_d_1']):
            mc.joint(self.blueprints['feather_d_0'], name=self.blueprints['feather_d_1'])
            mc.xform(self.blueprints['feather_d_1'], ws=True, t=(6.3 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_d_2']):
            mc.joint(self.blueprints['feather_d_1'], name=self.blueprints['feather_d_2'])
            mc.xform(self.blueprints['feather_d_2'], ws=True, t=(6.3 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_d_3']):
            mc.joint(self.blueprints['feather_d_2'], name=self.blueprints['feather_d_3'])
            mc.xform(self.blueprints['feather_d_3'], ws=True, t=(6.3 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_e_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_e_0'])
            mc.xform(self.blueprints['feather_e_0'], ws=True, t=(7.3 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_e_1']):
            mc.joint(self.blueprints['feather_e_0'], name=self.blueprints['feather_e_1'])
            mc.xform(self.blueprints['feather_e_1'], ws=True, t=(7.3 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_e_2']):
            mc.joint(self.blueprints['feather_e_1'], name=self.blueprints['feather_e_2'])
            mc.xform(self.blueprints['feather_e_2'], ws=True, t=(7.3 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_e_3']):
            mc.joint(self.blueprints['feather_e_2'], name=self.blueprints['feather_e_3'])
            mc.xform(self.blueprints['feather_e_3'], ws=True, t=(7.3 * mult, 17, -8))


        if not mc.objExists(self.blueprints['secondPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['secondPrimaryStart'])
            mc.xform(self.blueprints['secondPrimaryStart'], ws=True, t=(8 * mult, 17, 0))

        if not mc.objExists(self.blueprints['secondPrimaryEnd']):
            mc.joint(self.blueprints['secondPrimaryStart'], name=self.blueprints['secondPrimaryEnd'])
            mc.xform(self.blueprints['secondPrimaryEnd'], ws=True, t=(9 * mult, 17, -7))


        if not mc.objExists(self.blueprints['feather_f_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_f_0'])
            mc.xform(self.blueprints['feather_f_0'], ws=True, t=(8.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_f_1']):
            mc.joint(self.blueprints['feather_f_0'], name=self.blueprints['feather_f_1'])
            mc.xform(self.blueprints['feather_f_1'], ws=True, t=(8.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_f_2']):
            mc.joint(self.blueprints['feather_f_1'], name=self.blueprints['feather_f_2'])
            mc.xform(self.blueprints['feather_f_2'], ws=True, t=(8.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_f_3']):
            mc.joint(self.blueprints['feather_f_2'], name=self.blueprints['feather_f_3'])
            mc.xform(self.blueprints['feather_f_3'], ws=True, t=(8.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_g_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_g_0'])
            mc.xform(self.blueprints['feather_g_0'], ws=True, t=(9.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_g_1']):
            mc.joint(self.blueprints['feather_g_0'], name=self.blueprints['feather_g_1'])
            mc.xform(self.blueprints['feather_g_1'], ws=True, t=(9.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_g_2']):
            mc.joint(self.blueprints['feather_g_1'], name=self.blueprints['feather_g_2'])
            mc.xform(self.blueprints['feather_g_2'], ws=True, t=(9.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_g_3']):
            mc.joint(self.blueprints['feather_g_2'], name=self.blueprints['feather_g_3'])
            mc.xform(self.blueprints['feather_g_3'], ws=True, t=(9.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_h_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_h_0'])
            mc.xform(self.blueprints['feather_h_0'], ws=True, t=(10.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_h_1']):
            mc.joint(self.blueprints['feather_h_0'], name=self.blueprints['feather_h_1'])
            mc.xform(self.blueprints['feather_h_1'], ws=True, t=(10.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_h_2']):
            mc.joint(self.blueprints['feather_h_1'], name=self.blueprints['feather_h_2'])
            mc.xform(self.blueprints['feather_h_2'], ws=True, t=(10.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_h_3']):
            mc.joint(self.blueprints['feather_h_2'], name=self.blueprints['feather_h_3'])
            mc.xform(self.blueprints['feather_h_3'], ws=True, t=(10.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_i_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_i_0'])
            mc.xform(self.blueprints['feather_i_0'], ws=True, t=(11.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_i_1']):
            mc.joint(self.blueprints['feather_i_0'], name=self.blueprints['feather_i_1'])
            mc.xform(self.blueprints['feather_i_1'], ws=True, t=(11.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_i_2']):
            mc.joint(self.blueprints['feather_i_1'], name=self.blueprints['feather_i_2'])
            mc.xform(self.blueprints['feather_i_2'], ws=True, t=(11.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_i_3']):
            mc.joint(self.blueprints['feather_i_2'], name=self.blueprints['feather_i_3'])
            mc.xform(self.blueprints['feather_i_3'], ws=True, t=(11.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_j_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_j_0'])
            mc.xform(self.blueprints['feather_j_0'], ws=True, t=(12.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_j_1']):
            mc.joint(self.blueprints['feather_j_0'], name=self.blueprints['feather_j_1'])
            mc.xform(self.blueprints['feather_j_1'], ws=True, t=(12.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_j_2']):
            mc.joint(self.blueprints['feather_j_1'], name=self.blueprints['feather_j_2'])
            mc.xform(self.blueprints['feather_j_2'], ws=True, t=(12.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_j_3']):
            mc.joint(self.blueprints['feather_j_2'], name=self.blueprints['feather_j_3'])
            mc.xform(self.blueprints['feather_j_3'], ws=True, t=(12.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['thirdPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['thirdPrimaryStart'])
            mc.xform(self.blueprints['thirdPrimaryStart'], ws=True, t=(13.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_k_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_k_0'])
            mc.xform(self.blueprints['feather_k_0'], ws=True, t=(14.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_k_1']):
            mc.joint(self.blueprints['feather_k_0'], name=self.blueprints['feather_k_1'])
            mc.xform(self.blueprints['feather_k_1'], ws=True, t=(14.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_k_2']):
            mc.joint(self.blueprints['feather_k_1'], name=self.blueprints['feather_k_2'])
            mc.xform(self.blueprints['feather_k_2'], ws=True, t=(14.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_k_3']):
            mc.joint(self.blueprints['feather_k_2'], name=self.blueprints['feather_k_3'])
            mc.xform(self.blueprints['feather_k_3'], ws=True, t=(14.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_l_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_l_0'])
            mc.xform(self.blueprints['feather_l_0'], ws=True, t=(15.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_l_1']):
            mc.joint(self.blueprints['feather_l_0'], name=self.blueprints['feather_l_1'])
            mc.xform(self.blueprints['feather_l_1'], ws=True, t=(15.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_l_2']):
            mc.joint(self.blueprints['feather_l_1'], name=self.blueprints['feather_l_2'])
            mc.xform(self.blueprints['feather_l_2'], ws=True, t=(15.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_l_3']):
            mc.joint(self.blueprints['feather_l_2'], name=self.blueprints['feather_l_3'])
            mc.xform(self.blueprints['feather_l_3'], ws=True, t=(15.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_m_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_m_0'])
            mc.xform(self.blueprints['feather_m_0'], ws=True, t=(16.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_m_1']):
            mc.joint(self.blueprints['feather_m_0'], name=self.blueprints['feather_m_1'])
            mc.xform(self.blueprints['feather_m_1'], ws=True, t=(16.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_m_2']):
            mc.joint(self.blueprints['feather_m_1'], name=self.blueprints['feather_m_2'])
            mc.xform(self.blueprints['feather_m_2'], ws=True, t=(16.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_m_3']):
            mc.joint(self.blueprints['feather_m_2'], name=self.blueprints['feather_m_3'])
            mc.xform(self.blueprints['feather_m_3'], ws=True, t=(16.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_n_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_n_0'])
            mc.xform(self.blueprints['feather_n_0'], ws=True, t=(17.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_n_1']):
            mc.joint(self.blueprints['feather_n_0'], name=self.blueprints['feather_n_1'])
            mc.xform(self.blueprints['feather_n_1'], ws=True, t=(17.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_n_2']):
            mc.joint(self.blueprints['feather_n_1'], name=self.blueprints['feather_n_2'])
            mc.xform(self.blueprints['feather_n_2'], ws=True, t=(17.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_n_3']):
            mc.joint(self.blueprints['feather_n_2'], name=self.blueprints['feather_n_3'])
            mc.xform(self.blueprints['feather_n_3'], ws=True, t=(17.7 * mult, 17, -8))

        if not mc.objExists(self.blueprints['feather_o_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_o_0'])
            mc.xform(self.blueprints['feather_o_0'], ws=True, t=(18.7 * mult, 17, 0))

        if not mc.objExists(self.blueprints['feather_o_1']):
            mc.joint(self.blueprints['feather_o_0'], name=self.blueprints['feather_o_1'])
            mc.xform(self.blueprints['feather_o_1'], ws=True, t=(18.7 * mult, 17, -3))

        if not mc.objExists(self.blueprints['feather_o_2']):
            mc.joint(self.blueprints['feather_o_1'], name=self.blueprints['feather_o_2'])
            mc.xform(self.blueprints['feather_o_2'], ws=True, t=(18.7 * mult, 17, -6))

        if not mc.objExists(self.blueprints['feather_o_3']):
            mc.joint(self.blueprints['feather_o_2'], name=self.blueprints['feather_o_3'])
            mc.xform(self.blueprints['feather_o_3'], ws=True, t=(18.7 * mult, 17, -8))


        if not mc.objExists(self.blueprints['thirdPrimaryEnd']):
            mc.joint(self.blueprints['thirdPrimaryStart'], name=self.blueprints['thirdPrimaryEnd'])
            mc.xform(self.blueprints['thirdPrimaryEnd'], ws=True, t=(14 * mult, 17, -7))

        if not mc.objExists(self.blueprints['forthPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['forthPrimaryStart'])
            mc.xform(self.blueprints['forthPrimaryStart'], ws=True, t=(20 * mult, 17, 0))

        if not mc.objExists(self.blueprints['forthPrimaryEnd']):
            mc.joint(self.blueprints['forthPrimaryStart'], name=self.blueprints['forthPrimaryEnd'])
            mc.xform(self.blueprints['forthPrimaryEnd'], ws=True, t=(21 * mult, 17, -7))



        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=self.blueprints)

    def createJoints(self):

        # create joints
        par = self.moduleGrp
        self.firstPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('firstPrimaryStart', 'firstPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.firstPrimaryJnts.append(jnt)
            par = jnt

        self.orientJnts(self.firstPrimaryJnts)


        par = self.moduleGrp
        self.secondPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('secondPrimaryStart', 'secondPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.secondPrimaryJnts.append(jnt)
            par = jnt

        self.orientJnts(self.secondPrimaryJnts)

        par = self.moduleGrp
        self.thirdPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('thirdPrimaryStart', 'thirdPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.thirdPrimaryJnts.append(jnt)
            par = jnt

        self.orientJnts(self.thirdPrimaryJnts)
        par = self.moduleGrp
        self.forthPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('forthPrimaryStart', 'forthPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.forthPrimaryJnts.append(jnt)
            par = jnt

        self.orientJnts(self.forthPrimaryJnts)
        par = self.moduleGrp
        self.firstFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_a_0', 'feather_a_1','feather_a_2','feather_a_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.firstFeather.append(jnt)
            par = jnt

        self.orientJnts(self.firstFeather)

        par = self.moduleGrp
        self.secondFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_b_0', 'feather_b_1','feather_b_2','feather_b_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.secondFeather.append(jnt)
            par = jnt

        self.orientJnts(self.secondFeather)

        par = self.moduleGrp
        self.thirdFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_c_0', 'feather_c_1','feather_c_2','feather_c_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.thirdFeather.append(jnt)
            par = jnt

        self.orientJnts(self.thirdFeather)
        par = self.moduleGrp
        self.forthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_d_0', 'feather_d_1','feather_d_2','feather_d_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.forthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.forthFeather)
        par = self.moduleGrp
        self.fifthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_e_0', 'feather_e_1','feather_e_2','feather_e_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.fifthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.fifthFeather)

        par = self.moduleGrp
        self.sixFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_f_0', 'feather_f_1','feather_f_2','feather_f_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.sixFeather.append(jnt)
            par = jnt

        self.orientJnts(self.sixFeather)
        par = self.moduleGrp
        self.seventhFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_g_0', 'feather_g_1','feather_g_2','feather_g_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.seventhFeather.append(jnt)
            par = jnt

        self.orientJnts(self.seventhFeather)
        par = self.moduleGrp
        self.eightthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_h_0', 'feather_h_1','feather_h_2','feather_h_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.eightthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.eightthFeather)
        par = self.moduleGrp
        self.ninethFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_i_0', 'feather_i_1','feather_i_2','feather_i_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.ninethFeather.append(jnt)
            par = jnt

        self.orientJnts(self.ninethFeather)
        par = self.moduleGrp
        self.tenthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_j_0', 'feather_j_1','feather_j_2','feather_j_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.tenthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.tenthFeather)
        par = self.moduleGrp
        self.eleventhFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_k_0', 'feather_k_1','feather_k_2','feather_k_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.eleventhFeather.append(jnt)
            par = jnt

        self.orientJnts(self.eleventhFeather)
        par = self.moduleGrp
        self.twelevethFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_l_0', 'feather_l_1','feather_l_2','feather_l_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.twelevethFeather.append(jnt)
            par = jnt

        self.orientJnts(self.twelevethFeather)
        par = self.moduleGrp
        self.thirteenthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_m_0', 'feather_m_1','feather_m_2','feather_m_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.thirteenthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.thirteenthFeather)
        par = self.moduleGrp
        self.forteenthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_n_0', 'feather_n_1','feather_n_2','feather_n_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.forteenthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.forteenthFeather)
        par = self.moduleGrp
        self.fifteenthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_o_0', 'feather_o_1','feather_o_2','feather_o_3'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.fifteenthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.fifteenthFeather)
        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):
        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']

        upLoc = mc.createNode('transform')
        mc.xform(upLoc, ws = True, t=(mult * 42.97 , 17.17, 8.58))
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='x', upAxes='z', inverseUpAxes=inverseUpAxes)
        mc.delete(upLoc)


    def build(self):
        """
        building necessary nodes
        """
        super(WingFeather, self).build()

        self.iconSize = trsLib.getDistance(self.joints['firstPrimaryStart'], self.joints['firstPrimaryEnd'])
        mult = [1, -1][self.side == 'R']


        # create primary controls
        self.PrimaryCtls = {'primaryCtls': []}
        self.firstPrimaryCtl = control.Control(descriptor=self.prefix + '_01_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['firstPrimaryStart'],
                                          matchRotate=self.joints['firstPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.firstPrimaryCtl.name, 'blue')

        mc.parentConstraint(self.firstPrimaryCtl.name,self.joints['firstPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.firstPrimaryCtl.name,self.joints['firstPrimaryStart'], mo =  True)

        self.PrimaryCtls['primaryCtls'].append(self.firstPrimaryCtl.name)
        self.secondPrimaryCtl = control.Control(descriptor=self.prefix + '_02_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['secondPrimaryStart'],
                                          matchRotate=self.joints['secondPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.secondPrimaryCtl.name, 'blue')


        mc.parentConstraint(self.secondPrimaryCtl.name,self.joints['secondPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.secondPrimaryCtl.name,self.joints['secondPrimaryStart'], mo =  True)


        self.PrimaryCtls['primaryCtls'].append(self.secondPrimaryCtl.name)
        self.thirdPrimaryCtl = control.Control(descriptor=self.prefix + '_03_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['thirdPrimaryStart'],
                                          matchRotate=self.joints['thirdPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.thirdPrimaryCtl.name, 'blue')


        mc.parentConstraint(self.thirdPrimaryCtl.name,self.joints['thirdPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.thirdPrimaryCtl.name,self.joints['thirdPrimaryStart'], mo =  True)

        self.PrimaryCtls['primaryCtls'].append(self.thirdPrimaryCtl.name)
        self.forthPrimaryCtl = control.Control(descriptor=self.prefix + '_04_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['forthPrimaryStart'],
                                          matchRotate=self.joints['forthPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.forthPrimaryCtl.name, 'blue')


        mc.parentConstraint(self.forthPrimaryCtl.name,self.joints['forthPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.forthPrimaryCtl.name,self.joints['forthPrimaryStart'], mo =  True)

        self.PrimaryCtls['primaryCtls'].append(self.forthPrimaryCtl.name)
        self.setOut('primaryCtls', self.PrimaryCtls)

        self.primaryCtlsGrps  = {'primaryGrps':[]}
        self.primaryCtlsGrps['primaryGrps'].append(self.firstPrimaryCtl.zro)
        self.primaryCtlsGrps['primaryGrps'].append(self.secondPrimaryCtl.zro)
        self.primaryCtlsGrps['primaryGrps'].append(self.thirdPrimaryCtl.zro)
        self.primaryCtlsGrps['primaryGrps'].append(self.forthPrimaryCtl.zro)

        self.primaryCtlOffsets = []
        for i in self.primaryCtlsGrps['primaryGrps']:
            primaryCtlOffset = mc.createNode('transform' , n  = i + '_offset')
            primaryCtlGrp= mc.createNode('transform' , n  = i + '_GRP')
            trsLib.match(primaryCtlOffset, i )
            trsLib.match(primaryCtlGrp,primaryCtlOffset)
            mc.parent(i,primaryCtlOffset )
            mc.parent(primaryCtlGrp ,self.ctlGrp)
            mc.parent(primaryCtlOffset,primaryCtlGrp )
            self.primaryCtlOffsets.append(primaryCtlOffset)
        for i in self.primaryCtlsGrps['primaryGrps']:
            attrLib.lockHideAttrs(i, ['t' , 's'], lock=True, hide=True)

        # create feather controls
        # first feather control
        featherFirstFKCtls = {'featherFKCtls' : []}
        feathersecondFKCtls = {'featherFKCtls' : []}
        featherthirdFKCtls = {'featherFKCtls' : []}
        self.firstFeatherFK = fk.Fk(joints=[self.joints['feather_a_0'],self.joints['feather_a_1'],
                      self.joints['feather_a_2'],self.joints['feather_a_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # second feather control
        self.secondFeatherFK = fk.Fk(joints=[self.joints['feather_b_0'],self.joints['feather_b_1'],
                      self.joints['feather_b_2'],self.joints['feather_b_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # third feather control
        self.thirdFeatherFK = fk.Fk(joints=[self.joints['feather_c_0'],self.joints['feather_c_1'],
                      self.joints['feather_c_2'],self.joints['feather_c_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        featherforthFKCtls = {'featherFKCtls' : []}
        # forth feather control
        self.forthFeatherFK = fk.Fk(joints=[self.joints['feather_d_0'],self.joints['feather_d_1'],
                      self.joints['feather_d_2'],self.joints['feather_d_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # fifth feather control
        self.fifthFeatherFK = fk.Fk(joints=[self.joints['feather_e_0'],self.joints['feather_e_1'],
                      self.joints['feather_e_2'],self.joints['feather_e_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        # sixth feather control
        self.sixthFeatherFK = fk.Fk(joints=[self.joints['feather_f_0'],self.joints['feather_f_1'],
                      self.joints['feather_f_2'],self.joints['feather_f_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)



        # seventh feather control
        self.seventhFeatherFK = fk.Fk(joints=[self.joints['feather_g_0'],self.joints['feather_g_1'],
                      self.joints['feather_g_2'],self.joints['feather_g_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # eights Feather control
        self.eightFeatherFK = fk.Fk(joints=[self.joints['feather_h_0'],self.joints['feather_h_1'],
                      self.joints['feather_h_2'],self.joints['feather_h_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # nineth feather control
        self.nineFeatherFK = fk.Fk(joints=[self.joints['feather_i_0'],self.joints['feather_i_1'],
                      self.joints['feather_i_2'],self.joints['feather_i_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # tenth feather control
        self.tenthFeatherFK = fk.Fk(joints=[self.joints['feather_j_0'],self.joints['feather_j_1'],
                      self.joints['feather_j_2'],self.joints['feather_j_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        # eleventh feather control
        self.eleventhFeatherFK = fk.Fk(joints=[self.joints['feather_k_0'],self.joints['feather_k_1'],
                      self.joints['feather_k_2'],self.joints['feather_k_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)


        # tweleve feather control
        self.twelvethFeatherFK = fk.Fk(joints=[self.joints['feather_l_0'],self.joints['feather_l_1'],
                      self.joints['feather_l_2'],self.joints['feather_l_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        # thirteen feather control
        self.thirteenthFeatherFK = fk.Fk(joints=[self.joints['feather_m_0'],self.joints['feather_m_1'],
                      self.joints['feather_m_2'],self.joints['feather_m_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        # forteen feather control
        self.forteenthFeatherFK = fk.Fk(joints=[self.joints['feather_n_0'],self.joints['feather_n_1'],
                      self.joints['feather_n_2'],self.joints['feather_n_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        # fifteen feather control
        self.fifteenthFeatherFK = fk.Fk(joints=[self.joints['feather_o_0'],self.joints['feather_o_1'],
                      self.joints['feather_o_2'],self.joints['feather_o_3']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        featherFirstFKCtls['featherFKCtls'].append(self.firstFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.secondFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.thirdFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.forthFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.fifthFeatherFK[0].name)
        count = 1
        for i in featherFirstFKCtls['featherFKCtls']:
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = count)
            count -= 0.2


        feathersecondFKCtls['featherFKCtls'].append(self.sixthFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.seventhFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.eightFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.nineFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.tenthFeatherFK[0].name)
        count = 1
        for i in feathersecondFKCtls['featherFKCtls']:
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = count)
            count -= 0.2


        featherthirdFKCtls['featherFKCtls'].append(self.eleventhFeatherFK[0].name)
        featherthirdFKCtls['featherFKCtls'].append(self.twelvethFeatherFK[0].name)
        featherthirdFKCtls['featherFKCtls'].append(self.thirteenthFeatherFK[0].name)
        featherthirdFKCtls['featherFKCtls'].append(self.forteenthFeatherFK[0].name)
        featherthirdFKCtls['featherFKCtls'].append(self.fifteenthFeatherFK[0].name)
        count = 1
        for i in featherthirdFKCtls['featherFKCtls']:
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = count)
            count -= 0.2


        self.firstPartfeatherCtlsGrps  = {'featherGrps':[]}
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.firstFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.secondFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.thirdFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.forthFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.fifthFeatherFK[0].zro)

        self.firstFeatherPart = mc.createNode('transform', n = self.side +'_firstFeatherPart', parent = self.firstFeatherFK[0].name)
        mc.parent(self.firstFeatherPart, self.ctlGrp)


        for i in self.firstPartfeatherCtlsGrps['featherGrps']:
            firstFeatherCtlOffset = mc.createNode('transform' , n  = i + '_offset')
            firstFeatherCtlGrp= mc.createNode('transform' , n  = i + '_GRP')
            trsLib.match(firstFeatherCtlOffset, i )
            trsLib.match(firstFeatherCtlGrp,firstFeatherCtlOffset)
            mc.parent(i,firstFeatherCtlOffset )
            mc.parent(firstFeatherCtlOffset,firstFeatherCtlGrp )
            mc.parent(firstFeatherCtlGrp, self.firstFeatherPart)
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = 0)



        self.secondPartfeatherCtlsGrps  = {'featherGrps':[]}
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.sixthFeatherFK[0].zro)
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.seventhFeatherFK[0].zro)
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.eightFeatherFK[0].zro)
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.nineFeatherFK[0].zro)
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.tenthFeatherFK[0].zro)

        self.secondFeatherPart = mc.createNode('transform', n = self.side + '_secondFeatherPart', parent = self.sixthFeatherFK[0].name)
        mc.parent(self.secondFeatherPart, self.ctlGrp)

        for i in self.secondPartfeatherCtlsGrps['featherGrps']:
            firstFeatherCtlOffset = mc.createNode('transform', n=i + '_offset')
            secondFeatherCtlGrp = mc.createNode('transform', n=i + '_GRP')
            trsLib.match(firstFeatherCtlOffset, i)
            trsLib.match(secondFeatherCtlGrp, firstFeatherCtlOffset)
            mc.parent(i, firstFeatherCtlOffset)
            mc.parent(firstFeatherCtlOffset, secondFeatherCtlGrp)
            mc.parent(secondFeatherCtlGrp, self.secondFeatherPart )
            attrLib.addFloat(i, 'blend', min=0, max=1, dv=0)


        self.thirdPartfeatherCtlsGrps  = {'featherGrps':[]}
        self.thirdPartfeatherCtlsGrps['featherGrps'].append(self.eleventhFeatherFK[0].zro)
        self.thirdPartfeatherCtlsGrps['featherGrps'].append(self.twelvethFeatherFK[0].zro)
        self.thirdPartfeatherCtlsGrps['featherGrps'].append(self.thirteenthFeatherFK[0].zro)
        self.thirdPartfeatherCtlsGrps['featherGrps'].append(self.forteenthFeatherFK[0].zro)
        self.thirdPartfeatherCtlsGrps['featherGrps'].append(self.fifteenthFeatherFK[0].zro)

        self.thirdFeatherPart = mc.createNode('transform', n = self.side + '_thirdFeatherPart', parent = self.eleventhFeatherFK[0].name)
        mc.parent(self.thirdFeatherPart, self.ctlGrp)

        for i in self.thirdPartfeatherCtlsGrps['featherGrps']:
            firstFeatherCtlOffset = mc.createNode('transform', n=i + '_offset')
            thirdFeatherCtlGrp = mc.createNode('transform', n=i + '_GRP')
            trsLib.match(firstFeatherCtlOffset, i)
            trsLib.match(thirdFeatherCtlGrp, firstFeatherCtlOffset)
            mc.parent(i, firstFeatherCtlOffset)
            mc.parent(firstFeatherCtlOffset, thirdFeatherCtlGrp)
            mc.parent(thirdFeatherCtlGrp, self.thirdFeatherPart )
            attrLib.addFloat(i, 'blend', min=0, max=1, dv=0)



        # connect blend attrs to their group blend attrs
        mc.connectAttr(self.firstFeatherFK[0].name + '.blend', self.firstFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.secondFeatherFK[0].name + '.blend', self.secondFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.thirdFeatherFK[0].name + '.blend', self.thirdFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.forthFeatherFK[0].name + '.blend', self.forthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.fifthFeatherFK[0].name + '.blend', self.fifthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.sixthFeatherFK[0].name + '.blend', self.sixthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.seventhFeatherFK[0].name + '.blend', self.seventhFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.eightFeatherFK[0].name + '.blend', self.eightFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.nineFeatherFK[0].name + '.blend', self.nineFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.tenthFeatherFK[0].name + '.blend', self.tenthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.eleventhFeatherFK[0].name + '.blend', self.eleventhFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.twelvethFeatherFK[0].name + '.blend', self.twelvethFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.thirteenthFeatherFK[0].name + '.blend', self.thirteenthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.forteenthFeatherFK[0].name + '.blend', self.forteenthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.fifteenthFeatherFK[0].name + '.blend', self.fifteenthFeatherFK[0].zro + '.blend')

        # connect first part feathers offset grps
        firstPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_01_PMA')
        mc.connectAttr(self.firstPrimaryCtl.name + '.rotate', firstPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.firstPrimaryCtl.zro + '.rotate', firstPrimaryPlusNode + '.input3D[1]')

        featherthirdFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherThird_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherthirdFKBlendNode + '.color1')
        mc.connectAttr(featherthirdFKBlendNode + '.output' , self.thirdFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.thirdFeatherFK[0].zro + '.blend' , featherthirdFKBlendNode + '.blender')

        secondPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_02_PMA')
        mc.connectAttr(self.secondPrimaryCtl.zro + '.rotate', secondPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.secondPrimaryCtl.name + '.rotate', secondPrimaryPlusNode + '.input3D[1]')

        self.secondPrimaryPlusNodeSwitch = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_switch_02_PMA')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , self.secondPrimaryPlusNodeSwitch + '.input3D[0]')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D' , featherthirdFKBlendNode + '.color2')

        featherForthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherForth_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherForthFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D' , featherForthFKBlendNode + '.color2')
        mc.connectAttr(featherForthFKBlendNode + '.output' , self.forthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.forthFeatherFK[0].zro + '.blend' , featherForthFKBlendNode + '.blender')

        featherFifthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherFifth_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherFifthFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D', featherFifthFKBlendNode + '.color2')
        mc.connectAttr(featherFifthFKBlendNode + '.output' , self.fifthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.fifthFeatherFK[0].zro + '.blend' , featherFifthFKBlendNode + '.blender')

        featherFirstFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherFirst_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherFirstFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D' , featherFirstFKBlendNode + '.color2')
        mc.connectAttr(featherFirstFKBlendNode + '.output' , self.firstFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.firstFeatherFK[0].zro + '.blend' , featherFirstFKBlendNode + '.blender')

        featherSecondFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherSecond_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherSecondFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D', featherSecondFKBlendNode + '.color2')
        mc.connectAttr(featherSecondFKBlendNode + '.output' , self.secondFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.secondFeatherFK[0].zro + '.blend' , featherSecondFKBlendNode + '.blender')

        # connect second part feathers offset grps
        firstAndSecondPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_03_PMA')
        mc.connectAttr(self.thirdPrimaryCtl.zro + '.rotate', firstAndSecondPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.thirdPrimaryCtl.name + '.rotate', firstAndSecondPrimaryPlusNode + '.input3D[1]')

        self.thirdPrimaryPlusNodeSwitch = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_switch_03_PMA')
        mc.connectAttr(firstAndSecondPrimaryPlusNode + '.output3D' , self.thirdPrimaryPlusNodeSwitch + '.input3D[0]')

        featherSixFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherSix_BCN')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherSixFKBlendNode + '.color1')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherSixFKBlendNode + '.color2')
        mc.connectAttr(featherSixFKBlendNode + '.output' , self.sixthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.sixthFeatherFK[0].zro + '.blend' , featherSixFKBlendNode + '.blender')

        featherSeventhFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherSeven_BCN')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherSeventhFKBlendNode + '.color2')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherSeventhFKBlendNode + '.color1')
        mc.connectAttr(featherSeventhFKBlendNode + '.output' , self.seventhFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.seventhFeatherFK[0].zro + '.blend' , featherSeventhFKBlendNode + '.blender')

        featherEighthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherEight_BCN')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherEighthFKBlendNode + '.color2')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherEighthFKBlendNode + '.color1')
        mc.connectAttr(featherEighthFKBlendNode + '.output' , self.eightFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.eightFeatherFK[0].zro + '.blend' , featherEighthFKBlendNode + '.blender')

        featherNinethFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherNine_BCN')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherNinethFKBlendNode + '.color2')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherNinethFKBlendNode + '.color1')
        mc.connectAttr(featherNinethFKBlendNode + '.output' , self.nineFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.nineFeatherFK[0].zro + '.blend' , featherNinethFKBlendNode + '.blender')

        feathertenthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherTen_BCN')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , feathertenthFKBlendNode + '.color2')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , feathertenthFKBlendNode + '.color1')
        mc.connectAttr(feathertenthFKBlendNode + '.output' , self.tenthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.tenthFeatherFK[0].zro + '.blend' , feathertenthFKBlendNode + '.blender')

        # connect third part feathers offset grps
        thirdPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_04_PMA')
        mc.connectAttr(self.thirdPrimaryCtl.name + '.rotate', thirdPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.thirdPrimaryCtl.zro + '.rotate', thirdPrimaryPlusNode + '.input3D[1]')


        fifthPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_05_PMA')
        mc.connectAttr(self.forthPrimaryCtl.zro + '.rotate', fifthPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.forthPrimaryCtl.name + '.rotate', fifthPrimaryPlusNode + '.input3D[1]')

        feathereleventhFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherEleven_BCN')
        mc.connectAttr(thirdPrimaryPlusNode + '.output3D' , feathereleventhFKBlendNode + '.color1')
        mc.connectAttr(fifthPrimaryPlusNode + '.output3D' , feathereleventhFKBlendNode + '.color2')
        mc.connectAttr(feathereleventhFKBlendNode + '.output' , self.eleventhFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.eleventhFeatherFK[0].zro + '.blend' , feathereleventhFKBlendNode + '.blender')

        featherTwelevethFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherTweleve_BCN')
        mc.connectAttr(thirdPrimaryPlusNode + '.output3D' , featherTwelevethFKBlendNode + '.color1')
        mc.connectAttr(fifthPrimaryPlusNode + '.output3D' , featherTwelevethFKBlendNode + '.color2')
        mc.connectAttr(featherTwelevethFKBlendNode + '.output' , self.twelvethFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.twelvethFeatherFK[0].zro + '.blend' , featherTwelevethFKBlendNode + '.blender')

        featherThirteenthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherThirteen_BCN')
        mc.connectAttr(thirdPrimaryPlusNode + '.output3D' , featherThirteenthFKBlendNode + '.color1')
        mc.connectAttr(fifthPrimaryPlusNode + '.output3D' , featherThirteenthFKBlendNode + '.color2')
        mc.connectAttr(featherThirteenthFKBlendNode + '.output' , self.thirteenthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.thirteenthFeatherFK[0].zro + '.blend' , featherThirteenthFKBlendNode + '.blender')

        featherForteenthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherForteen_BCN')
        mc.connectAttr(thirdPrimaryPlusNode + '.output3D' , featherForteenthFKBlendNode + '.color1')
        mc.connectAttr(fifthPrimaryPlusNode + '.output3D' , featherForteenthFKBlendNode + '.color2')
        mc.connectAttr(featherForteenthFKBlendNode + '.output' , self.forteenthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.forteenthFeatherFK[0].zro + '.blend' , featherForteenthFKBlendNode + '.blender')

        featherFifteenthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherFifteen_BCN')
        mc.connectAttr(thirdPrimaryPlusNode + '.output3D' , featherFifteenthFKBlendNode + '.color1')
        mc.connectAttr(fifthPrimaryPlusNode + '.output3D' , featherFifteenthFKBlendNode + '.color2')
        mc.connectAttr(featherFifteenthFKBlendNode + '.output' , self.fifteenthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.fifteenthFeatherFK[0].zro + '.blend' , featherFifteenthFKBlendNode + '.blender')





    def connect(self):

        super(WingFeather, self).connect()

        par = self.getOut('ctlParent')

        shoulderJnt = self.getOut('shoulderJnt')
        elbowJnt = self.getOut('elbowJnt')
        handJnt = self.getOut('handJnt')

        elbowFKCtl =  self.getOut('elbowFkCtl')
        handFkCtl = self.getOut('handFkCtl')

        armSettingCtl = self.getOut('armSettingCtl')

        handIkJnt = self.getOut('handIkJnt')
        elbowIkJnt = self.getOut('elbowIkJnt')

        attrLib.addInt(armSettingCtl, 'featherExtraCtls', min = 0, max = 1)



        firstShoulderTwistJnts = self.getOut('firstShoulderTwstParent')
        secondShoulderTwistJnts = self.getOut('secondShoulderTwstParent')
        thirdShoulderTwistJnts = self.getOut('thirdShoulderTwstParent')

        firstElbowTwistJnts = self.getOut('firstElbowTwstParent')
        secondElbowTwistJnts = self.getOut('secondElbowTwstParent')
        thirdElbowTwistJnts = self.getOut('thirdElbowTwstParent')

        startTwistShoulderCtlGrp = self.getOut('startTwistShoulderCtlGrp')
        midTwistShoulderCtlGrp = self.getOut('midTwistShoulderCtlGrp')
        endTwistShoulderCtlGrp = self.getOut('endTwistShoulderCtlGrp')

        startTwistElbowCtlGrp = self.getOut('startTwistElbowCtlGrp')
        midTwistElbowCtlGrp = self.getOut('midTwistElbowCtlGrp')
        endTwistElbowCtlGrp = self.getOut('endTwistElbowCtlGrp')

        startTwistShoulderCtl = self.getOut('startTwistShoulderCtlGrp')
        midTwistShoulderCtl = self.getOut('midTwistShoulderCtlGrp')
        endTwistShoulderCtl = self.getOut('endTwistShoulderCtlGrp')

        startTwistElbowCtl = self.getOut('startTwistElbowCtl')
        midTwistElbowCtl = self.getOut('midTwistElbowCtl')
        endTwistElbowCtl = self.getOut('endTwistElbowCtl')

        mc.pointConstraint(firstElbowTwistJnts, self.sixthFeatherFK[0].zro, mo = True)
        mc.pointConstraint(firstElbowTwistJnts,secondElbowTwistJnts, self.seventhFeatherFK[0].zro, mo = True)
        mc.pointConstraint(secondElbowTwistJnts, self.eightFeatherFK[0].zro, mo = True)
        mc.pointConstraint(secondElbowTwistJnts,thirdElbowTwistJnts, self.nineFeatherFK[0].zro, mo = True)
        mc.pointConstraint(thirdElbowTwistJnts, self.tenthFeatherFK[0].zro, mo = True)

        mc.pointConstraint(firstShoulderTwistJnts, self.firstFeatherFK[0].zro, mo = True)
        mc.pointConstraint(firstShoulderTwistJnts,secondShoulderTwistJnts, self.secondFeatherFK[0].zro, mo = True)
        mc.pointConstraint(secondShoulderTwistJnts, self.thirdFeatherFK[0].zro, mo = True)
        mc.pointConstraint(secondShoulderTwistJnts,thirdShoulderTwistJnts, self.forthFeatherFK[0].zro, mo = True)
        mc.pointConstraint(thirdShoulderTwistJnts, self.fifthFeatherFK[0].zro, mo = True)

        # connect arm control and attrs to our wing nodes
        handFKCtlPma = mc.createNode('plusMinusAverage', n = self.name + 'handCtl_PMA')
        mc.connectAttr(handFkCtl + '.rotate', handFKCtlPma + '.input3D[0]')

        handFKCtlCond = mc.createNode('condition', n = self.name + 'handCtl_COND')
        mc.connectAttr(handFKCtlPma + '.output3Dx', handFKCtlCond + '.colorIfTrueR')
        mc.connectAttr(handFKCtlPma + '.output3Dy', handFKCtlCond + '.colorIfTrueG')
        mc.connectAttr(handFKCtlPma + '.output3Dz', handFKCtlCond + '.colorIfTrueB')
        mc.connectAttr(armSettingCtl + '.fk_ik', handFKCtlCond + '.firstTerm')
        mc.connectAttr(handIkJnt + '.rotateX', handFKCtlCond + '.colorIfFalseR')
        mc.connectAttr(handIkJnt + '.rotateY', handFKCtlCond + '.colorIfFalseG')
        mc.connectAttr(handIkJnt + '.rotateZ', handFKCtlCond + '.colorIfFalseB')


        mc.connectAttr(handFKCtlCond + '.outColorR', self.thirdPrimaryPlusNodeSwitch  + '.input3D[1].input3Dx')
        mc.connectAttr(handFKCtlCond + '.outColorG', self.thirdPrimaryPlusNodeSwitch  + '.input3D[1].input3Dy')
        mc.connectAttr(handFKCtlCond + '.outColorB', self.thirdPrimaryPlusNodeSwitch  + '.input3D[1].input3Dz')

        elbowFKCtlPma = mc.createNode('plusMinusAverage', n = self.name + 'elbowCtl_PMA')
        mc.connectAttr(elbowFKCtl + '.rotate', elbowFKCtlPma + '.input3D[0]')

        elbowFKCtlCond = mc.createNode('condition', n = self.name + 'elbowCtl_COND')
        mc.connectAttr(elbowFKCtlPma + '.output3Dx', elbowFKCtlCond + '.colorIfTrueR')
        mc.connectAttr(elbowFKCtlPma + '.output3Dy', elbowFKCtlCond + '.colorIfTrueG')
        mc.connectAttr(elbowFKCtlPma + '.output3Dz', elbowFKCtlCond + '.colorIfTrueB')
        mc.connectAttr(armSettingCtl + '.fk_ik', elbowFKCtlCond + '.firstTerm')
        mc.connectAttr(elbowIkJnt + '.rotateX', elbowFKCtlCond + '.colorIfFalseR')
        mc.connectAttr(elbowIkJnt + '.rotateY', elbowFKCtlCond + '.colorIfFalseG')
        mc.connectAttr(elbowIkJnt + '.rotateZ', elbowFKCtlCond + '.colorIfFalseB')


        mc.connectAttr(elbowFKCtlCond + '.outColorR', self.secondPrimaryPlusNodeSwitch  + '.input3D[1].input3Dx')
        mc.connectAttr(elbowFKCtlCond + '.outColorG', self.secondPrimaryPlusNodeSwitch  + '.input3D[1].input3Dy')
        mc.connectAttr(elbowFKCtlCond + '.outColorB', self.secondPrimaryPlusNodeSwitch  + '.input3D[1].input3Dz')

        # connect arm joints to feather part
        mc.parentConstraint(shoulderJnt, self.firstFeatherPart, mo = True)

        mc.parentConstraint(elbowJnt, self.secondFeatherPart, mo = True)

        mc.parentConstraint(handJnt, self.thirdFeatherPart, mo = True)

        # connect twist controls
        mc.pointConstraint(startTwistShoulderCtl, endTwistShoulderCtl,midTwistShoulderCtlGrp, mo = True )
        mc.pointConstraint(startTwistElbowCtl, endTwistElbowCtl,midTwistElbowCtlGrp, mo = True )

        mc.pointConstraint(elbowJnt, endTwistShoulderCtlGrp, mo = True )
        mc.pointConstraint(handJnt, endTwistElbowCtlGrp, mo = True )

        # connect visibility of extra controls
        mc.connectAttr(armSettingCtl + '.featherExtraCtls', self.firstFeatherPart + '.visibility' )
        mc.connectAttr(armSettingCtl + '.featherExtraCtls', self.secondFeatherPart + '.visibility' )
        mc.connectAttr(armSettingCtl + '.featherExtraCtls', self.thirdFeatherPart + '.visibility' )

        mc.parentConstraint(shoulderJnt , self.primaryCtlOffsets[0] , mo = True )
        mc.parentConstraint(elbowJnt, self.primaryCtlOffsets[1] , mo = True )
        mc.parentConstraint(handJnt , self.primaryCtlOffsets[2], mo = True)




        if par:
            connect.matrix(par, self.ctlGrp, world=True)
            connect.matrix(par, self.moduleGrp, world=True)


        # posPar = self.getOut('posParent')
        # if posPar:
        #     connect.matrix(posPar, self.shoulderPosition['shoulderPosition'][0], world=True)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(WingFeather, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v=self.side + '_birdArm.handJnt')
        attrLib.addString(self.blueprintGrp, 'blu_posParent', v=self.side + '_birdArm.clavEnd')
        attrLib.addString(self.blueprintGrp, 'blu_firstShoulderTwstParent', v=self.side + '_birdArm.firstShoulderTwistJnts')
        attrLib.addString(self.blueprintGrp, 'blu_secondShoulderTwstParent', v=self.side + '_birdArm.secondShoulderTwistJnts')
        attrLib.addString(self.blueprintGrp, 'blu_thirdShoulderTwstParent', v=self.side + '_birdArm.thirdShoulderTwistJnts')
        attrLib.addString(self.blueprintGrp, 'blu_firstElbowTwstParent', v=self.side + '_birdArm.firstElbowTwistJnts')
        attrLib.addString(self.blueprintGrp, 'blu_secondElbowTwstParent', v=self.side + '_birdArm.secondElbowTwistJnts')
        attrLib.addString(self.blueprintGrp, 'blu_thirdElbowTwstParent', v=self.side + '_birdArm.thirdElbowTwistJnts')

        attrLib.addString(self.blueprintGrp, 'blu_elbowFkCtl', v=self.side + '_birdArm.elbowfkCtl')
        attrLib.addString(self.blueprintGrp, 'blu_handFkCtl', v=self.side + '_birdArm.handfkCtl')

        attrLib.addString(self.blueprintGrp, 'blu_armSettingCtl', v=self.side + '_birdArm.armSettingCtl')

        attrLib.addString(self.blueprintGrp, 'blu_handIkJnt', v=self.side + '_birdArm.handIkJnt')
        attrLib.addString(self.blueprintGrp, 'blu_elbowIkJnt', v=self.side + '_birdArm.elbowIkJnt')

        attrLib.addString(self.blueprintGrp, 'blu_shoulderJnt', v=self.side + '_birdArm.shoulderJnt')
        attrLib.addString(self.blueprintGrp, 'blu_elbowJnt', v=self.side + '_birdArm.elbowJnt')
        attrLib.addString(self.blueprintGrp, 'blu_handJnt', v=self.side + '_birdArm.handJnt')

        attrLib.addString(self.blueprintGrp, 'blu_startTwistShoulderCtlGrp', v=self.side + '_birdArm.startTwistShoulderCtlGrp')
        attrLib.addString(self.blueprintGrp, 'blu_midTwistShoulderCtlGrp', v=self.side + '_birdArm.midTwistShoulderCtlGrp')
        attrLib.addString(self.blueprintGrp, 'blu_endTwistShoulderCtlGrp', v=self.side + '_birdArm.endTwistShoulderCtlGrp')

        attrLib.addString(self.blueprintGrp, 'blu_startTwistElbowCtlGrp', v=self.side + '_birdArm.startTwistElbowCtlGrp')
        attrLib.addString(self.blueprintGrp, 'blu_midTwistElbowCtlGrp', v=self.side + '_birdArm.midTwistElbowCtlGrp')
        attrLib.addString(self.blueprintGrp, 'blu_endTwistElbowCtlGrp', v=self.side + '_birdArm.endTwistElbowCtlGrp')

        attrLib.addString(self.blueprintGrp, 'blu_startTwistShoulderCtl', v=self.side + '_birdArm.startTwistShoulderCtl')
        attrLib.addString(self.blueprintGrp, 'blu_midTwistShoulderCtl', v=self.side + '_birdArm.midTwistShoulderCtl')
        attrLib.addString(self.blueprintGrp, 'blu_endTwistShoulderCtl', v=self.side + '_birdArm.endTwistShoulderCtl')

        attrLib.addString(self.blueprintGrp, 'blu_startTwistElbowCtl', v=self.side + '_birdArm.startTwistElbowCtl')
        attrLib.addString(self.blueprintGrp, 'blu_midTwistElbowCtl', v=self.side + '_birdArm.midTwistElbowCtl')
        attrLib.addString(self.blueprintGrp, 'blu_endTwistElbowCtl', v=self.side + '_birdArm.endTwistElbowCtl')





        # attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts)
        # attrLib.addBool(self.blueprintGrp, 'blu_movable', v=self.movable)







