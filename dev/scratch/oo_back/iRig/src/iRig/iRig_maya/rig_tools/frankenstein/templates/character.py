from master import Template_Master

import rig_tools.frankenstein.character.face as rig_face


class Template_Character(Template_Master):
    def __init__(self):
        Template_Master.__init__(self)
        
        self.ctrl_size *= 0.5
        self.with_face = False
        
        self.pack_options = ["Cog", "Face"]

    def _class_prompts(self):
        self.prompt_info["with_face"] = {"type": "checkBox", "value": self.with_face}
    
    def _add_packs(self):
        Template_Master._add_packs(self)

        # Face
        if self.with_face:
            self.packs.append(rig_face.Build_Face)
    
    def _stitch_packs(self):
        # Vars
        cog_build = self.pack_objects.get("COG")
        head_build = self.pack_objects.get("Head")
        face_build = self.pack_objects.get("Face")

        # Face
        self._do_stitch_packs(driven_obj=face_build, driver_objs=[head_build, cog_build], do_parenting=False)

    def _post_bits(self):
        # Additional connections
        if self.cog_pack_obj.scale_md:  # Cog built (as opposed to specified bits only being built)
            self.cog_pack_obj.scale_md.output.drive(self.group_jnt.s)
