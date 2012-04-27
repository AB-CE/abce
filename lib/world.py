"""
Using this file is not necessary. However if you want to create special action
groups you can copy this file in your working directory and extent it. If it is
not in your working directory everything will work anyway.


The World class defines special ActionGroups that replace the
('which_agent', 'does_what') entries in the action_list.

In this example every round first all agents raise there hands, then one
random agent jumps.


ACTIONLIST:

self.actionList, is the sequence in which the actions are executed each
round. It must be a list contain a string. The names must be the same as
in the "def" function in this class below. self.actionList must be declared
in the "def __init__(...):".
the indentation must by two tabs (or 8 spaces).

For example::

        self.actionList = [('which_agent', 'does_what'),
                "raise_hands", "one_agent_jumps"].


ACTIONGROUPS:

For example::

from worldengine import *


class World(WorldEngine):
    # Calls the ActionGroups in the order specified in self.actionList.
    def __init__(self, parameter_file):
        WorldEngine.__init__(self, parameter_file)
        self.action_list = ["give", "get", "report"]

    def give(self):
        self.ask_each_agent_in("agent", "give")

    def get(self):
        self.ask_each_agent_in("agent", "get")

    def report(self):
        self.ask_agent("agent_0", "report")
        time.sleep(0.1)
        self.ask_agent("agent_1", "report")
        time.sleep(0.1)
        self.ask_agent("agent_2", "report")

Start methods that start are not meant to be in the self.action with an
underscore('_'), this makes the execution faster as the system does not have
to keep track whether this methods are externally called.

ATTENTION:
 if you write mylist = self.agent_list and you change mylist. (for example:
 mylist.remove(3)) self agent_list will be changed. In order avoid this make
 a copy:
 write mylist = self.agent_list[:]
"""
from worldengine import *


class World(WorldEngine):
    """ Calls the ActionGroups in the order specified in self.actionList.
    """
    def __init__(self, parameter_file):
        WorldEngine.__init__(self, parameter_file)