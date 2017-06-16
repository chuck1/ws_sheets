import re
from setuptools import setup

with open('ws_sheets/__init__.py') as f:
    version = re.findall("^__version__ = '(.*)'", f.read())[0]

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
        )

