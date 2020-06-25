# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='ploceus',
    packages=['ploceus'],
    version='0.0.1',
    install_requires=[
        'pycrypto',
        'paramiko>=2.3',
        'PyYAML',
        'Jinja2',
        'terminaltables',
    ],
    entry_points="""
    [console_scripts]
    ploceus=ploceus.cli:main
"""
)
