#!/usr/bin/env python
import os

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension


cmdclass = {}
ext_modules = []


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
      install_requires=['pygal', 'numpy', 'pandas', 'networkx', 'flask'],
      include_package_data=True,
      ext_modules=ext_modules)

print('** **************************************************************************')
print('**                                                                         **')
print('** - To use ABCE download templates and examples from                      **')
print('**                                                                         **')
print('**    github.com/DavoudTaghawiNejad/abce                                   **')
print('**    or                                                                    **')
print('**    https://github.com/DavoudTaghawiNejad/abce/archive/master.zip        **')
print('**                                                                         **')
print('** - documentation http://davoudtaghawinejad.github.com/abce/              **')
print('**                                                                         **')
print('*****************************************************************************')
if os.name == 'posix':
    try:
        subprocess.call(["tar", "xf abce-0.3.tar.gz"])
    except:
        print('** Please unzip abce-0.3.tar.gz. There you will find examples, templates and documentation')
        print('** - documentation http://davoudtaghawinejad.github.com/abce/')
elif os.name == 'Darwin':
    try:
        subprocess.call(["tar", "xf abce-0.3.tar.gz"])
    except:
        print('** Please unzip abce-0.3.tar.gz. There you will find examples, templates and documentation')
        print('** - documentation http://davoudtaghawinejad.github.com/abce/')
else:
  print('** Please unzip abce-0.3.tar.gz. There you will find examples, templates and documentation')
  print('** - documentation http://davoudtaghawinejad.github.com/abce/')
