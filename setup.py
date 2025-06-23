from pathlib import Path

from setuptools import setup
import os
import json

with open(os.path.join(Path(__file__).resolve().parent, 'info.json')) as info_file:
    try:
        data = json.load(info_file)
        version = data['version']
    except json.JSONDecodeError:
        version = '-0.0.1'
    except KeyError:
        version = '-0.0.2'

setup(version=version)
