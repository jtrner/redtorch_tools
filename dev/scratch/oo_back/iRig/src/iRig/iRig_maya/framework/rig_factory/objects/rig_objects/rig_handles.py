from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle


class LocalHandle(GimbalHandle):

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LocalHandle, cls).create(controller, **kwargs)
        if this.side in ['left', 'right']:
            this.mirror_plugs = ['translateX', 'translateY', 'translateZ']
        elif this.side == 'center':
            this.mirror_plugs = ['translateX', 'rotateZ', 'rotateY']
        return this


class WorldHandle(GimbalHandle):

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(WorldHandle, cls).create(controller, **kwargs)
        if this.side in ['left', 'right']:
            this.mirror_plugs = ['translateX', 'rotateZ']
        elif this.side == 'center':
            this.mirror_plugs = ['translateX', 'rotateZ']
        return this


class CogHandle(GimbalHandle):

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(CogHandle, cls).create(controller, **kwargs)
        if this.side == 'center':
            this.mirror_plugs = ['rotateZ']
        return this
