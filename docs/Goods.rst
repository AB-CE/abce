Physical goods and services
===========================

Goods
-----

An agent can access a good with :code:`self['cookies']` or
:code:`self['money']`.

- :code:`self.create(money, 15)` creates money
- :code:`self.destroy(money, 10)` destroys money
- goods can be given, taken, sold and bought
- :code:`self['money']` returns the quantity an agent possesses

Services
--------

Services are like goods, but the need to be declared as services
in the simulation :func:`abcEconomics.__init__.service`.
In this function one declares a good that creates the other good and
how much. For example if one has :code:`self['adults'] = 2`, one could
get 16 hours of labor every day. :code:`simulation.declare_service('adults', 8, 'labor')`.


.. default-domain::abcEconomics.Goods

.. automodule:: abcEconomics.goods

.. autoclass:: abcEconomics.goods.Goods
    :members:
    :undoc-members:
    :show-inheritance:
