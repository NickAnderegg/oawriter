# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import os.path
import sys

from codecs import open

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(cwd, 'oawriter', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read())

with open('README.md', 'r', encoding='utf-8') as f:
    __readme__ = f.read()

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    __changelog__ = f.read()


setup(
    version      = __version__,

    name         = __title__,
    description  = __description__,
    url          = __url__,

    author       = __author__,
    author_email = __author_email__,

    license      = __license__,

    long_description = __readme__ + '\n\n' + __changelog__,

    packages     = find_packages(),
    #add required packages to install_requires list
    install_requires=[
        "ruamel.yaml"
    ],
    entry_points = {
        "console_scripts": ["oawriter = oawriter:main"]
    },
#list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=(
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only'
    ),
)
