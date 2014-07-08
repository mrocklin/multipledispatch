#!/usr/bin/env python

from os.path import exists
from setuptools import setup
from setuptools.extension import Extension
import multipledispatch

# XXX Quick hack to add this is.  We will make Cython and C compiler optional
from Cython.Build import cythonize
suffix = '.pyx'
ext_modules = []
for modname in ['_dispatcher']:
    ext_modules.append(Extension('multipledispatch.' + modname,
                                 ['multipledispatch/' + modname + suffix]))
ext_modules = cythonize(ext_modules)


setup(name='multipledispatch',
      version=multipledispatch.__version__,
      description='Multiple dispatch',
      ext_modules=ext_modules,
      url='http://github.com/mrocklin/multipledispatch/',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      license='BSD',
      keywords='dispatch',
      packages=['multipledispatch'],
      long_description=(open('README.md').read() if exists('README.md')
                        else ''),
      zip_safe=False)
