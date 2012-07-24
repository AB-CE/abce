Installation
============

The installation has two parts. Installing the necessary software packages. Retrieving ABCE with git or as a zip file.

 In terminal (necessary software) [1]_ ::

  sudo apt-get install python-pyparsing python-numpy python-scipy python-zmq


 Alternative 1 as a zip (EASY):

    1. download the zip file from: https://github.com/DavoudTaghawiNejad/abce
    2. extract zip file

 Alternative 2 via git [2]_ in terminal (RECOMMENDED)::

  [register with git and automatize a secure connection with your computer]
  sudo apt-get install git
  mkdir abce
  cd abce
  git init
  git pull git@github.com:DavoudTaghawiNejad/abce.git

Optional for development you can install sphinx and sphinx-apidoc.  sphinx-apidoc
currently needs the newest version of sphinx, they system that created this documentation

.. [1] possible you have to install sqlite3 and the according python bindings

.. [2] Git is a a version controll system. It is higly recommended to use it to make your development process more efficient and less error prone. http://gitimmersion.com/
