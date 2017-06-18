Download and Installation
=========================



Installation Ubuntu
-------------------

1. If pip not installed in terminal [#fail]_ ::

    
    sudo apt-get install python-pip python-dev python-pandas python-setuptools
    sudo pip install --upgrade numpy

#. In terminal::

    sudo pip install -i https://testpypi.python.org/pypi --extra-index-url https://pypi.python.org/pypi abce


Installation Mac
----------------

1. If you are on OSX Yosemite, download and install: :code:`Command line Tools (OS X 10.10)
   for XCODE 6.4` from https://developer.apple.com/downloads/



#. If pip not installed in terminal::

      sudo easy_install pip

#.  In terminal::

      sudo pip install -i https://testpypi.python.org/pypi --extra-index-url https://pypi.python.org/pypi abce


#. If you are on El Capitain, OSX will ask you to install cc - xcode "Command Line Developer Tools", click accept. [#update]_

#. If XCODE was installed type again in terminal::

    sudo pip install -i https://testpypi.python.org/pypi --extra-index-url https://pypi.python.org/pypi abce

#. download and unzip the
   `zip file with examples and the template <https://github.com/DavoudTaghawiNejad/abce/archive/master.zip>`_
   from: https://github.com/DavoudTaghawiNejad/abce



Installation Windows
--------------------

ABCE works with python 2.7, if you are using already anachonda python 3.5 follow
the instructions blow.


1. Install the **python2.7** anaconda distribution from https://continuum.io/downloads
   (Any other python 2.7 with numpy will also work)

2. Install Visual C++ for python 2.7 from here: https://www.microsoft.com/en-us/download/details.aspx?id=44266
   (for speed much a part of ABCE are written in C/Cython)

3. anaconda prompt or in the command line (cmd) type::

    pip install -i https://testpypi.python.org/pypi --extra-index-url https://pypi.python.org/pypi abce

3. download and unzip the
   `zip file with examples and the template <https://github.com/DavoudTaghawiNejad/abce/archive/master.zip>`_
   from: https://github.com/DavoudTaghawiNejad/abce



**When you run an IDE such as spyder sometimes the website blocks. In
order to avoid that, modify the 'Run Setting' and choose
'Execute in external System Terminal'.**

Installation Anaconda 3.5
--------------------------

If you have already Anaconda 3.5 installed:

1. anaconda prompt or in the command line (cmd) type::

    conda create -n py27 python=2.7 anaconda

#. close your anaconda prompt / command line and open a new one

#. Type::

    activate py27

You can now switch between python 2.7 and python 3.5.
To deactivate python2.7 :code:`deactivate` [#source]_

#. follow the windows installation instructions

#. In your IDE, choose the python2.7 environment py27

If you have any problems with the installation
----------------------------------------------
Mail to: DavoudTaghawiNejad@gmail.com

.. [#update] xcode 7 works only on OSX El Capitan. You need to either upgrade or if you want to
            avoid updating download xcode 6.4 from here: https://developer.apple.com/downloads/

.. [#source] sometimes :code:`source activate py27` and :code:`source deactivate` worksx

.. [#fail] If this fails :code:`sudo apt-add-repository universe` and :code:`sudo apt-get update`



