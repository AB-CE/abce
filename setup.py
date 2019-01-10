
import os
try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
try:
    from Cython.Distutils import build_ext
except ImportError:
    from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, \
    DistutilsPlatformError
import platform


class TXEntension(build_ext):
    # This class allows C extension building to fail.
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise Exception("BuildFailed")

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError):
            pass  # raise BuildFailed()


cmdclass = {}
ext_modules = []

install_requires = ['flexx >= 0.4.1',
                    'future',
                    'normality == 0.6.1',
                    'dataset == 0.8']


readthedocs = os.environ.get('READTHEDOCS') == 'True'

if not readthedocs:
    try:
        ext_modules += [
            Extension("abcEconomics.trade", ["abcEconomics/trade.pyx"]),
            Extension("abcEconomics.logger.online_variance", ["abcEconomics/logger/online_variance.pyx"]),
        ]
        cmdclass.update({'build_ext': TXEntension})
    except ImportError:
        ext_modules += [
            Extension("abcEconomics.trade", ["abcEconomics/trade.c"]),
            Extension("abcEconomics.logger.online_variance", ["abcEconomics/logger/online_variance.c"]),
        ]

    if not platform.python_implementation() == "PyPy":
        install_requires += ['numpy >= 1.10.2p']
        if ('APPVEYOR' not in os.environ) or ('TRAVIS' not in os.environ):
            install_requires += ['pandas >= 0.17.1',
                                 'bokeh == 0.12.16',
                                 'tornado == 4.3']


version = '0.9.7b0'


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
      install_requires=install_requires,
      include_package_data=True,
      ext_modules=ext_modules,
      cmdclass=cmdclass)
