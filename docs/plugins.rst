Plugins
=======

ABCE has one plugin so far. The ABCESL accounting framework. If
you want to author your own plugin - its dead simple. All you
have to do is write a class that inherits from Agent in agent.py.
This class can overwrite::

    def __init__(self, id, group, trade_logging, database, random_seed, num_managers,
                 agent_parameters, simulation_parameters, start_round=None):
    def _begin_subround(self):
    def _end_subround(self):
    def _advance_round(self, time):

For example like this::

    class UselessAgent(abce.Agent):
        def __init__(self, id, group, trade_logging,
                     database, random_seed, num_managers, agent_parameters,
                     simulation_parameters, start_round=None):
            super().__init__(id, group, trade_logging,
                             database, random_seed, num_managers, agent_parameters,
                             simulation_parameters, start_round=None):
            print("Here i begin")

        def _begin_subround(self):
            super()._begin_subround()
            print('subround begins')

        def _end_subround(self):
            super()._end_subround()
            print('subround finishes')

        def _advance_round(self, time):
            super()._advance_round(time)
            print('Super I made it to the next round')

        def ability(self):
            print("its %r o'clock" % self.time)
            print("the simulation called my ability")


**Do not overwrite the init(parameters, simulation_parameters)** method
