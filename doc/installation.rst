Download and Installation
=========================



Installation of stable version Ubuntu
-------------------------------------

1. download the zip file from: https://github.com/DavoudTaghawiNejad/abce

2. unzip the file

3. If pip or numpy or scipy is not installed in terminal::

    sudo apt-get install python-pip, python-scipy, python-numpy


4. In terminal::

    sudo pip install abce-0.3.1.zip


Installation Mac
----------------

1. download the zip file from: https://github.com/DavoudTaghawiNejad/abce

2. extract zip file

3. make sure python's pip is installed

4. sudo pip install scipy

5. sudo pip install numpy

4 sudo pip install abce-0.3.1.zip

Installation of development version
-----------------------------------

terminal::

  [register with git and automatize a secure connection with your computer]
  sudo apt-get install git
  mkdir abce
  cd abce
  git init
  git pull git@github.com:DavoudTaghawiNejad/abce.git

  proceed is before

Optional for development you can install sphinx and sphinx-apidoc,
the system that created this documentation.  sphinx-apidoc
currently needs the newest version of sphinx.

.. [1] possible you have to install sqlite3 and the according python bindings

.. [2] Git is a a version control system. It is highly recommended to use it to
       make your development process more efficient and less error prone.
       http://gitimmersion.com/
