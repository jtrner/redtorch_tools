import bpy


def constrain_one_to_many(driver, drivens):
    """
    driver = bpy.data.objects['Empty']
    drivens = [x for x in bpy.data.objects if  x.name.startswith('Cu')]
    constrain_one_to_many(driver, drivens)
    """
    for driven in drivens:
        bpy.context.view_layer.objects.active = driven
        #bpy.context.object.hide_viewport = False
        #bpy.context.object.hide_render = False
        bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
        bpy.context.object.constraints["Copy Transforms"].target = driver
