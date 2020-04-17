import maya.cmds as mc
import maya_tools.deformer_utilities.blendshape as but
reload(but)

def create_lambert(color):
    shader = mc.shadingNode("lambert", asShader=True)
    shading_group = mc.sets(renderable=True, noSurfaceShader=True, empty=True)
    mc.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
    mc.setAttr('%s.color' % shader, color[0], color[1], color[2], type='double3')
    mc.setAttr('%s.ambientColor' % shader, 0.75, 0.75, 0.75, type='double3')

    return shading_group


def create_duplicate_heads(head, index, names, namespace=None):
    bounding_box = mc.exactWorldBoundingBox(head)
    top = bounding_box[4]
    bottom = bounding_box[1]
    left = bounding_box[0]
    right = bounding_box[3]
    if right - left < 0.01:
        raise Exception('Mesh is too tiny!')
    x_spacing = 0.1
    y_spacing = 0.1
    x_position = (right - left + x_spacing)
    y_position = (top - bottom + y_spacing)
    blue_shader = create_lambert((0.4, 0.4, 0.9))

    for i, name in enumerate(names):

        old_neutral_head = '%s:neutral' % namespace
        existing_head_name = '%s:%s' % (namespace, name)

        if mc.objExists(existing_head_name):
            if mc.objExists(old_neutral_head):
                new_head = mc.duplicate(
                    old_neutral_head,
                    name=name
                )[0]
                blendshape = mc.blendShape(head, existing_head_name, new_head)[0]
                mc.setAttr('%s.w[0]' % blendshape, 1.0)
                mc.setAttr('%s.w[1]' % blendshape, 1.0)
                mc.delete(new_head, ch=True)

            else:
                new_head = mc.duplicate(
                    head,
                    name=name
                )[0]
                blendshape = mc.blendShape(existing_head_name, new_head)[0]
                mc.setAttr('%s.w[0]' % blendshape, 1.0)
                mc.delete(new_head, ch=True)
        else:
            new_head = mc.duplicate(
                head,
                name=name
            )[0]

        mc.setAttr(
            '%s.translate' % new_head,
            x_position*i,
            y_position*index,
            0.0,
            type='double3'
        )

        mc.setAttr(
            '%s.v' % new_head,
            True
        )
        mc.sets(new_head, e=True, forceElement=blue_shader)


