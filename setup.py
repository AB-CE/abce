#!/usr/bin/env python
try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
import platform


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
if platform.python_implementation() == 'CPython':
    install_requires = ['numpy >= 1.10.2p',
                        'pandas >= 0.17.1',
                        'bokeh == 0.12.7',
                        'networkx >= 1.9.1',
                        'flexx >= 0.4.1',
                        'future',
                        'datase']
else:
    install_requires = [
                        'flexx >= 0.4.1',
                        'future',
                        'dataset']

version = '0.8.1a7'
try:
    setup(name='abce',
          version=version,
          author='Davoud Taghawi-Nejad',
          author_email='Davoud@Taghawi-Nejad.de',
          description='Agent-Based Complete Economy modelling platform',
          url='https://github.com/AB-CE/abce.git',
          package_dir={'abce': 'abce', 'abce.gui': 'abce/gui'},
          packages=['abce'],
          long_description=open('README.rst').read(),
          install_requires=install_requires,
          include_package_data=True,
          ext_modules=ext_modules,
          use_2to3=True,
          cmdclass=cmdclass)
    print("ABCE runs with cython")
except:
    setup(name='abce',
          version=version,
          author='Davoud Taghawi-Nejad',
          author_email='Davoud@Taghawi-Nejad.de',
          description='Agent-Based Complete Economy modelling platform',
          url='https://github.com/AB-CE/abce.git',
          package_dir={'abce': 'abce', 'abce.gui': 'abce/gui'},
          packages=['abce'],
          long_description=open('README.rst').read(),
          install_requires=install_requires,
          include_package_data=True,
          ext_modules=[],
          use_2to3=True,
          cmdclass={})
    print("ABCE RUNS WITHOUT CYTHON, NORMAL ON PYPY")
