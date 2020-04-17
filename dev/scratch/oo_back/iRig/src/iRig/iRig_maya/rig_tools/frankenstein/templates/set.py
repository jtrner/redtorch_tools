import icon_api.utils as i_utils
import icon_api.attr as i_attr
import icon_api.constraint as i_constraint

from master import Template_Master


class Template_Set(Template_Master):

    def __init__(self):
        Template_Master.__init__(self)
        
        self.ctrl_size *= 10
        self.group_set_lighting = None

        self.create_geo_res_groups = False
        self.do_proxy_setup = False
        self.cleanup_all_attrs = True

        # Override some control settings
        # - Root
        self.root_ctrl_shape = "2D Square"
        # - Ground
        self.ground_ctrl_shape = "2D Square"
        # - COG
        self.cog_ctrl_shape = "2D Panel Square"
        self.cog_ctrl_color = "black"
        self.cog_ctrl_gimbal_color = "black"
        self.cog_ctrl_size_mult = 0.25

    def _post_bits(self):
        # Set Lighting Group (and constrain to control)
        self.group_set_lighting = self._group("SetLighting_Grp", self.group_main)
        i_constraint.constrain(self.cog_pack_obj.cog_ctrl.control, self.group_set_lighting, as_fn="parent")
        i_constraint.constrain(self.cog_pack_obj.cog_ctrl.control, self.group_set_lighting, as_fn="scale")
    
    def _cleanup(self):
        # UnLock and UnHide
        if i_utils.is_eav:
            for control in self.controls:
                i_attr.lock_and_hide(control, attrs=["t", "r"], unlock=True, unhide=True)
