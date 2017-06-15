import os
from setuptools import setup

version = open('VERSION.txt').read()

with open('requirements.txt') as f:
    req = [s.strip() for s in f.readlines()]

setup(name='ws_sheets',
        version=version,
        description='python spreadsheets',
        url='http://github.com/chuck1/ws_sheets',
        author='Charles Rymal',
        author_email='charlesrymal@gmail.com',
        license='MIT',
        packages=[
            'ws_sheets',
            'ws_sheets.tests',
            'ws_sheets.tests.conf',
            'ws_sheets.ext.middleware',
            ],
        zip_safe=False,
        install_requires=req,
        )

