
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import platform


cmdclass = {}

install_requires = ['flexx == 0.4.1',
                    'future',
                    'normality == 0.6.1',
                    'dataset == 0.8']


readthedocs = os.environ.get('READTHEDOCS') == 'True'

if not readthedocs:
    if not platform.python_implementation() == "PyPy":
        install_requires += ['numpy >= 1.10.2p']
        if ('APPVEYOR' not in os.environ) or ('TRAVIS' not in os.environ):
            install_requires += ['pandas >= 0.17.1',
                                 'bokeh == 0.12.16',
                                 'tornado == 4.3']


version = '0.9.7b1'


setup(name='abcEconomics',
      version=version,
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/AB-CE/abce.git',
      package_dir={'abcEconomics': 'abcEconomics',
                   'abcEconomics.gui': 'abcEconomics/gui',
                   'abcEconomics.agents': 'abcEconomics/agents',
                   'abcEconomics.contracts': 'abcEconomics/contracts',
                   'abcEconomics.logger': 'abcEconomics/logger',
                   },
      packages=['abcEconomics'],
      long_description=open('README.rst').read(),
      setup_requires=['setuptools>=18.0', 'cython'],
      install_requires=install_requires,
      include_package_data=True,
      cmdclass=cmdclass)
