import os
import glob
import shutil
import rig_factory.build.build as brg
ft = None
try:
    import fileTools.default as ft
except StandardError:
    print 'WARNING: unable to find file_tools'


def file_tools(func):
    def run_if_file_tools_exists(*args, **kwargs):
        if ft:
            return func(*args, **kwargs)
    return run_if_file_tools_exists


@file_tools
def get_scene_cache_directory():
    return '%s/scene_cache' % ft.ez.path('elems').replace('\\', '/')


@file_tools
def get_abc_directory():
    if ft:
        return '%s/abc' % ft.ez.path('products').replace('\\', '/')


@file_tools
def get_latest_abc():
    if ft:
        abc_directory = get_abc_directory()
        if os.path.exists(abc_directory):
            list_of_files = glob.glob('%s/*.abc' % abc_directory)
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                return latest_file


@file_tools
def get_rig_data_directory():
    return '%s/rig_data' % ft.ez.path('elems').replace('\\', '/')


@file_tools
def get_base_directory():
    return ft.ez.path('base').replace('\\', '/')


@file_tools
def get_work_directory():
    return ft.ez.path('work_dir').replace('\\', '/')


@file_tools
def get_rig_directory():
    return ft.ez.path('workrig').replace('\\', '/')


def get_build_script_path():
    return '%s/build.py' % get_user_build_directory()


@file_tools
def get_standard_build_script_path():
    return brg.__file__.replace('\\', '/').replace('.pyc', '.py')


@file_tools
def get_user_wip_directory():
    return ft.ez.path('wip').replace('\\', '/')


@file_tools
def get_user_build_directory():
    return '%s/build' % get_user_wip_directory()


@file_tools
def get_auto_build_directory():
    return '%s/legacy_build' % get_user_wip_directory()


@file_tools
def get_user_rig_blueprint_path():
    return '%s/rig_blueprint.json' % get_user_build_directory()


@file_tools
def get_user_face_blueprint_path():
    return '%s/face_blueprint.json' % get_user_build_directory()


@file_tools
def get_user_build_versions_directory():
    return '%s/build_versions' % get_user_wip_directory()


def backup_build_directory(directory_name):
    build_version_path = '%s/%s' % (get_user_build_versions_directory(), directory_name)
    if os.path.exists(build_version_path):
        shutil.rmtree(build_version_path)
    shutil.copytree(
        get_user_build_directory(),
        build_version_path
    )


def get_latest_build_directory():
    work_directory = ft.ez.path('workrig').replace('\\', '/')
    build_directories = []
    for item in os.listdir(work_directory):
        item_path = '%s/%s/build' % (work_directory, item)
        if os.path.exists(item_path) and os.path.isdir(item_path):
            build_directories.append(item_path)
    if build_directories:
        return max(build_directories, key=os.path.getctime)


def initialize_build_directory(controller):
    build_directory = get_user_build_directory()
    latest_build_directory = get_latest_build_directory()
    if not os.path.exists(build_directory) and latest_build_directory:
        controller.build_directory = latest_build_directory
    else:
        controller.build_directory = build_directory


def assemble_legacy_build(controller):
    auto_build_directory = get_auto_build_directory()
    if os.path.exists(auto_build_directory):
        shutil.rmtree(auto_build_directory)
    os.makedirs(auto_build_directory)

    old_rig_blueprint_path = legacy_find_latest_rig_blueprint()
    new_rig_blueprint_path = '%s/rig_blueprint.json' % auto_build_directory
    if old_rig_blueprint_path and os.path.exists(old_rig_blueprint_path):
        shutil.copyfile(
            old_rig_blueprint_path,
            new_rig_blueprint_path
        )
        controller.raise_warning(
            'Rig blueprint copied from:\n%s' % (
                old_rig_blueprint_path,
            )
        )

    #  Copy face blueprint

    old_face_blueprint_path = legacy_find_latest_face_blueprint()
    new_face_blueprint_path = '%s/face_blueprint.json' % auto_build_directory
    if old_face_blueprint_path and os.path.exists(old_face_blueprint_path):
        shutil.copyfile(
            old_face_blueprint_path,
            new_face_blueprint_path
        )
        controller.raise_warning(
            'Face blueprint copied from:\n%s' % (
                old_face_blueprint_path,
            )
        )

        old_face_abc_path = old_face_blueprint_path.replace('.json', '.abc')
        new_face_abc_path = '%s/face_blueprint.abc' % auto_build_directory

        if os.path.exists(old_face_abc_path):
            shutil.copyfile(
                old_face_abc_path,
                new_face_abc_path
            )
            controller.raise_warning(
                'Face abc file copied from:\n%s' % (
                    old_face_abc_path,
                )
            )

    #  Copy build script
    build_script_path = '%s/build.py' % auto_build_directory
    standard_build_script_path = get_standard_build_script_path()
    if not os.path.exists(build_script_path):
        shutil.copyfile(
            standard_build_script_path,
            build_script_path
        )

    #  Copy post/finalize scripts

    rig_data_directory = get_rig_data_directory()
    old_post_scripts_directory = '%s/post_scripts' % rig_data_directory
    old_finalize_scripts_directory = '%s/finalize_scripts' % rig_data_directory
    new_post_scripts_directory = '%s/post_scripts' % auto_build_directory
    new_finalize_scripts_directory = '%s/finalize_scripts' % auto_build_directory
    if os.path.exists(old_post_scripts_directory) and not os.path.exists(new_finalize_scripts_directory):
        shutil.copytree(
            old_post_scripts_directory,
            new_post_scripts_directory
        )
    if os.path.exists(old_finalize_scripts_directory):
        shutil.copytree(
            old_finalize_scripts_directory,
            new_finalize_scripts_directory
        )
    controller.build_directory = auto_build_directory

