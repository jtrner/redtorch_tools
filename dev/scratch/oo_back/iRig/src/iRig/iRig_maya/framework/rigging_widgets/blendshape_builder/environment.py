import os
import rigging_widgets.blendshape_builder

root_package_directory = os.path.dirname(blendshape_builder.__file__.replace('\\', '/'))
images_directory = '%s/static/images' % root_package_directory
