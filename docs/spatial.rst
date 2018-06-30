
Spatial and Netlogo like Models
===============================

.. figure:: abcEconomicsmesa.gif
   :figwidth:  35 %
   :align: right

abcEconomics deliberately does not provide spatial representation, instead it integrates
with other packages that specialize in spatial representation.


Netlogo like models
-------------------


For Netlogo like models in Python, we recommend using abcEconomics together with
`MESA <http://mesa.readthedocs.io/en/latest/overview.html>`_

A simple example shows how to build a spatial model in abcEconomics using MESA:

`On github <https://github.com/AB-CE/examples>`_

A wrapper file to start the graphical representation and the simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude :: ../examples/mesa_example/start.py
   :language: python

A file with the simulation itself, that can be executed also without the GUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude :: ../examples/mesa_example/model.py
   :language: python

A simple agent
~~~~~~~~~~~~~~

.. literalinclude :: ../examples/mesa_example/moneyagent.py
   :language: python


