Installation
============

The installation has three parts. Installing the necessary software packages. Retrieving ABCE. And setting up the database

 In terminal (necessary software)::

  sudo apt-get install python-pyparsing
  sudo apt-get install python-zmq
  sudo apt-get install python-mysqldb
  sudo apt-get install mysql-server
  sudo apt-get install git

 In terminal (retrieving ABCE)::

  mkdir abce
  cd abce
  git init
  git pull git@github.com:DavoudTaghawiNejad/abce.git
  git checkout -b localbranch


Git is a a verioning controll system. It is higly recommended to use it to
make you http://gitimmersion.com/ development process more efficient.

 Optional for development you can install sphinx, they system that created this documentation::

  sudo apt-get install sphinx-common

Database setup
==============

In terminal::

 Creation of the 'abce' user used by the abce-modeling software
 mysql -u root -p
 --your password
 CREATE USER 'abce'@'localhost' IDENTIFIED BY 'ictilo';
 GRANT ALL PRIVILEGES ON *.* TO 'abce'@'localhost' IDENTIFIED BY  'ictilo';
 quit




