#!/usr/bin/env python
try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension


cmdclass = {}
ext_modules = []

try:
    from Cython.Distutils import build_ext
    ext_modules += [
        Extension("abce.trade", ["abce/trade.pyx"]),
        Extension("abce.multicurrencytrade", ["abce/multicurrencytrade.pyx"]),
        Extension("abce.online_variance", ["abce/online_variance.pyx"]),
    ]
    cmdclass.update({'build_ext': build_ext})
except ImportError:
    ext_modules += [
        Extension("abce.trade", ["abce/trade.c"]),
        Extension("abce.multicurrencytrade", ["abce/multicurrencytrade.c"]),
        Extension("abce.online_variance", ["abce/online_variance.c"]),
    ]


setup(name='abce',
      version='0.6.0a0',
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/DavoudTaghawiNejad/abce.git',
      package_dir={'abce': 'abce'},
      packages=['abce'],
      long_description=open('README.rst').read(),
      install_requires=['numpy >= 1.10.2p',
                        'pandas >= 0.17.1',
                        'networkx >= 1.9.1',
                        'flask >= 0.10.1',
                        'bokeh < 0.12.0',
                        'future'],
      include_package_data=True,
      ext_modules=ext_modules,
      use_2to3=True,
      cmdclass=cmdclass)
