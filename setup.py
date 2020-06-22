import setuptools
import json
import os

from os import path
this_directory = path.abspath(path.dirname(__file__))

# read the contents of README file
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

if 'GIT_DESCRIBE_TAG' in os.environ:
    version = os.environ['GIT_DESCRIBE_TAG']
else:
    version='0.0.0.dev0'

setuptools.setup(
    name="conda-dependencies",
    version=version,
    url="https://github.com/raydouglass/conda-dependencies",
    author="Ray Douglass",
    author_email='ray@raydouglass.com',
    description="Tool to visualize conda dependencies",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="Apache",
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'conda-dependencies = conda_dependencies:main',
        ],
    }
)