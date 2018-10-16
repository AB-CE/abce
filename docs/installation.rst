Download and Installation
=========================

abcEconomics works exclusively with python 3!


Installation Ubuntu
-------------------

1. If python3 and pip not installed in terminal [#fail]_ ::

    sudo apt-get install python3
    sudo apt-get install python3-pip

#. In terminal::

    sudo pip3 install abcEconomics

#. download and unzip the
   `zip file with examples and the template <https://github.com/AB-CE/examples>`_
   from: https://github.com/AB-CE/examples

#. Optional for a 10 fold speed increase:

   Install pypy3 from https://pypy.org/download.html

#. Install pypy3 additionally::

   sudo pypy3 -m pip install abcEconomics

#. For pypy execute models with :code:`pypy3 start.py` instead
   of :code:`python3 start.py`

Installation Mac
----------------

1. If you are on OSX Yosemite, download and install: :code:`Command line Tools (OS X 10.10)
   for XCODE 6.4` from https://developer.apple.com/downloads/


#. If pip not installed in terminal::

      sudo python3 -m easy_install pip

#.  In terminal::

      sudo pip3 install abcEconomics


#. If you are on El Capitain, OSX will ask you to install cc - xcode "Command Line Developer Tools", click accept. [#update]_

#. If XCODE was installed type again in terminal::

    sudo pip3 install abcEconomics

#. download and unzip the
   `zip file with examples and the template <https://github.com/AB-CE/examples>`_
   from: https://github.com/AB-CE/examples

#. Optional for a 10 fold speed increase:

   Install pypy3 from https://pypy.org/download.html

#. Install pypy3 additionally::

   sudo pypy3 -m pip install abcEconomics

#. For pypy execute models with :code:`pypy3 start.py` instead
   of :code:`python3 start.py`


Installation Windows
--------------------

abcEconomics works best with anaconda python 3.5 follow
the instructions blow.


1. Install the **python3.5** anaconda distribution from https://continuum.io/downloads


3. anaconda prompt or in the command line (cmd) type::

    pip install abcEconomics

3. download and unzip the
   `zip file with examples and the template <https://github.com/AB-CE/examples>`_
   from: https://github.com/AB-CE/examples

Known Issues
------------

- When you run an IDE such as spyder sometimes the website blocks. In
order to avoid that, modify the 'Run Setting' and choose
'Execute in external System Terminal'.

- When the simulation blocks, there is probably a simulation.finalize() command
missing after the simulation loop

If you have any problems with the installation
----------------------------------------------
Mail to: DavoudTaghawiNejad@gmail.com

.. [#update] xcode 7 works only on OSX El Capitan. You need to either upgrade or if you want to
            avoid updating download xcode 6.4 from here: https://developer.apple.com/downloads/

.. [#fail] If this fails :code:`sudo apt-add-repository universe` and :code:`sudo apt-get update`



