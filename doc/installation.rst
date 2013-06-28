Download and Installation
=========================



Installation of stable version Ubuntu
-------------------------------------

1. Download stable version form:  https://dl.dropboxusercontent.com/u/3655123/abce-0.3.tar.gz
2. If pip is not installed in terminal::

    sudo apt-get install python-pip

3. In terminal::

    sudo pip install abce-0.3.1.tar.gz

4. If R has not been installed automatically install it::

    sudo apt-get install R




Installation of stable version Windows
--------------------------------------

1. Install Python2.7 (preferably 32bit)

2. Next, set the system’s PATH variable to include directories
  that include Python components and packages we’ll add later. To do this:
  - Right-click Computer and select Properties.
  - In the dialog box, select Advanced  System Settings.
  - In the next dialog, select Environment Variables.
  - In the User Variables section, edit the PATH statement to include this::

     C:\Python27;C:\Python27\Lib\site-packages\;C:\Python27\Scripts\;


2. Install Setuptools from http://pypi.python.org/pypi/setuptools#downloads
3. install pip::

  easy_install pip

4. Download stable version form:  https://dl.dropboxusercontent.com/u/3655123/abce-0.3.tar.gz
5. install ABCE::

  pip install abce-0.3.1.tar.gz

In case of problems reinstall python
http://www.anthonydebarros.com/2011/10/15/setting-up-python-in-windows-7/

6. Install R form www.cran.org


Installation of development version
-----------------------------------

The installation has two parts. Installing the necessary software packages. Retrieving ABCE with git or as a zip file.

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

Optional for development you can install sphinx and sphinx-apidoc,
the system that created this documentation.  sphinx-apidoc
currently needs the newest version of sphinx.

.. [1] possible you have to install sqlite3 and the according python bindings

.. [2] Git is a a version controll system. It is higly recommended to use it to make your development process more efficient and less error prone. http://gitimmersion.com/
