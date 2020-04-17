from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty


class Constraint(Transform):

    transform = ObjectProperty(
        name='transform'
    )

    targets = ObjectListProperty(
        name='targets'
    )

    create_kwargs = DataProperty(
        name='create_kwargs'
    )

    @classmethod
    def create(cls, controller, *args, **kwargs):
        root_name = '_'.join([x.get_selection_string() for x in args])
        parent = kwargs.pop('parent', args[-1])
        kwargs['create_kwargs'] = dict(kwargs)
        kwargs['parent'] = parent
        kwargs['root_name'] = root_name
        kwargs['targets'] = args[0:-1]
        kwargs['transform'] = args[-1]
        this = super(Constraint, cls).create(controller, **kwargs)
        return this

    def __init__(self, **kwargs):
        super(Constraint, self).__init__(**kwargs)

    def create_in_scene(self):
        transforms = list(self.targets)
        transforms.append(self.transform)
        self.m_object = self.controller.scene.create_constraint(
            self.node_type,
            name=self.name,
            parent=self.parent.m_object,
            *[x.m_object for x in transforms],
            **self.create_kwargs
        )


class ParentConstraint(Constraint):
    def __init__(self, **kwargs):
        super(ParentConstraint, self).__init__(**kwargs)
        self.node_type = 'parentConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You StandardError use "Transform" as arguments when you create a "%s"' % cls.__name__
            )
        return super(ParentConstraint, cls).create(controller, *args, **kwargs)


class PointConstraint(Constraint):

    def __init__(self, **kwargs):
        super(PointConstraint, self).__init__(**kwargs)
        self.node_type = 'pointConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You StandardError use "Transform" as arguments when you create a "%s"' % cls.__name__
            )
        return super(PointConstraint, cls).create(controller, *args, **kwargs)


class ScaleConstraint(Constraint):

    def __init__(self, **kwargs):
        super(ScaleConstraint, self).__init__(**kwargs)
        self.node_type = 'scaleConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You StandardError use "Transform" as arguments when you create a "%s"' % cls.__name__
            )
        return super(ScaleConstraint, cls).create(controller, *args, **kwargs)


class AimConstraint(Constraint):

    world_up_object = ObjectProperty(
        name='world_up_object'
    )

    def __init__(self, **kwargs):
        super(AimConstraint, self).__init__(**kwargs)
        self.node_type = 'aimConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        up_object = kwargs.pop('worldUpObject', None)
        if up_object:
            kwargs['worldUpObject'] = str(up_object)
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You StandardError use "Transform" as arguments when you create a "%s"' % cls.__name__
            )
        return super(AimConstraint, cls).create(controller, *args, **kwargs)


class OrientConstraint(Constraint):

    def __init__(self, **kwargs):
        super(OrientConstraint, self).__init__(**kwargs)
        self.node_type = 'orientConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You StandardError use "Transform" as arguments when you create a "%s"' % cls.__name__
            )
        return super(OrientConstraint, cls).create(controller, *args, **kwargs)


class PoleVectorConstraint(Constraint):

    def __init__(self, **kwargs):
        super(PoleVectorConstraint, self).__init__(**kwargs)
        self.node_type = 'poleVectorConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You StandardError use "Transform" as arguments when you create a "%s"' % cls.__name__
            )
        return super(PoleVectorConstraint, cls).create(controller, *args, **kwargs)


class TangentConstraint(Constraint):

    def __init__(self, **kwargs):
        super(TangentConstraint, self).__init__(**kwargs)
        self.node_type = 'tangentConstraint'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) < 2:
            raise StandardError(
                'Cannot make %s with less than 2 objects passed arguments' % cls.__name__
            )
        if len(args) > 2:
            raise StandardError(
                'Cannot make %s with more than 2 objects passed arguments' % cls.__name__
            )
        if not isinstance(args[0], NurbsCurve):
            raise Exception(
                'You StandardError use "NurbsCurve" as first argument when you create a "%s"' % cls.__name__
            )
        if not isinstance(args[1], Transform):
            raise Exception(
                'You StandardError use "Transform" as second argument when you create a "%s"' % cls.__name__
            )
        return super(TangentConstraint, cls).create(controller, *args, **kwargs)

