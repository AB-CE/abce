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
      install_requires=['pyparsing==1.5.7', 'numpy','scipy', 'rpy2', 'pyzmq'],
      include_package_data = True,
     )

if os.name == 'posix':
    print('** **************************************************************************')
    print('**                                                                         **')
    print('** - In the abce-0.X subdirectory you will find  examples ond templates    **')
    print('**                                                                         **')
    print('** - documentation http://davoudtaghawinejad.github.com/abce/              **')
    print('**                                                                         **')
    print('*****************************************************************************')
    try:
        subprocess.call(["tar", "xf abce-0.3.tar.gz"])
    except:
        print('** Please unzip abce-0.3.tar.gz. There you will find examples, templates and documentation')
        print('** - documentation http://davoudtaghawinejad.github.com/abce/')

elif os.name == 'Darwin':
    print('************************************************************************************')
    print('**                                                                                **')
    print('** - documentation http://davoudtaghawinejad.github.com/abce/                     **')
    print('**                                                                                **')
    print('** - please unzip abce-0.X.tar.gz, in there you will find examples and templates  **')
    print('**                                                                                **')
    print('************************************************************************************')
else:
    print('************************************************************************************')
    print('**                                                                                **')
    print('** - documentation http://davoudtaghawinejad.github.com/abce/                     **')
    print('**                                                                                **')
    print('** - please unzip abce-0.X.tar.gz, in there you will find examples and templates  **')
    print('**                                                                                **')
    print('************************************************************************************')
    print('')
    print('os.name: %s' % os.name)
