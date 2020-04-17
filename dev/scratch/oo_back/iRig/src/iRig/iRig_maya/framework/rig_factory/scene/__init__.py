
"""
!! This should be in rig_controller.scene to reduce dependencies
"""


def get_scene(standalone=False, mock=False):
    if mock:
        from rig_factory.scene.mock_scene import MockScene
        return MockScene()
    elif standalone:
        from rig_factory.scene.maya_scene import MayaScene
        import maya.standalone
        maya.standalone.initialize(name='python')
        scene = MayaScene()
        #maya_version = float(mc.about(version=True))

        load_plugins(scene)
        scene.standalone = True

        return scene
    else:
        from rig_factory.scene.maya_scene import MayaScene
        scene = MayaScene()
        load_plugins(scene)
        return scene


def load_plugins(scene):
    for plugin in ['matrixNodes', 'quatNodes', 'shard_matrix']:
        try:
            scene.loadPlugin(plugin)
        except Exception, e:
            print e.message