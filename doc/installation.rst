Installation
============

The installation has two parts. Installing the necessary software packages. Retrieving ABCE with git or as a zip file.

 In terminal (necessary software)::

  sudo apt-get install python-pyparsing
  sudo apt-get install python-zmq
  sudo apt-get install git
  [possible sqlite3 and the according python bindings, depends on your system]

 Alternative 1 as a zip (EASY)::

    download the zip file from: https://github.com/DavoudTaghawiNejad/abce
    extract zip file

 Alternative 2 via git [1] in terminal (RECOMMENDED)::

  [register with git and automatize a secure connection with your computer]
  mkdir abce
  cd abce
  git init
  git pull git@github.com:DavoudTaghawiNejad/abce.git

Optional for development you can install sphinx and sphinx-apidoc.  sphinx-apidoc 
currently needs the newest version of sphinx, they system that created this documentation

.. [1] Git is a a version controll system. It is higly recommended to use it to
make you http://gitimmersion.com/ development process more efficient.