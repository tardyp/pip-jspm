#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name = "pip-bower",
    version = "0.1",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'bower = pip_bower.main:main',
        ],
    }
 )
