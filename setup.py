#!/usr/bin/env python

from os.path import exists
from setuptools import setup

setup(name='multipledispatch',
      version='0.6.0',
      description='Multiple dispatch',
      url='http://github.com/mrocklin/multipledispatch/',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      install_requires=['six'],
      license='BSD',
      keywords='dispatch',
      packages=['multipledispatch'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      zip_safe=False)
