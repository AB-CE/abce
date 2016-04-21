Download and Installation
=========================



Installation of stable version Ubuntu
-------------------------------------

1. download the zip file from: https://github.com/DavoudTaghawiNejad/abce

2. unzip the file and change in the directory

3. If pip or numpy or scipy is not installed in terminal::

    sudo apt-get install python-pip, python-scipy, python-numpy

    sudo apt-get install python-setuptools python-dev build-essential

4. In terminal::

    sudo python setup.py install


Installation Mac
----------------

1. download the zip file from: https://github.com/DavoudTaghawiNejad/abce

2. extract zip file and change in the directory

3. make sure python's pip is installed

4.  In terminal::

        sudo pip install scipy

        sudo pip install numpy

        sudo python setup.py install

5. If OSX asks you to install cc - xcode "Command Line Developer Tools", click accept

6. If XCODE is installed type again in terminal::

       sudo python setup.py install


Installation Windows
--------------------

- windows currently is under development and not fully tested

1. Install the **python2.7** anaconda distribution from https://continuum.io/downloads
   (You can also install python and numpy/scipy by hand)

2. Install Visual C++ for python 2.7 from here: https://www.microsoft.com/en-us/download/details.aspx?id=44266
   (for speed much some of background things are written in C)

3. download the zip file from: https://github.com/DavoudTaghawiNejad/abce

4. extract zip file and change in the directory

5. In anachonda prompt or command line, if the path to python is set::

    python setup.py install

When you run an IDE such as spyder sometimes the website blocks. In
order to avoid that, modify the 'Run Setting' and choose
'Execute in external System Terminal'.

Installation of development version
-----------------------------------


terminal::

  git pull git@github.com:DavoudTaghawiNejad/abce.git

Optional for development you can install sphinx and sphinx-apidoc,
the system that created this documentation.  sphinx-apidoc
currently needs the newest version of sphinx.

.. [1] possible you have to install sqlite3 and the according python bindings

.. [2] Git is a a version control system. It is highly recommended to use it to
       make your development process more efficient and less error prone.
       http://gitimmersion.com/
