from rig_math.vector import Vector


class SourceCodeFactory(object):
    def __init__(self):
        super(SourceCodeFactory, self).__init__()
        self.import_lines = []
        self.body_lines = []
        self.nodes = dict()

    def add_node(self, node):
        if isinstance(node, nob.DependNode):
            self.nodes[node.uuid] = node
            class_name = node.__class__.__name__
            import_line = 'from %s import %s' % (node.__class__.__module__, class_name)
            if import_line not in self.import_lines:
                self.import_lines.append(import_line)

            body_line = '%s = controller.create_object(\n    %s,\n' % (node.name, class_name)
            for key in ['root_name', 'side', 'index', 'size', 'node_type']:
                value = getattr(node, key)
                if isinstance(value, basestring):
                    value = "'%s'" % value
                if value is not None:
                    body_line += '    %s=%s,\n' % (key, value)
            if node.parent:
                body_line += '    parent=%s\n' % node.parent.name

            body_line += ')'
            self.body_lines.append(body_line)
            for child in node.children:
                self.add_node(child)

    def generate_source_code(self, node):
        self.import_lines = []
        self.body_lines = []
        self.nodes = dict()
        self.import_lines.append('from face_factory.controllers.face_rig_controller import FaceRigController')
        self.body_lines.append('controller = FaceRigController.get_controller()\n')
        self.add_node(node)

        source_code = '\n'.join(self.import_lines)
        source_code += '\n\n'
        source_code += '\n'.join(self.body_lines)
        return source_code

def view_source_code(node):
    code_factory = SourceCodeFactory()
    file_name = '%s/source_code.py' % os.path.expanduser('~')
    with open(file_name, mode='w') as f:
        f.write(code_factory.generate_source_code(node))
    os.system('start %s' % file_name)