def setup_targets(head, namespace=None):

    bounding_box = mc.exactWorldBoundingBox(head)
    top = bounding_box[4]
    bottom = bounding_box[1]
    left = bounding_box[0]
    right = bounding_box[3]
    if right - left < 0.01:
        raise Exception('Mesh is too tiny!')
    x_spacing = 0.1
    y_spacing = 0.1
    x_position = (right - left + x_spacing)
    y_position = (top - bottom + y_spacing)

    yellow_shader = create_lambert((0.9, 0.9, 0.4))
    red_shader = create_lambert((0.9, 0.4, 0.4))
    green_shader = create_lambert((0.4, 0.9, 0.4))
    blue_shader = create_lambert((0.4, 0.4, 0.9))

    mc.polyNormalPerVertex(head, ufn=True)
    mc.polySoftEdge(head, ch=False, a=0)

    target_names = [
        ['neutral'],
        ['down_lid_flare', 'down_lid_25', 'down_lid_50', 'down_lid_75', 'down_lid_100'],
        ['up_lid_flare', 'up_lid_25', 'up_lid_50', 'up_lid_75', 'up_lid_100'],
        ['brow_down_blink', 'brow_up', 'brow_down', 'brow_down_50', 'brow_down_blink_50', 'brow_up_blink'],
        ['brow_twist_in', 'mid_brow_in', 'brow_twist_out', 'brow_scale', 'in_brow_in'],
        ['mouth_down', 'mouth_back', 'smile', 'smile_lid_up', 'mouth_up', 'frown', 'squint'],
        ['pucker', 'pucker_left', 'pucker_right'],
        ['jaw_open', 'jaw_closed', 'spread', 'pinch', 'puff', 'suck', 'lid_corners_down', 'jaw_open_smile'],
        ['mouth_all_down', 'mouth_all_up', 'mouth_right', 'mouth_left', 'mouth_rotate_left', 'mouth_rotate_right'],
        ['squash_down', 'squash_up', 'jaw_left', 'jaw_right'],
        ['down_out_lip_roll', 'down_in_lip_roll', 'up_in_lip_roll', 'up_out_lip_roll'],
        ['nostril_up', 'nose_up']

    ]

    for i, x in enumerate(target_names):
        new_targets = create_duplicate_heads(
            head, i+1, x,
            namespace=namespace
        )

    mc.sets(*target_names[0], e=True, forceElement=green_shader)




    # Brow Regions

    source_head = mc.duplicate(
        head,
        name='brow_source'
    )[0]
    mc.setAttr('%s.translate' % source_head, x_position*10, y_position*-1, 0.0, type='double3')
    mc.sets(source_head, e=True, forceElement=red_shader)
    source_shape = mc.listRelatives(source_head, c=True, type='mesh')[0]
    mc.sets(source_head, e=True, forceElement=red_shader)

    regions_head = mc.duplicate(
        head,
        name='brow_regions'
    )[0]
    mc.setAttr('%s.translate' % regions_head, x_position*11, y_position*-1, 0.0, type='double3')
    mc.sets(regions_head, e=True, forceElement=blue_shader)
    regions_shape = mc.listRelatives(regions_head, c=True, type='mesh')[0]
    mc.connectAttr(
        '%s.outMesh' % regions_shape,
        '%s.inMesh' % source_shape
    )
    brow_targets_head = mc.duplicate(
        head,
        name='brow_targets'
    )[0]
    mc.setAttr('%s.translate' % brow_targets_head, x_position*12, y_position*-1, 0.0, type='double3')
    mc.sets(brow_targets_head, e=True, forceElement=green_shader)
    blendshape = mc.blendShape(
        ['brow_down', 'brow_up', 'brow_down_blink', 'brow_up_blink', 'up_lid_100',
         'down_lid_100'],
        brow_targets_head,
        name='brow_targets_bs'
    )[0]
    existing_blendshape = '%s:brow_targets_bs' % namespace
    if mc.objExists(existing_blendshape):
        transfer_blendshape_weights(
            existing_blendshape,
            blendshape
        )


    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 4, 'up_lid_25Shape', 0.25))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 4, 'up_lid_50Shape', 0.5))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 4, 'up_lid_75Shape', 0.75))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 4, 'up_lid_flare', -1.0))

    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 5, 'down_lid_25Shape', 0.25))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 5, 'down_lid_50Shape', 0.5))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 5, 'down_lid_75Shape', 0.75))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 5, 'down_lid_flare', -1.0))

    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 0, 'brow_down_50Shape', 0.5))
    mc.blendShape(blendshape, e=True, tc=0, ib=True, t=('brow_targetsShape', 2, 'brow_down_blink_50Shape', 0.5))

    region_meshs = []
    for i, region in enumerate(['neutral', 'in', 'mid', 'out']):
        region_head = mc.duplicate(
            head,
            name='brow_%s' % region
        )[0]
        mc.setAttr('%s.translate' % region_head, x_position*(12 + i + 1), y_position*-1, 0.0, type='double3')
        mc.sets(region_head, e=True, forceElement=yellow_shader)
        blendshape = mc.blendShape(brow_targets_head, region_head)[0]
        mc.setAttr('%s.w[0]' % blendshape, 1.0)

        region_meshs.append(region_head)

    blendshape = mc.blendShape(region_meshs, regions_head, name='brow_regions_bs')[0]

    existing_blendshape = '%s:brow_regions_bs' % namespace
    if mc.objExists(existing_blendshape):
        transfer_blendshape_weights(
            existing_blendshape,
            blendshape
        )

    mc.setAttr('%s.it[0].itg[0].nid' % blendshape, 1)
    mc.setAttr('%s.it[0].itg[1].nid' % blendshape, 1)
    mc.setAttr('%s.it[0].itg[2].nid' % blendshape, 1)
    mc.setAttr('%s.it[0].itg[3].nid' % blendshape, 1)

    mc.hide(region_meshs)




    # Lip Regions

    source_head = mc.duplicate(
        head,
        name='lip_source'
    )[0]

    mc.setAttr('%s.translate' % source_head, x_position * 10, y_position * -2, 0.0, type='double3')
    mc.sets(source_head, e=True, forceElement=red_shader)
    source_shape = mc.listRelatives(source_head, c=True, type='mesh')[0]

    vertical_regions_head = mc.duplicate(
        head,
        name='vertical_lip_regions'
    )[0]
    mc.setAttr('%s.translate' % vertical_regions_head, x_position * 11, y_position * -2, 0.0, type='double3')
    mc.sets(vertical_regions_head, e=True, forceElement=blue_shader)

    horizontal_regions_head = mc.duplicate(
        head,
        name='horizontal_lip_regions'
    )[0]

    mc.setAttr('%s.translate' % horizontal_regions_head, x_position * 12, y_position * -2, 0.0, type='double3')
    mc.sets(horizontal_regions_head, e=True, forceElement=blue_shader)

    regions_shape = mc.listRelatives(vertical_regions_head, c=True, type='mesh')[0]
    mc.connectAttr(
        '%s.outMesh' % regions_shape,
        '%s.inMesh' % source_shape
    )
    targets_head = mc.duplicate(
        head,
        name='lip_targets'
    )[0]
    mc.setAttr('%s.translate' % targets_head, x_position * 13, y_position * -2, 0.0, type='double3')
    mc.sets(targets_head, e=True, forceElement=green_shader)

    blendshape = mc.blendShape(
        [u'mouth_all_up', u'mouth_all_down'],
        targets_head,
        name='lip_targets_bs'
    )[0]

    region_meshs = []
    for i, region in enumerate(['neutral', 'mid', 'out']):
        region_mesh = mc.duplicate(
            targets_head,
            name='lip_%s' % region
        )[0]
        mc.setAttr('%s.translate' % region_mesh, x_position * (12 + i + 1), y_position * -2, 0.0, type='double3')

        mc.sets(region_mesh, e=True, forceElement=yellow_shader)
        region_meshs.append(region_mesh)
        blendshape = mc.blendShape(targets_head, region_mesh)[0]
        mc.setAttr('%s.w[0]' % blendshape, 1.0)

    blendshape = mc.blendShape(
        region_meshs,
        horizontal_regions_head,
        name='lip_horizontal_regions_bs'
    )[0]

    existing_blendshape = '%s:lip_horizontal_regions_bs' % namespace
    if mc.objExists(existing_blendshape):
        transfer_blendshape_weights(
            existing_blendshape,
            blendshape
        )

    mc.setAttr('%s.it[0].itg[0].nid' % blendshape, 1)
    mc.setAttr('%s.it[0].itg[1].nid' % blendshape, 1)
    mc.setAttr('%s.it[0].itg[2].nid' % blendshape, 1)
    mc.hide(region_meshs)


    region_meshs = []
    for i, region in enumerate(['up', 'down']):
        region_mesh = mc.duplicate(
            targets_head,
            name='lip_%s' % region
        )[0]
        mc.setAttr('%s.translate' % region_mesh, x_position * (12 + i + 1), y_position * -2, 0.0, type='double3')
        mc.sets(region_mesh, e=True, forceElement=yellow_shader)
        region_meshs.append(region_mesh)
        blendshape = mc.blendShape(horizontal_regions_head, region_mesh)[0]
        mc.setAttr('%s.w[0]' % blendshape, 1.0)

    blendshape = mc.blendShape(
        region_meshs,
        vertical_regions_head,
        name='lip_vertical_regions_bs'
    )[0]

    existing_blendshape = '%s:lip_vertical_regions_bs' % namespace
    if mc.objExists(existing_blendshape):
        transfer_blendshape_weights(
            existing_blendshape,
            blendshape
        )
    mc.setAttr('%s.it[0].itg[0].nid' % blendshape, 1)
    mc.setAttr('%s.it[0].itg[1].nid' % blendshape, 1)
    mc.hide(region_meshs)

def transfer_blendshape_weights(source, target):
    geometry = mc.blendShape(source, q=True, geometry=True)
    for i in range(len(geometry)):
        for g in range(len(mc.blendShape(source, q=True, t=True))):
            weights = but.get_target_weights(
                geometry[i],
                source,
                geo_index=i,
                target_shape_index=g
            )
            but.set_target_weights(
                target,
                geo_index=i,
                target_shape_index=g,
                weights_data=weights
            )
        base_weights = but.get_base_weights(
            source,
            geo_index=i,
        )

        but.set_base_weights(
            target,
            geo_index=i,
            weights_data=base_weights
        )