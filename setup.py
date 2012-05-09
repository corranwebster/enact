# Copyright (c) 2012 by Enthought, Inc.
# All rights reserved.

from setuptools import setup, find_packages


setup(
    name='enact',
    version='0.1',
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://github.com/enthought/enact',
    description='Animation support for Traits and Chaco',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=('*.tests',)),
    requires=[],
    install_requires=['distribute', 'encore', 'traits', 'chaco'],
)
