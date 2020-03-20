from rig_factory.utilities.blueprint_utilities import BlueprintIterator
from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs
obs.register_classes()


path = 'Y:/RCL/assets/type/Vehicle/Ship_Starbug_A/products/rig_blueprint/Ship_Starbug_A_rig_blueprint_v0027.json'
controller = RigController.get_controller(mock=True)
blueprint = BlueprintIterator(path)

container_kwargs = blueprint.next()


container = controller.create_object(
    container_kwargs['klass'],
    **container_kwargs
)

all_parts = []
for kwargs in blueprint:
    owner = controller.named_objects[kwargs.pop('owner')]
    part = owner.create_part(
        kwargs['klass'],
        **kwargs
    )
    all_parts.append(part)

container.create_shaders()

container.create_groups()

for path in container_kwargs.get('geometry_paths', []):
    container.import_geometry(path)

for path in container_kwargs.get('utility_geometry_paths', []):
    container.import_utility_geometry(path)

container.create_origin_geometry()

container.set_parent_joints_by_index(container_kwargs['parent_joint_indices'])

container.create_deformation_rig(**container_kwargs)

container.set_shard_skin_cluster_data(
    container_kwargs.get(
        'shard_skin_cluster_data',
        dict()
    )
)
container.build_skin_clusters(
    container_kwargs.get(
        'skin_clusters',
        None
    )
)
container.set_delta_mush_data(
    container_kwargs.get(
        'delta_mush',
        None
    )
)
container.set_wrap_data(
    container_kwargs.get(
        'wrap',
        None
    )
)

for part in all_parts:
    part.post_create()

container.post_create()

for part in all_parts:
    part.finalize()

container.finalize()