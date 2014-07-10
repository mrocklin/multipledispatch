#!/usr/bin/env python
""" Build and install ``multipledispatch`` with or without Cython or C compiler

Building with Cython must be specified with the "--with-cython" option such as:

    $ python setup.py build_ext --inplace --with-cython

Not using Cython by default makes contributing to ``multipledispatch`` easy,
because Cython and a C compiler are not required for development or usage.

During installation, C extension modules will be automatically built with a
C compiler if possible, but will fail gracefully if there is an error during
compilation.  Use of C extensions significantly improves the performance of
``multipledispatch``, but a pure Python implementation will be used if the
extension modules are unavailable.

"""
import sys
import warnings
from os.path import exists
from setuptools import setup, Extension
from distutils.command.build_ext import build_ext
from distutils.errors import (CCompilerError, DistutilsExecError,
                              DistutilsPlatformError)
import multipledispatch

try:
    from Cython.Build import cythonize
    has_cython = True
except ImportError:
    has_cython = False

use_cython = False
if '--without-cython' in sys.argv:
    sys.argv.remove('--without-cython')

if '--with-cython' in sys.argv:
    use_cython = True
    sys.argv.remove('--with-cython')
    if use_cython and not has_cython:
        raise RuntimeError('ERROR: Cython not found.  Exiting.\n       '
                           'Install Cython or don\'t use "--with-cython"')

suffix = '.pyx' if use_cython else '.c'
ext_modules = []
for modname in ['_dispatcher']:
    ext_modules.append(Extension('multipledispatch.' + modname,
                                 ['multipledispatch/' + modname + suffix]))
if use_cython:
    ext_modules = cythonize(ext_modules)


build_exceptions = (CCompilerError, DistutilsExecError, DistutilsPlatformError,
                    IOError, SystemError)


class build_ext_may_fail(build_ext):
    """ Allow compilation of extensions modules to fail, but warn if they do"""

    warning_message = """
*********************************************************************
WARNING: %s
         could not be compiled.  See the output above for details.

Compiled C extension modules are not required for `multipledispatch`
to run, but they do result in significant speed improvements.
Proceeding to build `multipledispatch` as a pure Python package.

If you are using Linux, you probably need to install GCC or the
Python development package.

Debian and Ubuntu users should issue the following command:

    $ sudo apt-get install build-essential python-dev

RedHat, CentOS, and Fedora users should issue the following command:

    $ sudo yum install gcc python-devel

*********************************************************************
"""

    def run(self):
        try:
            build_ext.run(self)
        except build_exceptions:
            self.warn_failed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except build_exceptions:
            self.warn_failed(name=ext.name)

    def warn_failed(self, name=None):
        if name is None:
            name = 'Extension modules'
        else:
            name = 'The "%s" extension module' % name
        exc = sys.exc_info()[1]
        sys.stdout.write('%s\n' % str(exc))
        warnings.warn(self.warning_message % name)


cmdclass = {} if use_cython else {'build_ext': build_ext_may_fail}

setup(name='multipledispatch',
      version=multipledispatch.__version__,
      description='Multiple dispatch',
      cmdclass=cmdclass,
      ext_modules=ext_modules,
      url='http://github.com/mrocklin/multipledispatch/',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      license='BSD',
      keywords='dispatch',
      packages=['multipledispatch'],
      package_data={'multipledispatch': ['*.pxd', '*.pyx']},
      long_description=(open('README.md').read() if exists('README.md')
                        else ''),
      zip_safe=False)
