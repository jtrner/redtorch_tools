"""
ICON Creative Studio
    Template setup.py for building and distributing python packages

For more information see:
    https://packaging.python.org/guides/distributing-packages-using-setuptools/
    https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
import os
import imp
from glob import glob
from setuptools import setup, find_packages

about = {
    '__title__': 'Test',
    '__version__': '0.0.0',
    '__comment__': None,  # '0.0.0: No comment',
    '__description__': None,  # 'No description available'
}

def update_about():
    """
    This expects to find a file named: package.py which contains
    information about the Python distribution build
    """
    global about
    here = os.path.abspath(os.path.dirname(__file__))
    package_file_list = glob(here + '/src/*/package.py')
    try:
        package_file_list.reverse()
        package_file = package_file_list.pop()  # Gets the first found package.py file
        package_source = imp.load_source('package_details', package_file)
        about.update(package_source.__dict__)
    except (IndexError, ImportError) as e:
        pass

update_about()

setup(
    name=about.get('__title__', 'testing'),
    version=about.get('__version__', '0.0.0'),  # Required
    description=about.get('__description__', about.get('__comment__', 'No description available')),
    packages=find_packages('src'),  # Required
    package_dir={'': 'src'},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,  # Required when using non-py contents (specified in MANIFEST.in)
    python_requires='>=2.7, <3',  # Required - Studio uses Python 2.7
    install_requires=[],  # Optional when there are dependencies on 3rd party modules/packages
)