def legacy_get_latest_user_blueprint():
    work_directory = ft.ez.path('workrig').replace('\\', '/')
    latest_user_blueprints = []
    for item in os.listdir(work_directory):
        item_path = '%s/%s' % (work_directory, item)
        if os.path.isdir(item_path):
            user = item
            rig_blueprints_directory = legacy_get_rig_blueprints_directory(user=user)
            if os.path.exists(rig_blueprints_directory):
                list_of_files = glob.glob('%s/*rig_blueprint*.json' % rig_blueprints_directory)
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    latest_user_blueprints.append(latest_file)

    if latest_user_blueprints:
        return max(latest_user_blueprints, key=os.path.getctime)


def legacy_get_rig_blueprints_directory(user=None):
    if ft:
        return '%s/%s/rig_blueprint' % (
            ft.ez.path('workrig').replace('\\', '/'),
            user if user else os.getenv('USER')
        )


def legacy_get_face_blueprints_directory(user=None):
    if ft:
        return '%s/%s/face_blueprint' % (
            ft.ez.path('workrig').replace('\\', '/'),
            user if user else os.getenv('USER')
        )


def legacy_get_product_rig_blueprints_directory():
    if ft:
        return '%s/rig_blueprint' % ft.ez.path('products').replace('\\', '/')


def legacy_get_product_face_blueprints_directory():
    if ft:
        return '%s/face_blueprint' % ft.ez.path('products').replace('\\', '/')


def legacy_get_latest_user_rig_blueprint():
    rig_blueprints_directory = legacy_get_rig_blueprints_directory()
    if os.path.exists(rig_blueprints_directory):
        list_of_files = glob.glob('%s/*rig_blueprint*.json' % rig_blueprints_directory)
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            return latest_file


def legacy_get_latest_rig_blueprint():
    work_directory = ft.ez.path('workrig').replace('\\', '/')
    latest_user_blueprints = []
    for item in os.listdir(work_directory):
        item_path = '%s/%s' % (work_directory, item)
        if os.path.isdir(item_path):
            user = item
            rig_blueprints_directory = legacy_get_rig_blueprints_directory(user=user)
            if os.path.exists(rig_blueprints_directory):
                list_of_files = glob.glob('%s/*rig_blueprint*.json' % rig_blueprints_directory)
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    latest_user_blueprints.append(latest_file)


    if latest_user_blueprints:
        return max(latest_user_blueprints, key=os.path.getctime)


def legacy_get_latest_user_face_blueprint():
    face_blueprints_directory = legacy_get_face_blueprints_directory()
    if os.path.exists(face_blueprints_directory):
        list_of_files = glob.glob('%s/*face_blueprint*.json' % face_blueprints_directory)
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            return latest_file


def legacy_get_latest_face_blueprint():
    work_directory = ft.ez.path('workrig').replace('\\', '/')
    latest_user_blueprints = []
    for item in os.listdir(work_directory):
        item_path = '%s/%s' % (work_directory, item)
        if os.path.isdir(item_path):
            user = item
            face_blueprints_directory = legacy_get_face_blueprints_directory(user=user)
            if os.path.exists(face_blueprints_directory):
                list_of_files = glob.glob('%s/*face_blueprint*.json' % face_blueprints_directory)
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    latest_user_blueprints.append(latest_file)

    if latest_user_blueprints:
        return max(latest_user_blueprints, key=os.path.getctime)


def legacy_get_latest_rig_product_blueprint():
    if ft:
        rig_blueprints_directory = legacy_get_product_rig_blueprints_directory()
        if os.path.exists(rig_blueprints_directory):
            list_of_files = glob.glob('%s/*.json' % rig_blueprints_directory)
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                return latest_file


def legacy_get_latest_face_product_blueprint():
    if ft:
        face_blueprints_directory = legacy_get_product_face_blueprints_directory()
        if os.path.exists(face_blueprints_directory):
            list_of_files = glob.glob('%s/*.json' % face_blueprints_directory)
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                return latest_file


def legacy_find_latest_rig_blueprint():
    if ft:
        latest_blueprint = legacy_get_latest_rig_blueprint()
        latest_product_blueprint = legacy_get_latest_rig_product_blueprint()
        if latest_blueprint and latest_product_blueprint:
            return max([latest_blueprint, latest_product_blueprint], key=os.path.getctime).replace('\\', '/')
        elif latest_blueprint:
            return latest_blueprint.replace('\\', '/')
        elif latest_product_blueprint:
            return latest_product_blueprint.replace('\\', '/')


def legacy_find_latest_face_blueprint():
    if ft:
        latest_blueprint = legacy_get_latest_face_blueprint()
        latest_product_blueprint = legacy_get_latest_face_product_blueprint()
        if latest_blueprint and latest_product_blueprint:
            return max([latest_blueprint, latest_product_blueprint], key=os.path.getctime).replace('\\', '/')
        elif latest_blueprint:
            return latest_blueprint.replace('\\', '/')
        elif latest_product_blueprint:
            return latest_product_blueprint.replace('\\', '/')
