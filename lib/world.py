"""
Using this file is not necessary. However if you want to create special action
groups you can copy this file in your working directory and extent it. If it is
not in your working directory everything will work anyway.


The World class defines special ActionGroups that replace the
('agent_group', 'action') entries in the action_list.

In this example every round first all agents raise there hands, then one
random agent jumps.



ACTIONGROUPS:

For example::

 in start.py:
        ...
        self.action_list = [('agent_group', 'action'), "households_and_firms_simultaneously", "report_in_order"]
        ...

 in world.py:

from worldengine import *


class World(WorldEngine):
    # Calls the ActionGroups in the order specified in self.actionList.
    def __init__(self, parameter_file):
        WorldEngine.__init__(self, parameter_file)

    def households_and_firms_simultaneously(self):
        self.ask_each_agent_in("Firm", "buy")
        self.ask_each_agent_in("Household", "buy")
        # This is simultaneous
        # Firms and Households get the order to buy, after all offers have been
        given.  When they buy, there is no interaction until after they all have
        simultaneously made thir buying decision. Than the trades are cleared.
        No trade prohibits anotherone, as they have all been committed. For
        uncommited quotes the order is randomized, so the execution order has
        no influence.

    def report(self):
        self.ask_agent("agent_0", "report")
        time.sleep(0.1)
        self.ask_agent("agent_1", "report")
        time.sleep(0.1)
        self.ask_agent("agent_2", "report")

Start methods that start are not meant to be in the self.action with an
underscore('_'), this makes the execution faster as the system does not have
to keep track whether this methods are externally called.

ATTENTION::
 if you write mylist = self.agent_list and you change mylist. (for example:
 mylist.remove(3)) self.agent_list will be changed. In order avoid this make
 a copy:
 write mylist = self.agent_list[:]
"""
from worldengine import *


class World(WorldEngine):
    """ Calls the ActionGroups in the order specified in self.actionList.
    """
    def __init__(self, parameter_file):
        WorldEngine.__init__(self, parameter_file)