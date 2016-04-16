#from distutils.core import setup
#from distutils.extension import Extension
import numpy

from Cython.Distutils import build_ext

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

setup(
  name = 'trade',
  ext_modules=[
    Extension('trade', ['trade.pyx'], include_dirs = [numpy.get_include()])],
  cmdclass = {'build_ext': build_ext}

)
