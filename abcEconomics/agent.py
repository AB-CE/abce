# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# abcEconomics is open-source software. If you are using abcEconomics for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""
The :py:class:`abcEconomics.Agent` class is the basic class for creating your agents.
It automatically handles the possession of goods of an agent. In order to
produce/transforme goods you also need to subclass the :py:class:`abcEconomics.Firm` or
to create a consumer the :py:class:`abcEconomics.Household`.

For detailed documentation on:

Trading, see :doc:`Trade`

Logging and data creation, see :doc:`Database`.

Messaging between agents, see :doc:`Messenger`.
"""
from .logger import Logger
from .agents.trader import Trader
from .agents.messenger import Messenger
from .agents.goods import Goods


class Agent(Logger, Trader, Messenger, Goods):
    """ Every agent has to inherit this class. It connects the agent to the
    simulation and to other agent. The :class:`abcEconomics.Trade`,
    :class:`abcEconomics.Logger` and :class:`abcEconomics.Messenger` classes are included.
    An agent can also inheriting from :class:`abcEconomics.Firm`,
    :class:`abcEconomics.FirmMultiTechnologies` or :class:`abcEconomics.Household` classes.

    Every method can return parameters to the simulation.

    For example::

        class Household(abcEconomics.Agent, abcEconomics.Household):
            def init(self, simulation_parameters, agent_parameters):
                self.num_firms = simulation_parameters['num_firms']
                self.type = agent_parameters['type']
                ...

            def selling(self):
                for i in range(self.num_firms):
                    self.sell('firm', i, 'good', quantity=1, price=1)

            ...
            def return_quantity_of_good(self):
                return['good']


        ...

        simulation = Simulation()
        households = Simulation.build_agents(household, 'household',
                                             parameters={...},
                                             agent_parameters=[{'type': 'a'},
                                                               {'type': 'b'}])
        for r in range(10):
            simulation.advance_round(r)
            households.selling()
            print(households.return_quantity_of_good())



    """

    def __init__(self, id, agent_parameters, simulation_parameters, name=None):
        """ Do not overwrite __init__ instead use a method called init instead.
        init is called whenever the agent are build.
        """
        super(Agent, self).__init__(id, agent_parameters, simulation_parameters)
        """ self.id returns the agents id READ ONLY"""
        # unpacking simulation_parameters
        group = simulation_parameters['group']
        start_round = simulation_parameters.get('start_round', None)

        if name is None:
            name = (group, id)
        self.name = name
        # name_without_colon is used for logging purpose
        self.name_without_colon = '%s_%i' % (group, id)
        self.id = id
        """ self.name returns the agents name, which is the group name and the
        id
        """
        self.group = group
        """ self.group returns the agents group or type READ ONLY! """
        # TODO should be group_address(group), but it would not work
        # when fired manual + ':' and manual group_address need to be removed

        self.time = start_round
        """ self.time, contains the time set with simulation.advance_round(time)
            you can set time to anything you want an integer or
            (12, 30, 21, 09, 1979) or 'monday' """

    def init(self):
        """ This method is called when the agents are build.
        It can be overwritten by the user, to initialize the agents.
        Parameters are the parameters given to
        :py:meth:`abcEconomics.Simulation.build_agents`.

        Example::

            class Student(abcEconomics.Agent):
                def init(self, rounds, age, lazy, school_size):
                    self.rounds = rounds
                    self.age = age
                    self.lazy = lazy
                    self.school_size = school_size

                def say(self):
                    print('I am', self.age ' years old and go to a school
                    that is ', self.school_size')


            def main():
                sim = Simulation()
                students = sim.build_agents(Student, 'student',
                                            agent_parameters=[{'age': 12, lazy: True},
                                                              {'age': 12, lazy: True},
                                                              {'age': 13, lazy: False},
                                                              {'age': 14, lazy: True}],
                                            rounds=50,
                                            school_size=990)

        """
        print("Warning: agent %s has no init function" % self.group)

    def _advance_round(self, time, str_time):
        super()._advance_round(time)
        self._str_round = str_time
        self.time = time

        if self.conditional_logging:
            if self.time in self.log_rounds:
                self.log_this_round = True
            else:
                self.log_this_round = False

    def _execute(self, command, args, kwargs):
        self._do_message_clearing()
        self._begin_subround()
        ret = getattr(self, command)(*args, **kwargs)
        self._end_subround()
        self._reject_polled_but_not_accepted_offers()
        return ret

    def _begin_subround(self):
        """ Overwrite this to make abcEconomics plugins, that need to do
        something at the beginning of every subround """
        pass

    def _end_subround(self):
        """ Overwrite this to make abcEconomics plugins, that need to do
        something at the beginning of every subround """
        pass
