import re
from setuptools import setup

with open('ws_sheets/__init__.py') as f:
    version = re.findall("^__version__ = '(.*)'", f.read())[0]

with open('requirements.txt') as f:
    install_requires=[l.strip() for l in f.readlines()]

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
        install_requires=install_requires,
        zip_safe=False,
        )

