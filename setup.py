#!/usr/bin/env python

from distutils.core import setup
import os

if os.name in ('posix', 'Darwin'):  # unix compatible
    install_requires=['python-dev', 'pyparsing', 'numpy','scipy', 'rpy2', 'pyzmq'],
else:
    install_requires=['pyparsing', 'numpy','scipy', 'rpy2', 'pyzmq'],
    if not(os.name in ('nt')):
        print("Os not recognized, defaulted to tcp (slow) for windows"
        " compatibility. Edit config.py to choose ipc if you use anything but"
        "windows and get this message. Please track the bug on Github.")

setup(
      name='abce-numpydict',
      version='0.3',
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/DavoudTaghawiNejad/abce/downloads',
      package_dir = {'': 'lib', 'abce': 'lib/abce'},
      packages=['abce'],
      modules=['abce_db', 'abcetools', 'postprocess'],
      long_description=open('README.rst').read(),
      install_requires=install_requires,
      data_files=[('', ['lib/postprocess.R'])],
     )

if os.name == 'posix':
    try:
        subprocess.call(["sudo apt-get", "install r-base"])
    except:
        print('** *************************************************************************')
        print('**                                                                        **')
        print('**  please download and install R from http://cran.r-project.org          **')
        print('**                                                                        **')
        print('****************************************************************************')
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
    print('** - please download and install R from http://cran.r-project.org/bin/macosx/     **')
    print('**                                                                                **')
    print('** - documentation http://davoudtaghawinejad.github.com/abce/                     **')
    print('**                                                                                **')
    print('** - please unzip abce-0.X.tar.gz, in there you will find examples and templates  **')
    print('**                                                                                **')
    print('************************************************************************************')
else:
    print('************************************************************************************')
    print('**                                                                                **')
    print('** - pls download and install R from http://cran.r-project.org/bin/windows/base/  **')
    print('**                                                                                **')
    print('** - documentation http://davoudtaghawinejad.github.com/abce/                     **')
    print('**                                                                                **')
    print('** - please unzip abce-0.X.tar.gz, in there you will find examples and templates  **')
    print('**                                                                                **')
    print('************************************************************************************')
