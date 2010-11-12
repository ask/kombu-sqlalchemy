#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import sys

import sqlakombu

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
src_dir = "sqlakombu"

install_requires = ["sqlalchemy", "kombu"]


def osx_install_data(install_data):

    def finalize_options(self):
        self.set_undefined_options("install", ("install_lib", "install_dir"))
        install_data.finalize_options(self)


def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

SKIP_EXTENSIONS = [".pyc", ".pyo", ".swp", ".swo"]


def is_unwanted_file(filename):
    for skip_ext in SKIP_EXTENSIONS:
        if filename.endswith(skip_ext):
            return True
    return False


for dirpath, dirnames, filenames in os.walk(src_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    for filename in filenames:
        if filename.endswith(".py"):
            packages.append('.'.join(fullsplit(dirpath)))
        elif is_unwanted_file(filename):
            pass
        else:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in
                filenames]])

setup(
    name='kombu-sqlalchemy',
    version=sqlakombu.__version__,
    description=sqlakombu.__doc__,
    author=sqlakombu.__author__,
    author_email=sqlakombu.__contact__,
    url=sqlakombu.__homepage__,
    platforms=["any"],
    license='BSD',
    packages=packages,
    data_files=data_files,
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=codecs.open('README', "r", "utf-8").read(),
)
