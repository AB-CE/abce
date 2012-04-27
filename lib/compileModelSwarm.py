# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
  name = 'Name',
  ext_modules=[
    Extension('ModelSwarm', ['ModelSwarm.pyx'])
    ],
  cmdclass = {'build_ext': build_ext}
)
