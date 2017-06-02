import os
from setuptools import setup

version = open('VERSION.txt').read()

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
        install_requires=[
            'fs',
            'numpy',
            'modconf==0.3a2',
            'codemach==0.2a1',
            ],
        zip_safe=False,
        )

