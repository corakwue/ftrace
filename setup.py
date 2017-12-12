import os
import sys
import warnings
from itertools import chain

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

ftrace_dir = os.path.join(os.path.dirname(__file__), 'ftrace')

# happends if falling back to distutils
warnings.filterwarnings('ignore', "Unknown distribution option: 'install_requires'")
warnings.filterwarnings('ignore', "Unknown distribution option: 'extras_require'")

packages = []
data_files = {}
source_dir = os.path.dirname(__file__)
for root, dirs, files in os.walk(ftrace_dir):
    rel_dir = os.path.relpath(root, source_dir)
    data = []
    if '__init__.py' in files:
        for f in files:
            if os.path.splitext(f)[1] not in ['.py', '.pyc', '.pyo']:
                data.append(f)
        package_name = rel_dir.replace(os.sep, '.')
        package_dir = root
        packages.append(package_name)
        data_files[package_name] = data
    else:
        # use previous package name
        filepaths = [os.path.join(root, f) for f in files]
        data_files[package_name].extend([os.path.relpath(f, package_dir) for f in filepaths])

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

KEYWORDS = 'linux ftrace parser library'

setup(
    name='ftrace',
    version='1.0.0',
    description='Linux ftrace parser library.',
    author='Chuk Orakwue',
    author_email='chukwuchebem.orakwue@gmail.com',
    url='https://github.com/corakwue/ftrace/',
    download_url='https://github.com/corakwue/ftrace/',
    maintainer='Chuk Orakwue',
    maintainer_email='chukwuchebem.orakwue@gmail.com',
    packages=packages,
    platforms=['Platform Independent'],
    license='Apache v2',
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    install_requires=['logbook', 'pandas'],
)