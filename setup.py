from pathlib import Path

from setuptools import setup

version_file = Path(__file__).resolve().parent / 'ndr_core' / 'VERSION'
try:
    version = version_file.read_text().strip()
except FileNotFoundError:
    version = '0.0.0'

setup(version=version)
