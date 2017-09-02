#!/usr/bin/env python
import platform

from distutils.core import setup
from distutils.extension import Extension


cmdclass = {}
ext_modules = []
cpython_specific = []


if platform.python_implementation() != 'PyPy':
    cpython_specific = ['numpy >= 1.10.2p',
                        'pandas >= 0.17.1',
                        'bokeh == 0.12.7']

try:
    from Cython.Distutils import build_ext
    ext_modules += [
        Extension("abce.trade", ["abce/trade.pyx"]),
        Extension("abce.multicurrencytrade",
                  ["abce/multicurrencytrade.pyx"]),
        Extension("abce.online_variance",
                  ["abce/online_variance.pyx"]),
        Extension("abce.online_variance",
                  ["abce/online_variance.pxd"]),
    ]
    cmdclass.update({'build_ext': build_ext})
except ImportError:
    ext_modules += [
        Extension("abce.trade", ["abce/trade.c"]),
        Extension("abce.multicurrencytrade",
                  ["abce/multicurrencytrade.c"]),
        Extension("abce.online_variance",
                  ["abce/online_variance.c"]),
    ]

try:
    setup(name='abce',
          version='0.8.0a14',
          author='Davoud Taghawi-Nejad',
          author_email='Davoud@Taghawi-Nejad.de',
          description='Agent-Based Complete Economy modelling platform',
          url='https://github.com/DavoudTaghawiNejad/abce.git',
          package_dir={'abce': 'abce'},
          packages=['abce', 'abce.agents', 'abce.contracts', 'abce.gui'],
          long_description=open('README.rst').read(),
          install_requires=['networkx >= 1.9.1',
                            'flexx >= 0.4.1',
                            'future',
                            'dataset'] + cpython_specific,
          include_package_data=True,
          ext_modules=ext_modules,
          use_2to3=True,
          cmdclass=cmdclass)
except:
    setup(name='abce',
          version='0.8.0a14',
          author='Davoud Taghawi-Nejad',
          author_email='Davoud@Taghawi-Nejad.de',
          description='Agent-Based Complete Economy modelling platform',
          url='https://github.com/DavoudTaghawiNejad/abce.git',
          package_dir={'abce': 'abce'},
          packages=['abce', 'abce.agents', 'abce.contracts', 'abce.gui'],
          long_description=open('README.rst').read(),
          install_requires=['networkx >= 1.9.1',
                            'flexx >= 0.4.1',
                            'future',
                            'dataset'] + cpython_specific,
          include_package_data=True,
          ext_modules=[],
          use_2to3=True,
          cmdclass={})
