import glob
import os
import requests
import zipfile
import imp
import shutil

irig_zip_address = 'http://bitbucket.icon.local:7990/rest/api/latest/projects/RIG/repos/irig/archive?format=zip'
deployment_location = 'G:/Rigging/.rigging/iRig'
EXTRA_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(EXTRA_DIR)


def main():
    deploy_current_version()
    copy_extra_to_deploy_root()


def deploy_current_version():
    version_directories = glob.glob('%s/iRig_*' % deployment_location)
    latest_file = max(
        version_directories,
        key=os.path.getctime
    )
    deployment_version = get_version_from_package()
    new_version_zip_path = '%s/iRig_%s.zip' % (deployment_location, deployment_version)
    new_version_directory = '%s/iRig_%s' % (deployment_location, deployment_version)
    os.makedirs(new_version_directory)
    download_url(irig_zip_address, new_version_zip_path)
    with zipfile.ZipFile(new_version_zip_path, 'r') as zip_ref:
        zip_ref.extractall(new_version_directory)
    print 'Deployed to : ', new_version_zip_path


def get_version_from_package():
    package_file = os.path.join(ROOT_DIR, 'src', 'iRig', 'package.py')
    package_module = imp.load_source('iRig_package', package_file)
    resolved_version = package_module.__dict__.get('__version__', '0.0.0')
    return resolved_version


def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def copy_extra_to_deploy_root():
    for extra_file in glob.glob(EXTRA_DIR + '/*'):
        if os.path.normpath(extra_file) == os.path.normpath(__file__):
            continue
        print "Copying:", extra_file, 'to', deployment_location
        shutil.copy(extra_file, deployment_location)


if __name__ == '__main__':
    main()
