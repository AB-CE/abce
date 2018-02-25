
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

install_requires = ['networkx >= 1.9.1',
                    'flexx >= 0.4.1',
                    'future',
                    'dataset == 0.8']


readthedocs = os.environ.get('READTHEDOCS') == 'True'

if not readthedocs:
    try:
        ext_modules += [
            Extension("abce.trade", ["abce/trade.pyx"]),
            Extension("abce.online_variance", ["abce/online_variance.pyx"]),
        ]
        cmdclass.update({'build_ext': TXEntension})
    except ImportError:
        ext_modules += [
            Extension("abce.trade", ["abce/trade.c"]),
            Extension("abce.online_variance", ["abce/online_variance.c"]),
        ]

    if not platform.python_implementation() == "PyPy":
        install_requires += ['numpy >= 1.10.2p',
                             'pandas >= 0.17.1',
                             'bokeh == 0.12.7']


version = '0.9.3b0'


setup(name='abce',
      version=version,
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/AB-CE/abce.git',
      package_dir={'abce': 'abce',
                   'abce.gui': 'abce/gui',
                   'abce.agents': 'abce/agents',
                   'abce.contracts': 'abce/contracts'},
      packages=['abce'],
      long_description=open('README.rst').read(),
      install_requires=install_requires,
      include_package_data=True,
      ext_modules=ext_modules,
      use_2to3=True,
      cmdclass=cmdclass)
