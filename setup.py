from setuptools import setup
import os

with open(os.path.join('ndr_core', 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(version=version)
