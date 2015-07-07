#!/usr/bin/env python

from setuptools import setup
import os

# MUST ASSERT THAT python-dev is installed

setup(
      name='abce',
      version='0.3',
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/DavoudTaghawiNejad/abce/downloads',
      package_dir = {'abce': 'abce'},
      packages=['abce'],
      modules=['abce_db', 'abcetools', 'postprocess'],
      long_description=open('README.rst').read(),
      install_requires=['pyparsing==1.5.7', 'numpy','scipy', 'dataset', 'pandas'],
      include_package_data = True,
     )

print('** **************************************************************************')
print('**                                                                         **')
print('** - In the abce-0.X subdirectory you will find  examples ond templates    **')
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
