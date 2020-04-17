import os
ft = None
try:
    import fileTools.default as ft
except:
    pass
import glob


def get_rig_blueprints_directory(user=None):
    if ft:
        return '%s/%s/rig_blueprint' % (
            ft.ez.path('workrig').replace('\\', '/'),
            user if user else os.getenv('USER')
        )


def get_face_blueprints_directory(user=None):
    if ft:
        return '%s/%s/face_blueprint' % (
            ft.ez.path('workrig').replace('\\', '/'),
            user if user else os.getenv('USER')
        )


def get_product_rig_blueprints_directory():
    if ft:
        return '%s/rig_blueprint' % ft.ez.path('products').replace('\\', '/')


def get_product_face_blueprints_directory():
    if ft:
        return '%s/face_blueprint' % ft.ez.path('products').replace('\\', '/')


def get_abc_directory():
    if ft:
        return '%s/abc' % ft.ez.path('products').replace('\\', '/')


def get_latest_abc():
    if ft:
        abc_directory = get_abc_directory()
        if os.path.exists(abc_directory):
            list_of_files = glob.glob('%s/*.abc' % abc_directory)
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                return latest_file


def get_latest_user_rig_blueprint():
    rig_blueprints_directory = get_rig_blueprints_directory()
    if os.path.exists(rig_blueprints_directory):
        list_of_files = glob.glob('%s/*rig_blueprint*.json' % rig_blueprints_directory)
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            return latest_file


def get_latest_rig_blueprint():
    work_directory = ft.ez.path('workrig').replace('\\', '/')
    latest_user_blueprints = []
    #print 'work directory --> ', work_directory
    for item in os.listdir(work_directory):
        item_path = '%s/%s' % (work_directory, item)
        if os.path.isdir(item_path):
            user = item
            rig_blueprints_directory = get_rig_blueprints_directory(user=user)
            #print 'Checking directory -->> ', rig_blueprints_directory
            if os.path.exists(rig_blueprints_directory):
                list_of_files = glob.glob('%s/*rig_blueprint*.json' % rig_blueprints_directory)
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    #print 'Bluepring found ---> ', latest_file
                    latest_user_blueprints.append(latest_file)
                #else:
                #    print 'No blueprint found...'

    if latest_user_blueprints:
        return max(latest_user_blueprints, key=os.path.getctime)


def get_latest_user_face_blueprint():
    face_blueprints_directory = get_face_blueprints_directory()
    if os.path.exists(face_blueprints_directory):
        list_of_files = glob.glob('%s/*face_blueprint*.json' % face_blueprints_directory)
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            return latest_file


def get_latest_face_blueprint():
    work_directory = ft.ez.path('workrig').replace('\\', '/')
    latest_user_blueprints = []
    for item in os.listdir(work_directory):
        item_path = '%s/%s' % (work_directory, item)
        if os.path.isdir(item_path):
            user = item
            face_blueprints_directory = get_face_blueprints_directory(user=user)
            if os.path.exists(face_blueprints_directory):
                list_of_files = glob.glob('%s/*face_blueprint*.json' % face_blueprints_directory)
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    latest_user_blueprints.append(latest_file)
                    print 'Framework Found -->>  : ', latest_file

    if latest_user_blueprints:
        return max(latest_user_blueprints, key=os.path.getctime)


def get_latest_rig_product_blueprint():
    if ft:
        rig_blueprints_directory = get_product_rig_blueprints_directory()
        if os.path.exists(rig_blueprints_directory):
            list_of_files = glob.glob('%s/*.json' % rig_blueprints_directory)
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                return latest_file


def get_latest_face_product_blueprint():
    if ft:
        face_blueprints_directory = get_product_face_blueprints_directory()
        if os.path.exists(face_blueprints_directory):
            list_of_files = glob.glob('%s/*.json' % face_blueprints_directory)
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                return latest_file


def find_latest_rig_blueprint():
    if ft:
        latest_blueprint = get_latest_rig_blueprint()
        latest_product_blueprint = get_latest_rig_product_blueprint()
        if latest_blueprint and latest_product_blueprint:
            return max([latest_blueprint, latest_product_blueprint], key=os.path.getctime).replace('\\', '/')
        elif latest_blueprint:
            return latest_blueprint.replace('\\', '/')
        elif latest_product_blueprint:
            return latest_product_blueprint.replace('\\', '/')


def find_latest_face_blueprint():
    if ft:
        latest_blueprint = get_latest_face_blueprint()
        latest_product_blueprint = get_latest_face_product_blueprint()
        if latest_blueprint and latest_product_blueprint:
            return max([latest_blueprint, latest_product_blueprint], key=os.path.getctime).replace('\\', '/')
        elif latest_blueprint:
            return latest_blueprint.replace('\\', '/')
        elif latest_product_blueprint:
            return latest_product_blueprint.replace('\\', '/')
