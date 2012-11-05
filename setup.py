#!/usr/bin/env python

from distutils.core import setup
import subprocess
setup(name='abce',
      version='0.3',
      description='Agent-Based Complete Economy modelling platform',
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      url='https://github.com/DavoudTaghawiNejad/abce/downloads',
      packages=['lib'],
     )

packs = ['python-pyparsing', 'python-numpy', 'python-scipy', 'python-zmq', 'r-base', 'python-rpy2']

for pack in packs:
    subprocess.call(["apt-get", "install %s" % pack])
