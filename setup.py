#!/usr/bin/env python
import os

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension


cmdclass = { }
ext_modules = [ ]

try:
    from Cython.Distutils import build_ext
    ext_modules += [
        Extension("abce.trade", [ "abce/trade.pyx" ]),
    ]
    cmdclass.update({ 'build_ext': build_ext })
except ImportError:
    ext_modules += [
        Extension("abce.trade", [ "abce/trade.c" ]),
    ]






setup(name='abce',
      version='0.5b',
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/DavoudTaghawiNejad/abce.git',
      package_dir={'abce': 'abce'},
      packages=['abce'],
      long_description=open('README.rst').read(),
      install_requires=['numpy', 'pandas', 'networkx', 'flask', 'bokeh', 'matplotlib'],
      include_package_data=True,
      ext_modules=ext_modules,
      cmdclass=cmdclass)


