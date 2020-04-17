import icon_api.attr as i_attr

from rig_tools.frankenstein.core.master import Build_Master


class Build_Code(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # Variables to change
        self.script_author = None
        self.ui_execute_option = None
        self.exec_file_path = None
        self.exec_script = None

        # Set the pack info
        self.side = ""
        self.description = "Py"
        self.length = 0
        self.length_min = 0
        self.length_max = 0
        self.base_joint_positions = [[0, 0, 0]]

    def _create_bit(self):
        # Add information to info node
        i_attr.create(node=self.pack_info_node, ln="script_author", dt="string", l=True, dv=self.script_author)
        i_attr.create(node=self.pack_info_node, ln="execute_option", at="enum", l=True, en="File:Snippet:", 
                      dv=["File", "Snippet"].index(self.ui_execute_option))
        i_attr.create(node=self.pack_info_node, ln="execute_file_path", dt="string", l=True, dv=self.exec_file_path)
        i_attr.create(node=self.pack_info_node, ln="execute_script", dt="string", l=True, dv=self.exec_script)

